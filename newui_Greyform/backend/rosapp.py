# backend/rosapp.py
from fastapi import FastAPI, BackgroundTasks
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from processlistenerrunner import ListenerNodeRunner

app = FastAPI(title="ROS API")
_runner: Optional[ListenerNodeRunner] = None


def _runner_instance():
    global _runner
    if _runner is None:
        _runner = ListenerNodeRunner(status_cb=lambda m: print(m, flush=True))
    return _runner


@app.post("/listener/start")
def start_listener(restart: bool = False):
    r = _runner_instance()
    if restart and r.process:
        r.stop_listener_node()
        r.listener_started = False
    if not r.listener_started:
        r.run_listener_node()
        return {"ok": True, "message": "Listener starting"}
    return {"ok": True, "message": "Listener already running"}


class FileExecBody(BaseModel):
    directory: str
    excel_path: str


@app.post("/file_execute_data")
def file_execute_data(body: FileExecBody, background: BackgroundTasks):
    r = _runner_instance()
    if not r.listener_started:
        return {
            "ok": False,
            "error": "Listener not started. Call /ros/listener/start first.",
        }

    def job():
        r.file_selection_data(body.directory, body.excel_path)

    background.add_task(job)
    return {"ok": True, "queued": True}


@app.post("/execute_wall_data")
def execute_wall_data(rows: List[Dict[str, Any]], background: BackgroundTasks):
    r = _runner_instance()
    if not r.listener_started:
        return {
            "ok": False,
            "error": "Listener not started. Call /ros/listener/start first.",
        }

    def job():
        r.run_execution_data(rows)

    background.add_task(job)
    return {"ok": True, "queued": True}
