# backend/runner.py

from typing import List, Dict, Any, Optional

class Runner:
    def __init__(self):
        # You can wire this to your real listener logic
        self.listener_started: bool = True

        # Your ROS talker node (set this from main if needed)
        self.talker_node = None

        # Marking flow state
        self.is_paused: bool = False
        self.current_wall: Optional[int] = None
        self.pending_walls: List[Dict[str, Any]] = []
        self.current_rows: List[Dict[str, Any]] = []

    def bind_talker(self, talker) -> None:
        self.talker_node = talker
