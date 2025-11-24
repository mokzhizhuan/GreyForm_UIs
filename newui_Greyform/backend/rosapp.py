# backend/rosapp.py

import os
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

# -----------------------------------------------------
# Pydantic Schemas
# -----------------------------------------------------

class FileExecBody(BaseModel):
    directory: str
    excelfile: str


class WallInfo(BaseModel):
    wall: str
    count: int


class FileExecResponse(BaseModel):
    ok: bool
    working_path: str
    walls: List[WallInfo]


# -----------------------------------------------------
# FastAPI Sub-App for ROS
# -----------------------------------------------------
app = FastAPI(title="ROS Subsystem")


_runner: Optional[ListenerNodeRunner] = None


def _runner_instance() -> ListenerNodeRunner:
    global _runner
    if _runner is None:
        _runner = ListenerNodeRunner(status_cb=lambda m: print("[ROS]", m))
    return _runner


# -----------------------------------------------------
# API ROUTES
# -----------------------------------------------------

@app.post("/listener/start")
def start_listener(restart: bool = False):
    r = _runner_instance()

    if restart:
        r.stop_listener_node()

    if not r.listener_started:
        r.run_listener_node()
        return {"ok": True, "message": "Listener starting"}

    return {"ok": True, "message": "Listener already running"}


@app.post("/listener/stop")
def stop_listener():
    r = _runner_instance()
    r.stop_listener_node()
    return {"ok": True, "message": "Listener stopped"}


# =======================================================
#   FILE EXECUTION - create working Excel & count walls
# =======================================================

@app.post("/file_execute_data", response_model=FileExecResponse)
def file_execute_data(body: FileExecBody):
    r = _runner_instance()

    if not r.listener_started:
        raise HTTPException(400, "Listener not started. Call /listener/start first.")

    try:
        working_path = r.file_selection_data(body.directory, body.excelfile)
        r.last_working_path = working_path
    except Exception as e:
        raise HTTPException(500, f"file_selection_data failed: {e}")

    walls_list: List[WallInfo] = []
    wall_rows_map: Dict[str, List[Dict[str, Any]]] = {}

    try:
        xl = pd.read_excel(working_path, sheet_name=None)

        for df in xl.values():
            if not isinstance(df, pd.DataFrame):
                continue

            df = df.copy()
            df.columns = [str(c).strip() for c in df.columns]

            if "Wall Number" not in df.columns:
                continue

            for _, row in df.iterrows():
                wall = str(row["Wall Number"])
                wall_rows_map.setdefault(wall, []).append(row.to_dict())

        r.wall_rows_map = wall_rows_map

        for wall_key, rows in sorted(wall_rows_map.items(), key=lambda kv: kv[0]):
            walls_list.append(WallInfo(wall=wall_key, count=len(rows)))

    except Exception as e:
        print("Excel parsing failed:", e)

    return FileExecResponse(
        ok=True,
        working_path=working_path,
        walls=walls_list,
    )


# =======================================================
# EXECUTE WALL DATA (Marking)
# =======================================================

@app.post("/execute_wall_data")
def execute_wall_data(
    rows: List[Dict[str, Any]],
    background: BackgroundTasks
):
    r = _runner_instance()
    if not r.listener_started:
        return {"ok": False, "error": "Listener not started. Call /listener/start first."}

    background.add_task(r.run_execution_data, rows)
    return {"ok": True, "queued": True}


@app.get("/status")
def status():
    return {"listener_started": _runner_instance().listener_started}

