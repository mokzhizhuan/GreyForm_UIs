# backend/runner.py

from typing import List, Dict, Any, Optional

class Runner:
    def __init__(self):
        # Listener starts automatically (mock)
        self.listener_started: bool = True

        # Talker node instance
        self.talker_node = None

        # Marking state
        self.is_paused: bool = False
        self.current_wall: Optional[int] = None
        self.pending_walls: List[Dict[str, Any]] = []
        self.current_rows: List[Dict[str, Any]] = []

        # Track wall progress
        self.rows_processed_in_current_wall: int = 0   # ⭐ NEW ⭐

        # Optional debug tracking
        self.last_started_wall = None
        self.last_done_wall = None

    def bind_talker(self, talker) -> None:
        self.talker_node = talker
