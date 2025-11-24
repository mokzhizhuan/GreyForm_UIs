# backend/marking.py

from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import List, Dict, Any
import time

from backend.runner import Runner

# This is its own FastAPI app
app = FastAPI(title="MarkingApp")

# Shared runner instance for this app
_runner = Runner()

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
@app.post("/start")
def start_marking(walls: List[Dict[str, Any]]):
    r = _runner_instance()

    if not r.listener_started:
        raise HTTPException(status_code=400, detail="Listener not started.")

    # reset state
    r.pending_walls = [w.copy() for w in walls]
    r.current_wall = None
    r.current_rows = []
    r.is_paused = False

    return {
        "ok": True,
        "queued_walls": len(r.pending_walls),
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
