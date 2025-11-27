import pwd, grp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
import requests
import pandas as pd
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from roscore_service import ROS_MASTER_URI, is_master_up, start_roscore, stop_roscore, _OWNED
import backend.jointtargetip as jointip
from backend.listenerrunner import start_listener
from backend.marking_controller import app as marking_subapp
#from backend.marking_app import markers as marking_app
import sys
import os


WS = "/root/catkin_ws/newui_Greyform"
"""DEVEL_PYTHON = os.path.join(WS, "devel/lib/python3/dist-packages")
ROS_PYTHON = "/opt/ros/noetic/lib/python3/dist-packages"

# Inject ROS paths before any ROS import happens
for p in (DEVEL_PYTHON, ROS_PYTHON):
    if p not in sys.path:
        sys.path.insert(0, p)

# NOW import marking
from backend.marking import app as marking_app
ROOTDIR = Path(__file__).resolve().parent"""

# ============================================================
# 🌐 Main FastAPI Application (NO ROS)
# ============================================================
app = FastAPI(title="Main API (no ROS)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/marking", marking_subapp)
# ============================================================
# Basic test endpoints
# ============================================================
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
        except:
            return f"uid:{u}"

    def gname(g):
        try:
            return grp.getgrgid(g).gr_name
        except:
            return f"gid:{g}"

    return {
        "uid": uid,
        "gid": gid,
        "user": uname(uid),
        "group": gname(gid),
        "cwd": os.getcwd(),
        "can_read_media": os.access("/media", os.R_OK),
    }

# ============================================================
# Robot endpoint (NO ROS NEEDED)
# ============================================================
@app.get("/jointtarget/connection")
def jointtarget_connection():
    process = subprocess.Popen(
        [
            "sshpass",
            "-p", "winsys",
            "ssh", "winsys@192.168.130.5",
            "python3", "/home/winsys/pbu_marking_ros/catkin_ws/homeposcheck.py",
            "--file", "/home/winsys/pbu_marking_ros/catkin_ws/poses.json",
            "--target", "wall_1"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    lines = [line.rstrip("\n") for line in process.stdout]
    process.wait()

    if process.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"joint_target failed (code {process.returncode})",
        )

    return {"ok": True, "data": lines}
    

# ============================================================
# Read Directory (SSH)
# ============================================================
@app.post("/read_directory")
def read_directory():
    process = subprocess.Popen(
        [
            "sshpass",
            "-p", "winsys",
            "ssh", "winsys@192.168.130.5",
            "ls", "/home"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    lines = [line.rstrip("\n") for line in process.stdout]
    process.wait()

    if process.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"read_directory failed (code {process.returncode})",
        )

    return {"ok": True, "data": lines}


# ============================================================
#  File Execute → return walls + max wall number
# ============================================================
class FileExecBody(BaseModel):
    directory: str
    excelfile: str

class WallInfo(BaseModel):
    wall: str
    count: int
    rows: List[Dict[str, Any]]


@app.post("/file_execute_data")
def file_execute_data():
    process = subprocess.Popen(
        [
            "sshpass",
            "-p", "winsys",
            "ssh", "winsys@192.168.130.5",
            "python3", "/home/winsys/pbu_marking_ros/catkin_ws/detectwalls.py",
            "--filename", "/home/winsys/pbu_marking_ros/catkin_ws/PBU_TERRAHL2_working.xlsx"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    lines = [line.rstrip("\n") for line in process.stdout]
    process.wait()
    print(lines)
    if process.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"read_directory failed (code {process.returncode})",
        )

    return {"ok": True, "data": lines}
    


#_listener_process = None


"""@app.get("/roscore/status")
def status():
    return {"master_uri": ROS_MASTER_URI, "up": is_master_up(), "owned": _OWNED}


@app.post("/roscore/start")
def start():
    global _listener_process

    try:
        start_roscore(log=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Start listener AFTER sourcing setup.bash
    if _listener_process is None:
        _listener_process = start_listener()

    return {
        "status": "started",
        "uri": ROS_MASTER_URI,
        "owned": _OWNED,
        "listener": "running"
    }


@app.post("/roscore/stop")
def stop():
    global _listener_process

    stop_roscore()

    if _listener_process:
        _listener_process.terminate()
        _listener_process = None

    return {"status": "stopped"}"""
