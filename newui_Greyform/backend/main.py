# backend/main.py
import os, subprocess, traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Iterable, List, Dict , Union
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
LOGFILE = Path("/tmp/greyform_ui.log")

@app.get("/api/detect_usb")
def detect_usb(path: str = Query("/mnt/usb"), scan_media: bool = Query(True)):
    checked: List[Dict] = []
    choices: List[Dict] = []
    base = Path(path)
    to_test = [base]
    media = Path("/media/ubuntu")
    if scan_media and media.exists():
        to_test.extend([p for p in media.iterdir() if p.is_dir()])
    for root in to_test:
        info = _root_ok(root)
        checked.append({"path": str(root), **info})
        if info["exists"] and info["valid"]:
            choices.append({"path": str(root), "files": info["files"]})
    return {
        "found": len(choices) > 0,
        "preferred": choices[0]["path"] if choices else None,
        "choices": choices,
        "checked": checked,
    }


IFC_EXTS = {".ifc", ".ifczip", ".ifcxml"}


def _iter_files(root: Path, max_depth: int = 3):
    """Yield files under root up to max_depth levels deep."""
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


# keep your WANTED_EXTS as-is
WANTED_EXTS = {".pbt", ".ifc", ".ifczip", ".ifcxml"}


# replace the old _root_ok with a recursive version
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
            raise HTTPException(status_code=400, detail=f"usb_path not found or not a directory: {usb_path}")

        # pick_ifc(...) -> you already have this
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

        # Resolve paths to your files (adjust project_dir if needed)
        project_dir = Path(__file__).resolve().parent.parent
        main_py = (project_dir / "mainwindow.py").resolve()
        ui_file = (project_dir / "UI_Design" / "greyform_sweefeng.ui").resolve()
        excel_checklist = (project_dir / "Greyform TERRAHL2(JMB)-T1a BOM Checklist 20231211.xlsx").resolve()
        excel_output    = (project_dir / "PBU_TERRAHL2(final).xlsx").resolve()

        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        env.setdefault("QT_QPA_PLATFORM", "xcb")

        args = [
            "python3", str(main_py),
            str(ui_file),
            str(ifc),
            str(excel_checklist),
            str(excel_output),
        ]

        LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        log_f = open(LOGFILE, "ab", buffering=0)

        # START DETACHED (do NOT call communicate)
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
    # trust-but-verify: if this pid matches the one we started, clear it
    try:
        saved = int(PIDFILE.read_text().strip())
        if saved == pid:
            PIDFILE.unlink(missing_ok=True)
    except Exception:
        pass
    return {"ok": True}



@app.get("/api/ui_status")
def ui_status(pid: Optional[int] = Query(None)):
    # if pid not provided, read pidfile (nice fallback)
    if pid is None and PIDFILE.exists():
        try:
            pid = int(PIDFILE.read_text().strip())
        except Exception:
            pid = None

    if pid is None:
        return {"running": False, "pid": None}

    running = _pid_running(pid)

    # clean up pidfile if it matches
    if not running and PIDFILE.exists():
        try:
            saved = int(PIDFILE.read_text().strip())
            if saved == pid:
                PIDFILE.unlink(missing_ok=True)
        except Exception:
            pass

    return {"running": running, "pid": pid}

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}
