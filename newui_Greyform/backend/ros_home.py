import threading
from typing import Dict, Optional
from urllib.parse import urlunparse, urlencode

import rospy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sensor_msgs.msg import JointState
import httpx
import os

app = FastAPI(title="ROS HOME Monitor", version="1.2.0")

# -----------------------
# Settings (env override)
# -----------------------
ROS_NODE_NAME       = os.getenv("ROS_NODE_NAME", "home_status_monitor")
JOINT_STATES_TOPIC  = os.getenv("JOINT_STATES_TOPIC", "/joint_states")

HOME = {
    "joint_1": float(os.getenv("HOME_J1", 0.0)),
    "joint_2": float(os.getenv("HOME_J2", -1.5708)),
    "joint_3": float(os.getenv("HOME_J3", 1.5708)),
    "joint_4": float(os.getenv("HOME_J4", 0.0)),
    "joint_5": float(os.getenv("HOME_J5", 1.5708)),
    "joint_6": float(os.getenv("HOME_J6", 0.0)),
}
TOL = float(os.getenv("HOME_TOL", 0.02))
# per-joint tolerance overrides: "joint_2:0.03,joint_5:0.015"
_tol_map_env = os.getenv("HOME_TOL_MAP", "")
TOL_MAP: Dict[str, float] = {}
if _tol_map_env:
    for pair in _tol_map_env.split(","):
        if pair.strip():
            name, val = pair.split(":")
            TOL_MAP[name.strip()] = float(val)

# FlexPendant/controller URL pieces
CONTROLLER_SCHEME = os.getenv("CONTROLLER_SCHEME", "http")
CONTROLLER_HOST   = os.getenv("CONTROLLER_HOST", "192.168.125.1")
CONTROLLER_PORT   = int(os.getenv("CONTROLLER_PORT", "80"))
CONTROLLER_PATH   = os.getenv("CONTROLLER_PATH", "")  # "" or "/rw" etc.
PATH_WHITELIST    = [p for p in os.getenv("PATH_WHITELIST", "/,/rw").split(",") if p]
TLS_VERIFY        = os.getenv("TLS_VERIFY", "true").lower() == "true"
LINK_TIMEOUT      = float(os.getenv("LINK_TIMEOUT", "2.0"))

ALLOW_ORIGINS = [
    os.getenv("CORS_ORIGIN", "http://localhost:5173"),
    os.getenv("CORS_ORIGIN2", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Background ROS monitor
# -----------------------
_state_lock = threading.Lock()
_latest_home_ok = False
_latest_reason = "No data yet"
_latest_stamp = 0.0

def _is_home(joint_map: Dict[str, float]):
    missing = [j for j in HOME if j not in joint_map]
    if missing:
        return False, f"Missing joints: {', '.join(missing)}"
    for j, target in HOME.items():
        tol = TOL_MAP.get(j, TOL)
        err = abs(joint_map[j] - target)
        if err > tol:
            return False, f"{j} off by {err:.4f} rad (> {tol:.4f})"
    return True, "Within tolerance"

def _ros_spin():
    rospy.init_node(ROS_NODE_NAME, anonymous=True, disable_signals=True)

    def _cb(msg: JointState):
        global _latest_home_ok, _latest_reason, _latest_stamp
        jm = dict(zip(msg.name, msg.position))
        ok, reason = _is_home(jm)
        with _state_lock:
            _latest_home_ok = ok
            _latest_reason = reason
            _latest_stamp = msg.header.stamp.to_sec() if msg.header and msg.header.stamp else 0.0

    rospy.Subscriber(JOINT_STATES_TOPIC, JointState, _cb, queue_size=1)
    rospy.spin()

@app.on_event("startup")
def _startup():
    t = threading.Thread(target=_ros_spin, daemon=True)
    t.start()

# -------------
# API models
# -------------
class VerifyResponse(BaseModel):
    home: bool
    reason: str
    stamp: float

class StatusResponse(BaseModel):
    ok: bool
    details: str

class FlexLink(BaseModel):
    url: str
    reachable: bool

# -------------
# Endpoints
# -------------
@app.get("/verify-home", response_model=VerifyResponse)
async def verify_home():
    with _state_lock:
        return VerifyResponse(home=_latest_home_ok, reason=_latest_reason, stamp=_latest_stamp)

@app.get("/status", response_model=StatusResponse)
async def status():
    with _state_lock:
        ok = _latest_reason != "No data yet"
        return StatusResponse(ok=ok, details=_latest_reason)

# -------- FlexPendant linking / deep-links --------
def _build_controller_url(subpath: str = "", query: Optional[Dict[str, str]] = None) -> str:
    base_path = CONTROLLER_PATH or ""
    if base_path and not base_path.startswith("/"):
        base_path = "/" + base_path
    if subpath and not subpath.startswith("/"):
        subpath = "/" + subpath
    full_path = base_path + (subpath or "")

    if PATH_WHITELIST and not any(full_path.startswith(p) for p in PATH_WHITELIST):
        full_path = base_path or "/"

    q = urlencode(query or {}, doseq=True)
    return urlunparse((
        CONTROLLER_SCHEME,
        f"{CONTROLLER_HOST}:{CONTROLLER_PORT}",
        full_path,
        "",
        q,
        "",
    ))

@app.get("/flexpendant/link", response_model=FlexLink)
async def flexpendant_link(subpath: str = "", q: Optional[str] = None):
    # q = raw query string like "tab=jogging&view=axes"
    query = dict([p.split("=", 1) for p in (q.split("&") if q else [])]) if q else None
    url = _build_controller_url(subpath=subpath, query=query)
    reachable = False
    try:
        timeout = httpx.Timeout(LINK_TIMEOUT)
        async with httpx.AsyncClient(verify=TLS_VERIFY, timeout=timeout) as client:
            r = await client.request("HEAD", url)
            if r.status_code >= 400:
                r = await client.get(url)
            reachable = r.status_code < 400
    except Exception:
        reachable = False
    return FlexLink(url=url, reachable=reachable)

@app.get("/flexpendant/redirect")
async def flexpendant_redirect(subpath: str = "", q: Optional[str] = None):
    query = dict([p.split("=", 1) for p in (q.split("&") if q else [])]) if q else None
    url = _build_controller_url(subpath=subpath, query=query)
    return RedirectResponse(url=url, status_code=302)
