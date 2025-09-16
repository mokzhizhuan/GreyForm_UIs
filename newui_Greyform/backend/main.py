# backend/main.py
import os, subprocess, traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Iterable, List, Dict, Union
from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fnmatch import fnmatch
import threading, time

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

<<<<<<< Updated upstream
<<<<<<< Updated upstream
def _list_mounts(base="/media/ubuntu") -> List[str]:
    try:
        with os.scandir(base) as it:
            return [e.path for e in it if e.is_dir(follow_symlinks=False)]
    except FileNotFoundError:
        return []

@app.get("/api/usb_list")
def usb_list(path: str = "/media/ubuntu"):
    """FAST: just list mount directories under /media/ubuntu."""
    mounts = _list_mounts(path)
    return {"paths": mounts, "found": bool(mounts), "preferred": mounts[0] if mounts else None}

def _peek_for_patterns(root: str,
                       patterns: List[str],
                       max_depth: int = 2,
                       max_files: int = 5000,
                       deadline: Optional[float] = None) -> Optional[str]:
    """Bounded, shallow peek for matching files; returns first hit or None."""
    seen = 0
    for cur, dirs, files in os.walk(root):
        depth = cur[len(root):].count(os.sep)
        if depth >= max_depth:
            dirs[:] = []  # stop descending deeper
        for f in files:
            seen += 1
            if any(fnmatch(f.lower(), p) for p in patterns):
                return os.path.join(cur, f)
            if seen >= max_files or (deadline and time.time() > deadline):
                return None
    return None

@app.get("/api/detect_usb")
def detect_usb(
    path: str = "/media/ubuntu",
    scan_media: bool = True,
    need_files: bool = False,
    patterns: str = Query("*.ifc,*.stl,*.xlsx,*.xls,*.csv", description="comma-separated"),
    timeout: float = 0.6,  # seconds budget for OPTIONAL peek
):
    """FAST path detection; optional, bounded file peek if need_files=true."""
    mounts = _list_mounts(path) if scan_media else ([path] if os.path.isdir(path) else [])
    if not mounts:
        return {"found": False, "preferred": None, "paths": []}

    preferred = mounts[0]
    first_match = None

    if need_files:
        pats = [p.strip().lower() for p in patterns.split(",") if p.strip()]
        deadline = time.time() + max(0.1, timeout)
        for m in mounts:
            hit = _peek_for_patterns(m, pats, max_depth=2, max_files=5000, deadline=deadline)
            if hit:
                preferred, first_match = m, hit
                break

    return {"found": True, "preferred": preferred, "paths": mounts, "match": first_match}

def _dir_has_wanted_files(d: Path, exts=WANTED_EXTS, max_files=50) -> list[str]:
    files = []
    try:
        for p in d.iterdir():
            if p.is_file() and p.suffix.lower() in exts:
                files.append(str(p))
                if len(files) >= max_files:
                    break
    except Exception:
        pass
    return files

def _gather_candidates(roots: list[Path], max_depth: int = 2) -> list[Path]:
    out, seen = [], set()
    stack = [(r, 0) for r in roots if r.exists()]
    while stack:
        d, depth = stack.pop()
        try:
            rp = d.resolve()
        except Exception:
            continue
        if rp in seen or not rp.is_dir():
            continue
        seen.add(rp)
        out.append(rp)
        if depth < max_depth:
            try:
                for c in rp.iterdir():
                    if c.is_dir():
                        stack.append((c, depth + 1))
            except Exception:
                pass
    return out

@app.get("/api/detect_usb")
=======
def _dir_has_wanted_files(d: Path, exts=WANTED_EXTS, max_files=50) -> list[str]:
    files = []
    try:
        for p in d.iterdir():
            if p.is_file() and p.suffix.lower() in exts:
                files.append(str(p))
                if len(files) >= max_files:
                    break
    except Exception:
        pass
    return files

def _gather_candidates(roots: list[Path], max_depth: int = 2) -> list[Path]:
    out, seen = [], set()
    stack = [(r, 0) for r in roots if r.exists()]
    while stack:
        d, depth = stack.pop()
        try:
            rp = d.resolve()
        except Exception:
            continue
        if rp in seen or not rp.is_dir():
            continue
        seen.add(rp)
        out.append(rp)
        if depth < max_depth:
            try:
                for c in rp.iterdir():
                    if c.is_dir():
                        stack.append((c, depth + 1))
            except Exception:
                pass
    return out

@app.get("/api/detect_usb")
>>>>>>> Stashed changes
def detect_usb(path: str | None = Query(None), scan_media: bool = Query(True)):
    roots = []
    if path:
        roots.append(Path(path))
    if scan_media:
        roots += [Path("/media"), Path("/run/media")]
    checked, choices = [], []
    for d in _gather_candidates(roots, max_depth=2):
        files = _dir_has_wanted_files(d)
        info = {
            "path": str(d),
            "exists": True,
            "valid": bool(files) or os.path.ismount(d),
            "files": files,
            "ismount": os.path.ismount(d),
        }
        checked.append(info)
        if info["valid"]:
            choices.append({"path": info["path"], "files": info["files"]})
    return {
        "found": bool(choices),
        "preferred": choices[0]["path"] if choices else None,
        "choices": choices,
        "checked": checked,
    }
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

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
    candidates.sort(key=lambda t: (t[0].suffix.lower() != ".ifc", -t[1]))
    return candidates[0][0]


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
            raise HTTPException(
                status_code=400,
                detail=f"usb_path not found or not a directory: {usb_path}",
            )
        if ifc_path:
            ifc = Path(ifc_path).resolve()
        else:
            ifc = pick_ifc(base, recursive=True, max_depth=8)
            if ifc is None:
                raise HTTPException(
                    status_code=404, detail="No IFC file found on the USB drive"
                )
        try:
            _ = ifc.resolve().relative_to(base)
        except ValueError:
            raise HTTPException(status_code=400, detail="IFC must be inside usb_path")
        project_dir = Path(__file__).resolve().parent.parent
        main_py = (project_dir / "mainwindow.py").resolve()
        ui_file = (project_dir / "UI_Design" / "greyform_sweefeng.ui").resolve()
        excel_checklist = (
            project_dir / "Greyform TERRAHL2(JMB)-T1a BOM Checklist 20231211.xlsx"
        ).resolve()
        excel_output = (project_dir / "PBU_TERRAHL2(final).xlsx").resolve()
        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        env.setdefault("QT_QPA_PLATFORM", "xcb")
        args = [
            "python3",
            str(main_py),
            str(ui_file),
            str(ifc),
            str(excel_checklist),
            str(excel_output),
        ]
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
        raise HTTPException(
            status_code=500, detail=f"Exception launching with usb_path={usb_path}"
        )


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
