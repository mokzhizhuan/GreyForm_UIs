# backend/marking.py

from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import List, Dict, Any
import time
from src.talker_listener.talker_listener import talker_node as RosPublisher
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from roscore_service import (
    ROS_MASTER_URI,
    is_master_up,
    start_roscore,
    stop_roscore,
    _OWNED,
)

from backend.runner import Runner

# This is its own FastAPI app
app = FastAPI(title="MarkingApp")

# Shared runner instance for this app
_runner = Runner()
_runner.bind_talker(RosPublisher)


def _runner_instance() -> Runner:
    return _runner


# ------------------------------------------------------
# INTERNAL: execute all walls sequentially
# ------------------------------------------------------
def _execute_all_walls(r: Runner) -> None:
    while r.pending_walls:

        # Pause requested? stop processing further walls
        if r.is_paused:
            break

        wall_block = r.pending_walls.pop(0)

        # e.g. wall_block = { "wall": "1", "rows": [ {...}, ... ] }
        r.current_wall = int(wall_block["wall"])
        r.current_rows = wall_block["rows"]

        # ----- Execute this wall's rows -----
        for row in r.current_rows:
            if r.is_paused:
                # stop mid-wall; current wall ends after this point loop
                break

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

            # small delay to avoid hammering hardware
            time.sleep(0.05)

        # ----- Wall finished -----
        if (not r.is_paused) and r.talker_node:
            r.talker_node.publish_all_done(True)

    # clear rows when done or paused
    r.current_rows = []


# ------------------------------------------------------
# API: receive all walls & queue them
# Body example:
# [
#   { "wall": "1", "rows": [ {...}, {...} ] },
#   { "wall": "2", "rows": [ {...}, {...} ] }
# ]
# ------------------------------------------------------
class StartMarkingBody(BaseModel):
    walls: List[Dict[str, Any]]   # full walls array from React
    max_wall: int                 # 4 or 6
    phase: Optional[int] = None   # only used for 6-wall


@app.post("/start")
def start_marking(body: StartMarkingBody):
    r = _runner_instance()

    if not is_master_up():
        raise HTTPException(status_code=400, detail="ROS core not running")

    if not r.listener_started:
        raise HTTPException(status_code=400, detail="Listener not started.")

    walls = body.walls
    max_wall = body.max_wall
    phase = body.phase

    # ---------- 4-wall: NO phase, always run walls as given ----------
    if max_wall == 4:
        pending = walls[:]   # just take whatever order came from Excel / UI

    # ---------- 6-wall: optional phase ----------
    elif max_wall == 6:
        # If no phase → run everything in the order given
        if phase is None:
            pending = walls[:]
        else:
            # Phase logic for 6-wall:
            # phase 1: walls 2,3,4
            # phase 2: walls 5,6,1
            if phase == 1:
                pending_ids = ["2", "3", "4"]
            elif phase == 2:
                pending_ids = ["5", "6", "1"]
            else:
                raise HTTPException(status_code=400, detail="Invalid phase for 6-wall")

            # Filter only matching walls
            pending = [w for w in walls if str(w.get("wall")) in pending_ids]

            # Sort in the exact [2,3,4] or [5,6,1] order
            id_index = {wid: i for i, wid in enumerate(pending_ids)}
            pending.sort(key=lambda w: id_index[str(w["wall"])])

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported max_wall: {max_wall}")

    # Store in runner
    r.pending_walls = [w.copy() for w in pending]
    r.current_wall = None
    r.current_rows = []
    r.is_paused = False

    return {
        "ok": True,
        "phase": phase,
        "queued_walls": len(r.pending_walls),
        "pending_ids": [w["wall"] for w in pending],
    }


# ------------------------------------------------------
# API: run (wall1 → wall2 → wall3)
# ------------------------------------------------------
@app.post("/run")
def run_marking(background: BackgroundTasks):
    r = _runner_instance()

    if not r.listener_started:
        raise HTTPException(status_code=400, detail="Listener not started.")

    def job():
        _execute_all_walls(r)

    background.add_task(job)
    return {"ok": True, "started": True}


# ------------------------------------------------------
# API: pause — finish current wall then stop
# ------------------------------------------------------
@app.post("/pause")
def pause_marking():
    r = _runner_instance()
    r.is_paused = True
    return {
        "ok": True,
        "paused": True,
        "current_wall": r.current_wall,
    }


# ------------------------------------------------------
# API: continue — resume from next wall
# ------------------------------------------------------
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


# ------------------------------------------------------
# API: status — for React polling
# ------------------------------------------------------
@app.get("/status")
def marking_status():
    r = _runner_instance()
    return {
        "currentWall": r.current_wall,
        "paused": r.is_paused,
        "pendingCount": len(r.pending_walls),
    }
