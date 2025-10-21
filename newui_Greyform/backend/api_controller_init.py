# api_controller_init.py
import json
import rospy
from fastapi import APIRouter, Form, HTTPException
from std_msgs.msg import String

router = APIRouter()
_pub = None
_ready = False

def _ensure_ros():
    global _pub, _ready
    if _ready:
        return
    # IMPORTANT: only one process should run this; avoid multiple Uvicorn workers.
    rospy.init_node("http_controller_init_bridge", anonymous=True, disable_signals=True)
    _pub = rospy.Publisher("/controller/init", String, queue_size=1, latch=True)
    _ready = True

@router.post("/api/controller/init")
def controller_init(
    excel_path: str = Form(...),
    stl_path: str | None = Form(None),
    typeselection: str | None = Form(None),
    expected_walls: str | None = Form(None),  # e.g. "1,2,3,4,F"
):
    try:
        _ensure_ros()
        walls = None
        if expected_walls:
            walls = [w.strip() for w in expected_walls.split(",") if w.strip()]
        payload = {
            "excel_path": excel_path,
            "stl_path": stl_path,
            "typeselection": typeselection,
            "expected_walls": walls,
        }
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        _pub.publish(msg)
        return {"ok": True, "published": payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish init: {e}")
