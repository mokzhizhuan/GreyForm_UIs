# backend/marking.py

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time

import rospy  # safe to import; we don't call init_node here

from backend.runner import Runner
from roscore_service import is_master_up

# --------------------------------------------------------
# FastAPI app
# --------------------------------------------------------
app = FastAPI(title="MarkingApp")

# --------------------------------------------------------
# Shared Runner, but DO NOT create ROS talker at import time
# --------------------------------------------------------
_runner = Runner()
_talker_initialized = False  # track if we've bound the ROS talker yet


def _runner_instance() -> Runner:
    return _runner


def _ensure_talker():
    """
    Lazily create and bind the ROS talker only when:
      - ROS master is up
      - We actually need to talk to ROS
    """
    global _talker_initialized

    if _talker_initialized:
        return

    if not is_master_up():
        raise HTTPException(status_code=400, detail="ROS core not running")

    # Import here so we don't trigger rospy.init_node at module import
    from src.talker_listener.talker_listener import talker_node as RosPublisher

    _runner.bind_talker(RosPublisher.TalkerNode())
    _talker_initialized = True


# --------------------------------------------------------
# Internal: execute all queued walls
# --------------------------------------------------------
def _execute_all_walls(r: Runner) -> None:
    while r.pending_walls:

        # CHECK BEFORE STARTING NEXT WALL
        if r.is_paused:
            break

        wall_block = r.pending_walls.pop(0)
        r.current_wall = int(wall_block["wall"])
        r.current_rows = wall_block["rows"]

        # PROCESS ALL ROWS
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

            time.sleep(0.06)

        # WALL COMPLETED
        if (not r.is_paused) and r.talker_node:
            r.talker_node.publish_all_done(True)

        # NEW IMPORTANT CHECK HERE!!!
        # 🔥 Stop immediately AFTER finishing current wall if paused
        if r.is_paused:
            break

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
# START marking: build sequence, send Excel path to listener,
# but DO NOT start execution yet (that's /run).
# --------------------------------------------------------
@app.post("/start")
def start_marking(body: StartMarkingBody):
    r = _runner_instance()

    # Ensure ROS master is up + talker bound
    _ensure_talker()

    if not r.listener_started:
        raise HTTPException(status_code=400, detail="Listener not started")

    # 1) Tell listener which Excel to use BEFORE any selection messages
    try:
        if r.talker_node:
            # directory is ignored by your listener_node; we just send excelfile
            r.talker_node.publish_file_message("", body.excelfile)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send Excel file path to listener: {e}",
        )

    # 2) Build pending wall sequence
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
                raise HTTPException(
                    status_code=400, detail="Invalid phase for 6-wall flow"
                )

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

    # Ensure ROS + talker
    _ensure_talker()

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
        "pendingCount": len(r.pending_walls),
    }


# --------------------------------------------------------
# CONTINUE marking (next wall onwards)
# --------------------------------------------------------
@app.post("/continue")
def continue_marking(background: BackgroundTasks):
    r = _runner_instance()
    _ensure_talker()

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

    if not is_master_up():
        # ROS not up → don't call rospy.get_param at all
        return {
            "ros_up": False,
            "currentWall": r.current_wall,
            "paused": r.is_paused,
            "pendingCount": len(r.pending_walls),
            "startedWall": None,
            "doneWall": None,
        }

    # ROS is up; safe to query params
    try:
        last_started = rospy.get_param("/ui_last_started_wall", None)
        last_done = rospy.get_param("/ui_last_done_wall", None)
    except Exception:
        last_started = None
        last_done = None

    return {
        "ros_up": True,
        "currentWall": r.current_wall,
        "paused": r.is_paused,
        "pendingCount": len(r.pending_walls),
        "startedWall": last_started,
        "doneWall": last_done,
    }
