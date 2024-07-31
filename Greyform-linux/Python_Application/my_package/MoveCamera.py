# MoveCamera.py

from typing import Optional
from typing_extensions import TypedDict
from geometry_msgs.msg import PointStamped
from std_msgs.msg import Bool

class MoveCamera_Goal(TypedDict):
    target: Optional[PointStamped]

class MoveCamera_Result(TypedDict):
    success: bool

class MoveCamera_Feedback(TypedDict):
    progress: float
