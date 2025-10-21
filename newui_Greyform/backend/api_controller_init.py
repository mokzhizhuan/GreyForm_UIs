# api_controller_init.py
import json
import rospy
from fastapi import APIRouter, Form, HTTPException
from std_msgs.msg import RosString

router = APIRouter()
_pub = None
_ready = False

_ctrl_ready = False
_ctrl_pub = None
_state_lock = threading.Lock()

def _ensure_ctrl_pub():
    global _ctrl_ready, _ctrl_pub
    if _ctrl_ready:
        return
    # one ROS node in this process; disable signals so FastAPI keeps running
    rospy.init_node("http_controller_init_bridge", anonymous=True, disable_signals=True)
    _ctrl_pub = rospy.Publisher("/controller/init", RosString, queue_size=1, latch=True)
    _ctrl_ready = True

    
def _ensure_ros():
    """Initialize one ROS node for HTTP bridge and a latched /controller/init publisher."""
    global _ros_ready, _ctrl_pub
    if _ros_ready:
        return
    rospy.init_node("http_controller_init_bridge", anonymous=True, disable_signals=True)
    _ctrl_pub = rospy.Publisher("/controller/init", RosString, queue_size=1, latch=True)
    _ros_ready = True

def _compute_walls(model_sides: int, include_floor: bool, explicit_csv: Optional[str]) -> List[str]:
    """Return a list of walls either from explicit CSV or derived from model_sides (+optional floor)."""
    if explicit_csv and explicit_csv.strip():
        return [w.strip() for w in explicit_csv.split(",") if w.strip()]
    if model_sides not in (4, 6):
        raise ValueError("model_sides must be 4 or 6")
    walls = [str(i) for i in range(1, model_sides + 1)]
    if include_floor:
        walls.append("F")
    return walls

@router.post("/api/controller/init")
def controller_init(
    excel_path: str = Form(...),
    model_sides: int = Form(...),
    stl_path: Optional[str] = Form(None),
    typeselection: Optional[str] = Form(None),
    expected_walls: Optional[str] = Form(None),   # e.g. "1,2,3,4,F"
):
    _ensure_ros()

    # If explicit list provided, use it; else derive from model_sides only
    if expected_walls and expected_walls.strip():
        walls = [w.strip() for w in expected_walls.split(",") if w.strip()]
    else:
        walls = [str(i) for i in range(1, model_sides + 1)]

    payload = {
        "excel_path": excel_path,
        "stl_path": stl_path,
        "typeselection": typeselection,
        "expected_walls": walls,
        "model_sides": int(model_sides),
    }
    msg = RosString()
    msg.data = json.dumps(payload, ensure_ascii=False)
    _ctrl_pub.publish(msg)
    return {"ok": True, "published": payload}
