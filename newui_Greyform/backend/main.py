# backend/main.py
import os, importlib, subprocess, shlex
from pathlib import Path
from typing import Optional, Dict
from contextlib import asynccontextmanager
import sys

import pwd, grp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from roscore_service import start_roscore, stop_roscore, is_master_up, ROS_MASTER_URI
from backend.build_subapp import build_app as catkin_builder

WS = Path("/root/catkin_ws/newui_Greyform")
SCRIPT = WS / "safe_catkin_make.sh"
ENV_SNAPSHOT = WS / ".env_after_build"

DEVEL_PYTHON = WS / "devel" / "lib" / "python3" / "dist-packages"
ROS_PYTHON = Path("/opt/ros/noetic/lib/python3/dist-packages")
for p in (DEVEL_PYTHON, ROS_PYTHON):
    if p.exists():
        p_str = str(p)
        if p_str not in sys.path:
            sys.path.insert(0, p_str)


def _run(cmd: str):
    # Run a bash login shell to ensure /etc/profile is respected if needed
    subprocess.run(["bash", "-lc", cmd], check=True)

def ensure_built():
    # Build if first run OR if devel/setup.bash missing
    need = not (WS / "devel/setup.bash").exists()
    if need:
        _run(f"source /opt/ros/noetic/setup.bash && {shlex.quote(str(SCRIPT))}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) Ensure build completed (blocks startup until done)
    ensure_built()
    # 2) Only now import and mount ros app (lazy import after build)
    ros_module = importlib.import_module("backend.rosapp")
    ros_app = getattr(ros_module, "app")
    app.mount("/ros", ros_app)
    yield
    # (optional) shutdown cleanup here if needed

app = FastAPI(title="Main API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount the catkin build sub-app
app.mount("/build", catkin_builder)

PIDFILE = Path("/tmp/greyform_ui.pid")
LOCKFILE = Path("/tmp/greyform_ui.lock")
LOGFILE = Path("/tmp/greyform_ui.log")

WANTED_EXTS = {".ifc", ".ifczip", ".step", ".stp", ".csv", ".xlsx", ".xls"}
IFC_EXTS = {".ifc", ".ifczip", ".ifcxml"}
MEDIA_ROOTS = [Path("/media"), Path("/run/media")]
CACHE_FILE = Path("/tmp/ifc_cache.json")
IFC_CACHE: Dict[str, Dict[str, float]] = {}
PROJECT_DIR = Path(__file__).resolve().parent.parent
LAST_USB_PATH: Optional[Path] = None

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}

@app.get("/api/whoami")
def whoami():
    uid = os.geteuid()
    gid = os.getegid()

    def uname(u):
        try:
            return pwd.getpwuid(u).pw_name
        except Exception:
            return f"uid:{u}"

    def gname(g):
        try:
            return grp.getgrgid(g).gr_name
        except Exception:
            return f"gid:{g}"

    return {
        "uid": uid,
        "gid": gid,
        "user": uname(uid),
        "group": gname(gid),
        "cwd": os.getcwd(),
        "can_read_media": os.access("/media", os.R_OK | os.X_OK),
        "can_x_ubuntu": os.access("/media/ubuntu", os.X_OK),
    }

@app.get("/roscore/status")
def status():
    return {
        "master_uri": ROS_MASTER_URI,
        "up": is_master_up(),
    }

@app.post("/roscore/start")
def start():
    try:
        start_roscore(log=True)
        return {"status": "started", "uri": ROS_MASTER_URI}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/roscore/stop")
def stop():
    stop_roscore()
    return {"status": "stopped"}
