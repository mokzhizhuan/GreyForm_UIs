from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
import pandas as pd
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.marking_controller import app as marking_subapp
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
# Robot endpoint (NO ROS NEEDED)
# ============================================================
@app.get("/getdirectory")
def getdirectory():
    process = subprocess.Popen(
        [
            "sshpass",
            "-p",
            "winsys",
            "ssh",
            "winsys@192.168.130.5",
            "python3",
            "/home/winsys/pbu_marking_ros/directorysearch.py",
            "--directory",
            "/home/winsys/pbu_marking_ros/pbu_data/mockup/",
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


@app.get("/jointtarget/connection")
def jointtarget_connection():
    process = subprocess.Popen(
        [
            "sshpass",
            "-p",
            "winsys",
            "ssh",
            "winsys@192.168.130.5",
            "python3",
            "/home/winsys/pbu_marking_ros/homeposcheck.py",
            "--file",
            "/home/winsys/pbu_marking_ros/pbu_data/mockup/poses.json",
            "--target",
            "outside",
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
        ["sshpass", "-p", "winsys", "ssh", "winsys@192.168.130.5", "ls", "/home"],
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


class FileExecuBody(BaseModel):
    excelfile: str


@app.post("/file_execute_data")
def file_execute_data(body: FileExecuBody):
    excelFile = body.excelfile  # <── get from JSON body
    try:
        process = subprocess.Popen(
            [
                "sshpass",
                "-p",
                "winsys",
                "ssh",
                "winsys@192.168.130.5",
                "python3",
                "/home/winsys/pbu_marking_ros/detectwalls.py",
                "--filename",
                excelFile,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        lines = [line.rstrip("\n") for line in process.stdout]
        process.wait()

        return {
            "ok": process.returncode == 0,
            "returncode": process.returncode,
            "data": lines,
        }

    except Exception as e:
        return {"ok": False, "error": str(e), "data": []}
    

class CombineRequest(BaseModel):
    folder: str   # full path: /home/ros_user/pbu_data/mockup/PBU_TERRAHL2_out


@app.post("/combine_walls")
def combine_walls(req: CombineRequest):

    # Remote command for SSH
    remote_cmd = (
        f"python3 /home/winsys/combine_wall_excels.py '{req.folder}'"
    )

    cmd = [
        "sshpass",
        "-p",
        "winsys",
        "ssh",
        "winsys@192.168.130.5",
        remote_cmd,
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SSH call failed: {str(e)}"
        )

    # If SSH failed
    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"SSH error: {result.stderr.strip()}"
        )

    # Parse the JSON return from combine_wall_excels.py
    try:
        response_data = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON returned from remote script: {result.stdout}"
        )

    return response_data


