# backend/main.py
import os, stat , json , time , glob , shutil, traceback , subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Union, Tuple , Any
import dataanalysis as datadraft
import pwd, grp , requests
import subprocess, shlex
import threading
from errno import errorcode
from src.talker_listener.talker_listener import talker_node as RosPublisher
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Form, HTTPException, Query, Request , HTTPException , Body
from fastapi.middleware.cors import CORSMiddleware
from roscore_service import start_roscore, stop_roscore, is_master_up, ROS_MASTER_URI
import processlistenerrunner as ListenerNode
from backend.rosapp import app as ros_app



app = FastAPI(title="Main API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/ros", ros_app)
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
  
