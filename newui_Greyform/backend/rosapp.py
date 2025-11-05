# backend/rosapp.py
from fastapi import FastAPI, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from processlistenerrunner import ListenerNodeRunner
from backend import placementcoord as placementcoord_json


app = FastAPI(title="ROS API")
_runner: Optional[ListenerNodeRunner] = None


def _runner_instance():
    global _runner
    if _runner is None:
        _runner = ListenerNodeRunner(file="", status_cb=lambda m: print(m, flush=True))
    return _runner


@app.post("/listener/start")
def start_listener(file: str = "", restart: bool = False):
    r = _runner_instance()
    if file:
        r.file = file
    if restart and r.process:
        r.stop_listener_node()
        r.listener_started = False
    if not r.listener_started:
        r.run_listener_node()
        return {"ok": True, "message": "Listener starting"}
    return {"ok": True, "message": "Listener already running"}


@app.post("/execute")
def execute(excel_path: str, rows: List[Dict[str, Any]], background: BackgroundTasks):
    r = _runner_instance()
    if not r.listener_started:
        return {
            "ok": False,
            "error": "Listener not started. Call /ros/listener/start first.",
        }

    def job():
        r.run_execution_data(rows, excel_path)

    background.add_task(job)
    return {"ok": True, "queued": True}


class JointValuesBody(BaseModel):
    jointvalues: Any = Field(
        ..., description="Single pose or list/sequence of joint frames"
    )
    json_path: str = Field(
        "wall_centerpoints.json", description="Path to the CP JSON file"
    )


@app.post("/api/getjoint_values")
def getjoint_values(req: JointValuesBody, background: BackgroundTasks):
    r = _runner_instance()
    json_path = "wall_centerpoints.json"
    if not r.listener_started:
        return {
            "ok": False,
            "error": "Listener not started. Call /ros/listener/start first.",
        }

    # Load placementcoord (first/last WallCP) from JSON
    try:
        placementcoord = placementcoord_json.placementcoord_from_json(json_path)
        if not placementcoord:
            return {
                "ok": False,
                "error": f"No CenterWallPoint found in {req.json_path} (need at least two).",
            }
    except FileNotFoundError:
        return {"ok": False, "error": f"JSON file not found: {req.json_path}"}
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to parse placementcoord from {req.json_path}: {e!r}",
        }

    # Queue the publishing job
    def job():
        r.run_jointvalues(req.jointvalues, placementcoord)

    background.add_task(job)
    return {"ok": True, "queued": True, "placementcoord": placementcoord}
