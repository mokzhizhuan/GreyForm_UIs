# fastapi_ros_home.py
import threading
import math
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

import rospy
from sensor_msgs.msg import JointState  # or your ABB status msg

app = FastAPI()
_home_ok = False
_lock = threading.Lock()

# Define your "home" joint targets (example values)
HOME = {
    "joint_1": 0.0,
    "joint_2": -1.5708,
    "joint_3": 1.5708,
    "joint_4": 0.0,
    "joint_5": 1.5708,
    "joint_6": 0.0,
}
TOL = 0.02  # radians, tune as needed


def is_home(name: List[str], position: List[float]) -> bool:
    joint_map = dict(zip(name, position))
    for j, target in HOME.items():
        if j not in joint_map:
            return False
        if abs(joint_map[j] - target) > TOL:
            return False
    return True


def ros_worker():
    rospy.init_node("home_status_monitor", anonymous=True, disable_signals=True)

    def cb(msg: JointState):
        global _home_ok
        ok = is_home(msg.name, msg.position)
        with _lock:
            _home_ok = ok

    rospy.Subscriber("/joint_states", JointState, cb, queue_size=1)
    rospy.spin()


@app.on_event("startup")
def start_ros_thread():
    t = threading.Thread(target=ros_worker, daemon=True)
    t.start()


class VerifyResponse(BaseModel):
    home: bool


@app.get("/verify-home", response_model=VerifyResponse)
def verify_home():
    with _lock:
        return VerifyResponse(home=_home_ok)
