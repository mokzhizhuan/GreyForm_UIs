# backend/rosapp.py
from fastapi import FastAPI, BackgroundTasks
from typing import List, Dict, Any, Optional
from processlistenerrunner import ListenerNodeRunner

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
    if file: r.file = file
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
        return {"ok": False, "error": "Listener not started. Call /ros/listener/start first."}
    def job(): r.run_execution_data(rows, excel_path)
    background.add_task(job)
    return {"ok": True, "queued": True}

@app.post("api/getjoint_values")
def getjoint_values(jointvalues , placementcoord, background: BackgroundTasks):
    r = _runner_instance()
    if not r.listener_started:
        return {"ok": False, "error": "Listener not started. Call /ros/listener/start first."}
    def jobs(): r.run_jointvalues(jointvalues, placementcoord)
    background.add_task(jobs)
    return {"ok": True, "queued": True}    
