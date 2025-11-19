# backend/main.py
import os
import pwd, grp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests, subprocess
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--rootdir", type=Path, default=Path.cwd())
args = parser.parse_args()

ROOTDIR = args.rootdir.resolve()

import backend.jointtargetip as jointip

# ============================================================
# 🌐 Main FastAPI Application (NO ROS, NO CATKIN)
# ============================================================
app = FastAPI(title="Main API (no ROS)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 🔹 Simple API Endpoints
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
        "can_read_media": os.access("/media", os.R_OK),
    }


# ============================================================
# 🤖 Robot jointtarget endpoint (NO ROS NEEDED)
# ============================================================
@app.get("/jointtarget/connection")
def jointtarget_connection():
    session = requests.Session()
    try:
        # Uses baked-in user/pass/IP from jointip.py
        jointip.login(session)

        data = jointip.get_request(
            session, "/rw/motionsystem/mechunits/ROB_1/jointtarget"
        )

        return {
            "ok": True,
            "jointtarget": data,
        }

    except Exception as e:
        # send error to React
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
    # /rw/motionsystem/mechunits/ROB_1/robtarget ---> end-effector pose in xyz (mm) + quat (rad)
    # /rw/motionsystem/mechunits/ROB_1/jointtarget -> joint values in degrees


class PlacementRequest(BaseModel):
    step: str


# ============================================================
# 🔍 VALIDATE PLACEMENT
# ============================================================
@app.post("/validate_placement")
def validate_placement(body: PlacementRequest):
    print("validate_placement called with:", body.step)
    return {"ok": True}


# def confition_is_met(line: str) -> bool:
# return False


@app.post("/read_directory")
def read_directory():
    process = subprocess.Popen(
        [
            "sshpass",
            "-p",
            "winsys",
            "ssh",
            "winsys@192.168.131.5",
            "ls",
            "/home/",
            f"{ROOTDIR}/TERRAHL2-FP-MB-T1am(JMB)_out.xlsx",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    lines: list[str] = []
    for line in process.stdout:
        # collect lines from ssh output
        lines.append(line.rstrip("\n"))

    process.wait()

    if process.returncode != 0:
        # something went wrong with ssh/ls
        raise HTTPException(
            status_code=500,
            detail=f"read_directory failed with return code {process.returncode}",
        )

    return {
        "ok": True,
        "data": lines,  # an array of file/dir names
    }


@app.post("/run_script")
def run_script():
    process = subprocess.Popen(
        ["./run-marking.sh", "--pbu", "1", "--wall", "4"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    matched_line: str | None = None

    lines: list[str] = []
    if process.stdout is not None:
        for line in process.stdout:
            # collect lines from ssh output
            lines.append(line.rstrip("\n"))

    # (optional) wait for process to actually terminate
    process.wait()

    return {
        "ok": True,
        "data": lines,  # null if no condition matched
    }
