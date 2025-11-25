# backend/marking.py

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import rospy
from backend.runner import Runner
from roscore_service import is_master_up
from src.talker_listener.talker_listener import talker_node as RosPublisher

# --------------------------------------------------------
# FastAPI app
# --------------------------------------------------------
app = FastAPI(title="MarkingApp")

# --------------------------------------------------------
# Shared Runner + bind existing ROS talker instance
# --------------------------------------------------------
# NOTE: RosPublisher is already a TalkerNode instance imported
# from src.talker_listener.talker_listener. We DO NOT create
# a new instance here; we just bind it to the Runner.
_runner = Runner()
_runner.bind_talker(RosPublisher.TalkerNode())


def _runner_instance() -> Runner:
    return _runner


# --------------------------------------------------------
# Internal: execute all queued walls
# --------------------------------------------------------
def _execute_all_walls(r: Runner) -> None:
    """
    Process r.pending_walls in order.

    Each entry in r.pending_walls is expected to be:
      { "wall": "1", "rows": [ {...}, ... ] }

    We publish SelectionWall for every row, then publish_all_done(True)
    after each wall finishes (unless paused between walls).
    """
    while r.pending_walls:

        # Pause applies BEFORE starting the next wall
        if r.is_paused:
            break

        wall_block = r.pending_walls.pop(0)
        r.current_wall = int(wall_block["wall"])
        r.current_rows = wall_block["rows"]

        for row in r.current_rows:
            pos = [
                int(float(row.get("Position X", 0))),
                int(float(row.get("Position Y", 0))),
                int(float(row.get("Position Z", 0))),
            ]
            marking_type = row.get("Marking Type")

            if r.talker_node:
                r.talker_node.publish_selection_message(
                    r.current_wall,
                    pos,
                    marking_type,
                )

            # Small delay to avoid hammering ROS / hardware
            time.sleep(0.06)

        # Wall finished; tell UI/ROS this wall is done
        if (not r.is_paused) and r.talker_node:
            r.talker_node.publish_all_done(True)

    # Clear current rows when done (or paused)
    r.current_rows = []


# --------------------------------------------------------
# Request Body
# --------------------------------------------------------
class StartMarkingBody(BaseModel):
    walls: List[Dict[str, Any]]  # wall blocks from React
    max_wall: int                # 4 or 6
    phase: Optional[int] = None  # only used for 6-wall
    excelfile: str               # full path to working Excel


# --------------------------------------------------------
# START marking
# --------------------------------------------------------
@app.post("/start")
def start_marking(body: StartMarkingBody):
    r = _runner_instance()

    # Safety checks
    if not is_master_up():
        raise HTTPException(status_code=400, detail="ROS core not running")

    if not r.listener_started:
        raise HTTPException(status_code=400, detail="Listener not started")

    # 🔥 1) Tell listener which Excel to use BEFORE any selection messages
    try:
        # directory is ignored by your new listener_node; we just send excelfile
        if r.talker_node:
            r.talker_node.publish_file_message("", body.excelfile)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send Excel file path to listener: {e}",
        )

    # 🔥 2) Build pending wall sequence
    walls = body.walls
    max_wall = body.max_wall
    phase = body.phase

    # -------- 4 WALL FLOW (no phase logic) --------
    if max_wall == 4:
        # Use whatever order came from Excel/UI
        pending = walls[:]

    # -------- 6 WALL FLOW (optional two phases) --------
    elif max_wall == 6:
        if phase is None:
            # Full automatic: run all walls in the order sent from UI
            pending = walls[:]
        else:
            # Phase 1 → walls 2,3,4
            # Phase 2 → walls 5,6,1
            if phase == 1:
                order = ["2", "3", "4"]
            elif phase == 2:
                order = ["5", "6", "1"]
            else:
                raise HTTPException(status_code=400, detail="Invalid phase for 6-wall flow")

            # Filter to matching walls
            pending = [w for w in walls if str(w.get("wall")) in order]

            # Sort in strict [2,3,4] or [5,6,1] sequence
            order_index = {wid: i for i, wid in enumerate(order)}
            pending.sort(key=lambda w: order_index[str(w["wall"])])

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported max_wall={max_wall}")

    # Store on runner
    r.pending_walls = [w.copy() for w in pending]
    r.current_wall = None
    r.current_rows = []
    r.is_paused = False

    return {
        "ok": True,
        "phase": phase,
        "queued_walls": [w["wall"] for w in pending],
    }


# --------------------------------------------------------
# RUN marking (background task)
# --------------------------------------------------------
@app.post("/run")
def run_marking(background: BackgroundTasks):
    r = _runner_instance()

    if not r.listener_started:
        raise HTTPException(status_code=400, detail="Listener not started")

    def job():
        _execute_all_walls(r)

    background.add_task(job)
    return {"ok": True, "started": True}


# --------------------------------------------------------
# PAUSE marking (after current wall)
# --------------------------------------------------------
@app.post("/pause")
def pause_marking():
    r = _runner_instance()
    r.is_paused = True
    return {
        "ok": True,
        "paused": True,
        "current_wall": r.current_wall,
    }


# --------------------------------------------------------
# CONTINUE marking (next wall onwards)
# --------------------------------------------------------
@app.post("/continue")
def continue_marking(background: BackgroundTasks):
    r = _runner_instance()
    r.is_paused = False

    def job():
        _execute_all_walls(r)

    background.add_task(job)
    return {
        "ok": True,
        "resumed": True,
    }


# --------------------------------------------------------
# STATUS for React polling
# --------------------------------------------------------
@app.get("/status")
def marking_status():
    r = _runner_instance()
    last_started = rospy.get_param("/ui_last_started_wall", None)
    last_done = rospy.get_param("/ui_last_done_wall", None)

    return {
        "currentWall": r.current_wall,
        "paused": r.is_paused,
        "pendingCount": len(r.pending_walls),
        "startedWall": last_started,
        "doneWall": last_done,
    }

