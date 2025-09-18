# backend/main.py
import os
import stat
import json
import time
import glob
import shutil
import traceback
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Union, Tuple

import pwd, grp
from errno import errorcode
from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


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
_CACHE = {"ts": 0.0, "preferred": None, "choices": []}
_CACHE_TTL = 5.0  # seconds
PROJECT_DIR = Path(__file__).resolve().parent.parent  
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

def _is_under_media(p: Path) -> bool:
    s = str(p)
    return any(s == str(r) or s.startswith(str(r) + "/") for r in MEDIA_ROOTS)

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
    seen, uniq = set(), []
    for p in out:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp not in seen:
            uniq.append(rp)
            seen.add(rp)
    return uniq

def _cheap_list(d: Path, exts: List[str], limit: int = 200) -> List[str]:
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

def _has_entries(d: Path) -> bool:
    try:
        with os.scandir(d) as it:
            return next(it, None) is not None
    except Exception:
        return False

def _iter_files(root: Path, max_depth: int = 3):
    base = root.resolve()
    base_depth = len(base.parts)
    for p in base.rglob("*"):
        try:
            if p.is_file():
                depth = len(p.resolve().parts) - base_depth
                if depth <= max_depth:
                    yield p
        except Exception:
            continue

def _root_ok(root: Path) -> Dict:
    if not root.exists() or not root.is_dir():
        return {"exists": False, "valid": False, "files": []}
    files = [p.name for p in _iter_files(root, max_depth=3) if p.suffix.lower() in WANTED_EXTS]
    return {"exists": True, "valid": len(files) > 0, "files": files[:50]}

def pick_ifc(root: Path, recursive: bool = True, max_depth: int = 8) -> Optional[Path]:
    if not root.exists() or not root.is_dir():
        return None
    candidates: List[Tuple[Path, float]] = []
    for p in _iter_files(root, max_depth=max_depth):
        if p.suffix.lower() in IFC_EXTS:
            try:
                candidates.append((p, p.stat().st_mtime))
            except Exception:
                pass
    if not candidates:
        return None
    candidates.sort(key=lambda t: (t[0].suffix.lower() != ".ifc", -t[1]))
    return candidates[0][0]

def _first_existing(*cands: Union[str, Path]) -> Optional[Path]:
    for c in cands:
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

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}

@app.get("/api/whoami")
def whoami():
    uid = os.geteuid()
    gid = os.getegid()
    def uname(u): 
        try: return pwd.getpwuid(u).pw_name
        except Exception: return f"uid:{u}"
    def gname(g): 
        try: return grp.getgrgid(g).gr_name
        except Exception: return f"gid:{g}"
    return {
        "uid": uid, "gid": gid,
        "user": uname(uid), "group": gname(gid),
        "cwd": os.getcwd(),
        "can_read_media": os.access("/media", os.R_OK | os.X_OK),
        "can_x_ubuntu": os.access("/media/ubuntu", os.X_OK),
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
        eno = getattr(e, "errno", None)
        return {
            "ok": False,
            "reason": type(e).__name__,
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

    # cache hit?
    got = IFC_CACHE.get(str(r))
    if got:
        p = Path(got.get("path", ""))
        try:
            if p.is_file():
                return {"ok": True, "match": str(p), "cached": True}
        except Exception:
            pass
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
    m = scan_dir_once(r)
    if m:
        IFC_CACHE[str(r)] = {"path": m, "mtime": Path(m).stat().st_mtime}
        _cache_save()
        return {"ok": True, "match": m, "cached": False}
    lvl1: List[Path] = []
    try:
        with os.scandir(r) as it:
            for e in it:
                if e.is_dir(follow_symlinks=False):
                    lvl1.append(Path(e.path))
    except Exception:
        pass
    PREFERRED = {"ifc", "IFC", "models", "model", "bim", "BIM", "export", "exports"}
    for d in lvl1:
        if d.name in PREFERRED:
            m = scan_dir_once(d)
            if m:
                IFC_CACHE[str(r)] = {"path": m, "mtime": Path(m).stat().st_mtime}
                _cache_save()
                return {"ok": True, "match": m, "cached": False}
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

@app.get("/api/find_ifc_fast")
def find_ifc_fast(
    root: Optional[str] = Query(None, description="Optional mount or wildcard, e.g. /media/*/*"),
    max_depth: int = Query(3, ge=0, le=20),
    timeout_ms: int = Query(1200, ge=100, le=10000),
):
    candidates: List[Path] = []
    if root:
        if any(ch in root for ch in "*?[]"):
            candidates = [Path(p) for p in glob.glob(root) if Path(p).is_dir()]
        else:
            candidates = [Path(root)]
    if not candidates:
        mounts = _iter_mounts_under_media() or MEDIA_ROOTS
        candidates = [m for m in mounts if m.exists() and m.is_dir()]
    per_root_timeout = max(200, int(timeout_ms / max(1, min(len(candidates), 4))))
    find_bin = _which_find()
    for r in candidates:
        got = IFC_CACHE.get(str(r))
        if got:
            p = Path(got.get("path", ""))
            try:
                if p.is_file():
                    return {"ok": True, "match": str(p), "cached": True}
            except Exception:
                pass
        cmd = [
            find_bin, str(r), "-maxdepth", str(max_depth),
            "-type", "f",
            "(", "-iname", "*.ifc", "-o", "-iname", "*.ifczip", "-o", "-iname", "*.ifcxml", ")",
            "-printf", "%T@ %p\n",
        ]
        try:
            cp = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=per_root_timeout / 1000.0, check=False)
            out = cp.stdout.strip()
            if out:
                lines = out.splitlines()
                # newest first; prefer .ifc
                lines.sort(key=lambda s: (float(s.split(" ", 1)[0]),
                                          s.split(" ", 1)[1].lower().endswith(".ifc")), reverse=True)
                ts, path = lines[0].split(" ", 1)
                IFC_CACHE[str(r)] = {"path": path, "mtime": float(ts)}
                _cache_save()
                return {"ok": True, "match": path, "cached": False}
        except Exception:
            pass
        try:
            cmd2 = [find_bin, str(r), "-maxdepth", str(max_depth), "-type", "f",
                    "(", "-iname", "*.ifc", "-o", "-iname", "*.ifczip", "-o", "-iname", "*.ifcxml", ")"]
            cp2 = subprocess.run(cmd2, capture_output=True, text=True,
                                 timeout=per_root_timeout / 1000.0, check=False)
            out2 = [p for p in cp2.stdout.strip().splitlines() if p]
            if out2:
                sel = out2[0]
                try:
                    ts = Path(sel).stat().st_mtime
                except Exception:
                    ts = 0.0
                IFC_CACHE[str(r)] = {"path": sel, "mtime": ts}
                _cache_save()
                return {"ok": True, "match": sel, "cached": False}
        except Exception:
            pass
    return {"ok": False, "reason": "no-match", "match": None}


@app.get("/api/detect_usb")
def detect_usb(
    path: Optional[str] = Query(None, description="Optional hint; wildcards like /media/*/*"),
    scan_media: bool = Query(True, description="Scan /media and /run/media"),
    need_files: bool = Query(False, description="If true, add cheap (non-recursive) file list"),
):
    now = time.monotonic()
    if (now - _CACHE["ts"]) < _CACHE_TTL and _CACHE["preferred"]:
        return {"found": True, "preferred": _CACHE["preferred"], "choices": _CACHE["choices"], "checked": [], "cached": True}
    checked: List[Dict] = []
    choices: List[Dict] = []
    roots = _expand_roots(path)
    if scan_media:
        roots += [Path("/media"), Path("/run/media")]
        roots += [Path(p) for p in glob.glob("/media/*/*")]
        roots += [Path(p) for p in glob.glob("/run/media/*/*")]
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
        has_any = _has_entries(rp)
        ismnt = os.path.ismount(rp)
        info = {
            "path": str(rp),
            "exists": True,
            "valid": bool(files) or ismnt or has_any,
            "files": files,
            "ismount": ismnt,
            "has_entries": has_any,
        }
        checked.append(info)
        if info["valid"]:
            choices.append({"path": info["path"], "files": info["files"]})
            _CACHE.update(ts=now, preferred=info["path"], choices=choices)
            return {"found": True, "preferred": info["path"], "choices": choices, "checked": checked, "cached": False}
    return {"found": False, "preferred": None, "choices": choices, "checked": checked, "cached": False}

@app.post("/api/launch_ui")
async def launch_ui(
    usb_path: str = Form(...),
    ifc_path: Optional[str] = Form(None),
    force: bool = Form(False),
):
    try:
        base = Path(usb_path).resolve()
        if not base.exists() or not base.is_dir():
            raise HTTPException(status_code=400, detail=f"usb_path not found or not a directory: {usb_path}")
        if ifc_path:
            ifc = Path(ifc_path).resolve()
        else:
            ifc = pick_ifc(base, recursive=True, max_depth=8)
            if ifc is None:
                raise HTTPException(status_code=404, detail="No IFC file found on the USB drive")
        try:
            _ = ifc.resolve().relative_to(base)
        except ValueError:
            raise HTTPException(status_code=400, detail="IFC must be inside usb_path")
        main_py = (PROJECT_DIR / "mainwindow.py").resolve()
        ui_file = (PROJECT_DIR / "UI_Design" / "greyform_sweefeng.ui").resolve()
        excel_checklist = (PROJECT_DIR / "Greyform TERRAHL2(JMB)-T1a BOM Checklist 20231211.xlsx").resolve()
        excel_output = (PROJECT_DIR / "PBU_TERRAHL2(final).xlsx").resolve()
        if not main_py.exists():
            raise HTTPException(500, detail=f"mainwindow.py not found: {main_py}")
        if not ui_file.exists():
            raise HTTPException(500, detail=f"UI .ui file not found: {ui_file}")
        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        env.setdefault("QT_QPA_PLATFORM", "xcb")
        args = ["python3", str(main_py), str(ui_file), str(ifc), str(excel_checklist), str(excel_output)]
        LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        log_f = open(LOGFILE, "ab", buffering=0)
        if LOCKFILE.exists():
            LOCKFILE.unlink(missing_ok=True)
        if PIDFILE.exists():
            try:
                saved = int(PIDFILE.read_text().strip())
                if _pid_running(saved):
                    return {"status": "running", "message": f"UI already running (pid {saved})", "pid": saved}
            except Exception:
                pass
        proc = subprocess.Popen(
            args,
            cwd=str(PROJECT_DIR),
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
