# backend/main.py
import os, subprocess, traceback, threading, time, glob
from pathlib import Path
from datetime import datetime
from typing import Optional, Iterable, List, Dict, Union , Tuple
from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fnmatch import fnmatch
import glob, shutil, subprocess
from errno import errorcode
import json
import backend.main as m
p = Path(m.__file__).resolve()
project_dir = p.parent.parent
print("backend/main.py:", p)
print("project_dir:", project_dir)
print("mainwindow.py exists?", (project_dir/"mainwindow.py").exists())
print("UI file exists?", (project_dir/"UI_Design"/"greyform_sweefeng.ui").exists())
print("Checklist exists?", (project_dir/"Greyform TERRAHL2(JMB)-T1a BOM Checklist 20231211.xlsx").exists())
print("Output xlsx exists?", (project_dir/"PBU_TERRAHL2(final).xlsx").exists())
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

PIDFILE = Path("/tmp/greyform_ui.pid")
LOCKFILE = Path("/tmp/greyform_ui.lock")
LOGFILE = Path("/tmp/greyform_ui.log")

WANTED_EXTS = {".ifc", ".ifczip", ".step", ".stp", ".csv", ".xlsx", ".xls"}
IFC_EXTS = {".ifc", ".ifczip", ".ifcxml"}
MEDIA_ROOTS = [Path("/media"), Path("/run/media")]
CACHE_FILE = Path("/tmp/ifc_cache.json")
IFC_CACHE: Dict[str, Dict[str, float]] = {}

# Small cache for detect_usb (avoid repeated /proc/mounts + FS hits)
_CACHE = {"ts": 0.0, "preferred": None, "choices": []}
_CACHE_TTL = 5.0  # seconds


def _cache_load():
    global IFC_CACHE
    try:
        if CACHE_FILE.exists():
            IFC_CACHE = json.loads(CACHE_FILE.read_text())
    except Exception:
        IFC_CACHE = {}

def _cache_save():
    try:
        CACHE_FILE.write_text(json.dumps(IFC_CACHE))
    except Exception:
        pass

_cache_load()

def _which_find() -> str:
    return "/usr/bin/find" if Path("/usr/bin/find").exists() else (shutil.which("find") or "find")

def _expand_roots(root: Optional[str]) -> List[Path]:
    if not root:
        return []
    if any(ch in root for ch in "*?[]"):
        return [Path(p) for p in glob.glob(root) if Path(p).is_dir()]
    return [Path(root)]

def _newest_ifc_with_find(root: Path, max_depth: int, timeout_ms: int) -> Optional[Tuple[float, str]]:
    """Return (mtime, path) of newest IFC under root using 'find', or None."""
    if not root.exists() or not root.is_dir():
        return None
    find_bin = _which_find()

    # Try with -printf (GNU find); prefer .ifc newer first
    cmd = [
        find_bin, str(root),
        "-maxdepth", str(max_depth),
        "-type", "f",
        "(",
            "-iname", "*.ifc", "-o",
            "-iname", "*.ifczip", "-o",
            "-iname", "*.ifcxml",
        ")",
        "-printf", "%T@ %p\n",
    ]
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=timeout_ms/1000.0, check=False)
        out = cp.stdout.strip()
        if out:
            lines = out.splitlines()
            # newest first
            lines.sort(key=lambda s: float(s.split(" ", 1)[0]), reverse=True)
            # prefer .ifc over others at the same mtime
            def key(line):
                ts, p = line.split(" ", 1)
                return (float(ts), p.lower().endswith(".ifc"))
            # pick first where extension preference is also applied
            best = max(lines, key=lambda ln: (float(ln.split(" ",1)[0]),
                                              ln.split(" ",1)[1].lower().endswith(".ifc")))
            ts, path = best.split(" ", 1)
            return (float(ts), path)
    except Exception:
        pass

    # Busybox/find without -printf — fall back and just take the first hit
    try:
        cmd2 = [find_bin, str(root), "-maxdepth", str(max_depth), "-type", "f",
                "(", "-iname", "*.ifc", "-o", "-iname", "*.ifczip", "-o", "-iname", "*.ifcxml", ")"]
        cp2 = subprocess.run(cmd2, capture_output=True, text=True,
                             timeout=timeout_ms/1000.0, check=False)
        out2 = [p for p in cp2.stdout.strip().splitlines() if p]
        if out2:
            # stat to get mtime so we can compare across roots
            try:
                st = Path(out2[0]).stat()
                return (st.st_mtime, out2[0])
            except Exception:
                return (0.0, out2[0])
    except Exception:
        pass

    return None

@app.get("/api/whoami")
def whoami():
    uid = os.geteuid()
    gid = os.getegid()
    def name_or(id_, fn, fallback):
        try:
            return fn(id_).pw_name if fn is pwd.getpwuid else fn(id_).gr_name
        except Exception:
            return fallback
    return {
        "uid": uid,
        "gid": gid,
        "user": name_or(uid, pwd.getpwuid, f"uid:{uid}"),
        "group": name_or(gid, grp.getgrgid, f"gid:{gid}"),
        "cwd": os.getcwd(),
        "can_read_media": os.access("/media", os.R_OK | os.X_OK),
        "can_x_ubuntu": os.access("/media/ubuntu", os.X_OK),  # traverse
    }

@app.get("/api/ifc_probe")
def ifc_probe(path: str = Query(..., description="Absolute path to IFC")):
    p = Path(path)
    if not p.exists() or not p.is_file():
        return {"ok": False, "reason": "not-found-or-not-file", "path": str(p)}
    try:
        st = p.stat()
        with p.open("rb") as f:
            head = f.read(256)
        kind = "zip" if head.startswith(b"PK\x03\x04") else "ifc-or-ifcxml"
        preview = head[:80].decode("ascii", "ignore")
        return {"ok": True, "path": str(p), "size": st.st_size, "kind": kind, "preview": preview}
    except Exception as e:
        import traceback, os
        # include errno and traceback for clarity
        eno = getattr(e, "errno", None)
        return {
            "ok": False,
            "reason": f"{type(e).__name__}",
            "errno": eno,
            "errno_name": errorcode.get(eno, None) if eno is not None else None,
            "trace": traceback.format_exc().splitlines()[-1],
            "path": str(p),
        }

@app.get("/api/find_ifc_quick")
def find_ifc_quick(root: str = Query(..., description="USB mount root")):
    r = Path(root)
    if not r.exists() or not r.is_dir():
        return {"ok": False, "reason": "root-not-dir", "match": None}

    # 0) cache first
    got = IFC_CACHE.get(str(r))
    if got:
        p = Path(got.get("path", ""))
        try:
            st = p.stat()
            if p.is_file():
                return {"ok": True, "match": str(p), "cached": True}
        except Exception:
            pass  # fallthrough if stale

    def scan_dir_once(d: Path) -> Optional[str]:
        try:
            with os.scandir(d) as it:
                for e in it:
                    if e.is_file():
                        n = e.name.lower()
                        if n.endswith(".ifc") or n.endswith(".ifczip") or n.endswith(".ifcxml"):
                            return str(Path(e.path))
        except Exception:
            pass
        return None

    # level 0: root
    m = scan_dir_once(r)
    if m:
        IFC_CACHE[str(r)] = {"path": m, "mtime": Path(m).stat().st_mtime}
        _cache_save()
        return {"ok": True, "match": m, "cached": False}

    # level 1: each immediate subdir (non-recursive)
    lvl1: list[Path] = []
    try:
        with os.scandir(r) as it:
            for e in it:
                if e.is_dir(follow_symlinks=False):
                    lvl1.append(Path(e.path))
    except Exception:
        pass

    # quick preferred names first (still level 1)
    PREFERRED = {"ifc", "IFC", "models", "model", "bim", "BIM", "export", "exports"}
    for d in lvl1:
        if d.name in PREFERRED:
            m = scan_dir_once(d)
            if m:
                IFC_CACHE[str(r)] = {"path": m, "mtime": Path(m).stat().st_mtime}
                _cache_save()
                return {"ok": True, "match": m, "cached": False}

    # level 2: each subdir of level-1 dirs (non-recursive)
    for d in lvl1:
        try:
            with os.scandir(d) as it:
                for f in it:
                    if f.is_dir(follow_symlinks=False):
                        m = scan_dir_once(Path(f.path))
                        if m:
                            IFC_CACHE[str(r)] = {"path": m, "mtime": Path(m).stat().st_mtime}
                            _cache_save()
                            return {"ok": True, "match": m, "cached": False}
        except Exception:
            continue

    return {"ok": False, "reason": "no-quick-hit", "match": None}


def _which_find() -> str:
    return "/usr/bin/find" if Path("/usr/bin/find").exists() else (shutil.which("find") or "find")

@app.get("/api/find_ifc_fast")
def find_ifc_fast(
    root: Optional[str] = Query(None, description="Optional mount or wildcard, e.g. /media/*/*"),
    max_depth: int = Query(3, ge=0, le=20),
    timeout_ms: int = Query(1200, ge=100, le=10000),
):
    # expand candidates
    candidates: List[Path] = []
    if root:
        if any(ch in root for ch in "*?[]"):
            candidates = [Path(p) for p in glob.glob(root) if Path(p).is_dir()]
        else:
            candidates = [Path(root)]
    if not candidates:
        mounts = _iter_mounts_under_media() or MEDIA_ROOTS
        candidates = [m for m in mounts if m.exists() and m.is_dir()]

    best: Optional[Tuple[float, str]] = None
    per_root_timeout = max(200, int(timeout_ms / max(1, min(len(candidates), 4))))
    find_bin = _which_find()

    for r in candidates:
        # cache first
        got = IFC_CACHE.get(str(r))
        if got:
            p = Path(got.get("path", ""))
            try:
                st = p.stat()
                if p.is_file():
                    return {"ok": True, "match": str(p), "cached": True}
            except Exception:
                pass

        # fast path via GNU find
        cmd = [
            find_bin, str(r), "-maxdepth", str(max_depth),
            "-type", "f",
            "(", "-iname", "*.ifc", "-o", "-iname", "*.ifczip", "-o", "-iname", "*.ifcxml", ")",
            "-printf", "%T@ %p\n",
        ]
        try:
            cp = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=per_root_timeout/1000.0, check=False)
            out = cp.stdout.strip()
            if out:
                lines = out.splitlines()
                # newest first, prefer .ifc
                lines.sort(key=lambda s: (float(s.split(" ",1)[0]), s.split(" ",1)[1].lower().endswith(".ifc")), reverse=True)
                ts, path = lines[0].split(" ", 1)
                IFC_CACHE[str(r)] = {"path": path, "mtime": float(ts)}
                _cache_save()
                return {"ok": True, "match": path, "cached": False}
        except Exception:
            pass

        # fallback without -printf
        try:
            cmd2 = [find_bin, str(r), "-maxdepth", str(max_depth), "-type", "f",
                    "(", "-iname", "*.ifc", "-o", "-iname", "*.ifczip", "-o", "-iname", "*.ifcxml", ")"]
            cp2 = subprocess.run(cmd2, capture_output=True, text=True,
                                 timeout=per_root_timeout/1000.0, check=False)
            out2 = [p for p in cp2.stdout.strip().splitlines() if p]
            if out2:
                sel = out2[0]
                try:
                    st = Path(sel).stat()
                    ts = st.st_mtime
                except Exception:
                    ts = 0.0
                IFC_CACHE[str(r)] = {"path": sel, "mtime": ts}
                _cache_save()
                return {"ok": True, "match": sel, "cached": False}
        except Exception:
            pass

    return {"ok": False, "reason": "no-match", "match": None}


def _is_under_media(p: Path) -> bool:
    ps = str(p)
    return any(ps == str(r) or ps.startswith(str(r) + "/") for r in MEDIA_ROOTS)

def _iter_mounts_under_media() -> List[Path]:
    out: List[Path] = []
    try:
        with open("/proc/mounts", "r") as f:
            for ln in f:
                parts = ln.split()
                if len(parts) >= 2:
                    mnt = Path(parts[1])
                    if _is_under_media(mnt):
                        out.append(mnt)
    except Exception:
        pass
    # de-dup preserving order
    seen, uniq = set(), []
    for p in out:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp not in seen:
            uniq.append(rp); seen.add(rp)
    return uniq

def _expand_path(path: Optional[str]) -> List[Path]:
    if not path:
        return []
    # allow wildcards like /media/*/* for username-agnostic hints
    if any(ch in path for ch in "*?[]"):
        return [Path(p) for p in glob.glob(path)]
    return [Path(path)]

def _cheap_list(d: Path, exts: List[str], limit: int = 200) -> List[str]:
    """Non-recursive, capped directory listing for speed."""
    out: List[str] = []
    try:
        with os.scandir(d) as it:
            for i, e in enumerate(it):
                if i >= limit:
                    break
                if e.is_file():
                    nm = e.name
                    if not exts or any(nm.lower().endswith(x) for x in exts):
                        out.append(nm)
    except Exception:
        pass
    return out


# -------------------------
# Fast USB detection
# -------------------------

def _has_entries(d: Path, limit: int = 1) -> bool:
    try:
        with os.scandir(d) as it:
            for i, _ in enumerate(it):
                return True if i >= 0 else False
    except Exception:
        return False
    return False

@app.get("/api/detect_usb")
def detect_usb(
    path: Optional[str] = Query(None, description="Optional hint; can include wildcards like /media/*/*"),
    scan_media: bool = Query(True, description="Scan /media and /run/media using mount table"),
    need_files: bool = Query(False, description="If true, include a cheap (non-recursive) file list"),
):
    now = time.monotonic()
    if (now - _CACHE["ts"]) < _CACHE_TTL and _CACHE["preferred"]:
        return {"found": True, "preferred": _CACHE["preferred"], "choices": _CACHE["choices"], "checked": [], "cached": True}

    checked: List[Dict] = []
    choices: List[Dict] = []

    # try user hint first
    roots = _expand_path(path)

    # if scanning media, add common patterns even if not mountpoints
    if scan_media:
        roots += [Path("/media"), Path("/run/media")]
        # also add username/label depth patterns so we don't rely on ismount()
        roots += [Path(p) for p in glob.glob("/media/*/*")] + [Path(p) for p in glob.glob("/run/media/*/*")]

    seen = set()
    for d in roots:
        try:
            rp = d.resolve()
        except Exception:
            continue
        if rp in seen or not rp.exists() or not rp.is_dir():
            continue
        seen.add(rp)

        files = [] if not need_files else _cheap_list(rp, exts=[], limit=200)
        has_any = _has_entries(rp, limit=1)      # <-- NEW: cheap non-recursive presence check
        ismnt   = os.path.ismount(rp)

        info = {
            "path": str(rp),
            "exists": True,
            "valid": bool(files) or ismnt or has_any,   # <-- accept non-mount dirs that have entries
            "files": files,
            "ismount": ismnt,
            "has_entries": has_any,                     # (useful in UI when debugging)
        }
        checked.append(info)
        if info["valid"]:
            choices.append({"path": info["path"], "files": info["files"]})
            # pick the first non-empty / likely USB dir
            _CACHE.update(ts=now, preferred=info["path"], choices=choices)
            return {"found": True, "preferred": info["path"], "choices": choices, "checked": checked, "cached": False}

    return {"found": False, "preferred": None, "choices": choices, "checked": checked, "cached": False}


# -------------------------
# Optional: focused folder scan for IFC
# -------------------------

IGNORE_DIRS = {"node_modules", ".git", "__pycache__", "System Volume Information", "$RECYCLE.BIN"}

def _iter_files(root: Path, max_depth: int = 3):
    root = root.resolve()
    root_depth = len(root.parts)
    for p in root.rglob("*"):
        try:
            if p.is_file():
                depth = len(p.resolve().parts) - root_depth
                if depth <= max_depth:
                    yield p
        except Exception:
            continue

def _root_ok(root: Path) -> Dict:
    if not root.exists() or not root.is_dir():
        return {"exists": False, "valid": False, "files": []}
    files = [
        p.name
        for p in _iter_files(root, max_depth=3)
        if p.suffix.lower() in WANTED_EXTS
    ]
    return {"exists": True, "valid": len(files) > 0, "files": files[:50]}

def pick_ifc(root: Path, recursive: bool = True, max_depth: int = 8) -> Optional[Path]:
    if not root.exists() or not root.is_dir():
        return None
    candidates = []
    for p in _iter_files(root, max_depth=max_depth):
        if p.suffix.lower() in IFC_EXTS:
            try:
                st = p.stat()
                candidates.append((p, st.st_mtime))
            except Exception:
                pass
    if not candidates:
        return None
    # Prefer .ifc over others; latest mtime first
    candidates.sort(key=lambda t: (t[0].suffix.lower() != ".ifc", -t[1]))
    return candidates[0][0]

@app.get("/api/scan_folder")
def scan_folder(
    path: str = Query(..., description="Absolute folder path (e.g., /media/ubuntu/079B-BD5C)"),
    recursive: bool = Query(True),
    max_depth: int = Query(2, ge=0, le=16),
    timeout_ms: int = Query(1500),
    max_hits: int = Query(10, ge=1, le=100),
):
    """
    Fast, focused scan for IFCs under a user-chosen folder.
    """
    start = time.monotonic()
    root = Path(path)
    if not root.exists() or not root.is_dir():
        return {"ok": False, "folder": str(root), "count": 0, "ifc_files": []}

    hits: List[str] = []
    from collections import deque
    q = deque([(root, 0)])
    budget_s = max(0.05, timeout_ms / 1000.0)

    while q and (time.monotonic() - start) <= budget_s:
        d, depth = q.popleft()
        try:
            with os.scandir(d) as it:
                for e in it:
                    if e.is_file():
                        n = e.name.lower()
                        if n.endswith(".ifc") or n.endswith(".ifczip") or n.endswith(".ifcxml"):
                            hits.append(e.path)
                            if len(hits) >= max_hits:
                                return {"ok": True, "folder": str(root), "count": len(hits), "ifc_files": hits}
                    elif recursive and depth < max_depth and e.is_dir(follow_symlinks=False):
                        name = os.path.basename(e.path)
                        if name in IGNORE_DIRS:
                            continue
                        q.append((Path(e.path), depth + 1))
        except Exception:
            pass

    return {"ok": bool(hits), "folder": str(root), "count": len(hits), "ifc_files": hits}


# -------------------------
# UI launch & status endpoints
# -------------------------

def _first_existing(*candidates: Union[str, Path]) -> Optional[Path]:
    for c in candidates:
        if not c:
            continue
        p = Path(c).expanduser().resolve()
        if p.exists():
            return p
    return None

def _require_exists(label: str, p: Path):
    if not p.exists():
        raise HTTPException(status_code=400, detail=f"{label} not found: {p}")

def _pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    proc = Path(f"/proc/{pid}")
    if not proc.exists():
        return False
    try:
        cmd = (proc / "cmdline").read_text(errors="ignore")
        return "mainwindow.py" in cmd or "greyform" in cmd.lower()
    except Exception:
        return False

@app.post("/api/launch_ui")
async def launch_ui(usb_path: str = Form(...), ifc_path: Optional[str] = Form(None)):
    try:
        base = Path(usb_path).resolve()
        if not base.exists() or not base.is_dir():
            raise HTTPException(status_code=400, detail=f"usb_path not found or not a directory: {usb_path}")

        if ifc_path:
            ifc = Path(ifc_path).resolve()
        else:
            # Prefer a fast focused search in the chosen folder
            ifc = pick_ifc(base, recursive=True, max_depth=8)
            if ifc is None:
                raise HTTPException(status_code=404, detail="No IFC file found on the USB drive")

        # ensure IFC is inside usb_path
        try:
            _ = ifc.resolve().relative_to(base)
        except ValueError:
            raise HTTPException(status_code=400, detail="IFC must be inside usb_path")

        project_dir = Path(__file__).resolve().parent.parent
        main_py = (project_dir / "mainwindow.py").resolve()
        ui_file = (project_dir / "UI_Design" / "greyform_sweefeng.ui").resolve()
        excel_checklist = (project_dir / "Greyform TERRAHL2(JMB)-T1a BOM Checklist 20231211.xlsx").resolve()
        excel_output = (project_dir / "PBU_TERRAHL2(final).xlsx").resolve()

        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        env.setdefault("QT_QPA_PLATFORM", "xcb")

        args = ["python3", str(main_py), str(ui_file), str(ifc), str(excel_checklist), str(excel_output)]

        LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        log_f = open(LOGFILE, "ab", buffering=0)

        if LOCKFILE.exists():
            raise HTTPException(status_code=409, detail="UI relaunch is locked (machine should be powered off).")

        if PIDFILE.exists():
            try:
                saved = int(PIDFILE.read_text().strip())
                if _pid_running(saved):
                    return {"status": "running", "message": f"UI already running (pid {saved})", "pid": saved}
            except Exception:
                pass

        proc = subprocess.Popen(
            args,
            cwd=str(project_dir),
            env=env,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        PIDFILE.write_text(str(proc.pid))
        return {
            "status": "started",
            "message": f"UI started (pid {proc.pid})",
            "pid": proc.pid,
            "ifc_path": str(ifc),
            "log_file": str(LOGFILE),
        }
    except HTTPException:
        raise
    except Exception:
        print("Exception launching Qt UI:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Exception launching with usb_path={usb_path}")

@app.post("/api/ui_closed")
def ui_closed(pid: int = Form(...)):
    try:
        saved = int(PIDFILE.read_text().strip())
        if saved == pid:
            PIDFILE.unlink(missing_ok=True)
            LOCKFILE.write_text(datetime.now().isoformat())
    except Exception:
        pass
    return {"ok": True}

@app.get("/api/ui_status")
def ui_status(pid: Optional[int] = Query(None)):
    if pid is None and PIDFILE.exists():
        try:
            pid = int(PIDFILE.read_text().strip())
        except Exception:
            pid = None
    if pid is None:
        return {"running": False, "pid": None}
    running = _pid_running(pid)
    if not running and PIDFILE.exists():
        try:
            saved = int(PIDFILE.read_text().strip())
            if saved == pid:
                PIDFILE.unlink(missing_ok=True)
                if not LOCKFILE.exists():
                    LOCKFILE.write_text(datetime.now().isoformat())
        except Exception:
            pass
    return {"running": running, "pid": pid}

@app.post("/api/reset_lock")
def reset_lock():
    try:
        LOCKFILE.unlink(missing_ok=True)
        return {"ok": True, "message": "Lock cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear lock: {e}")

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}
