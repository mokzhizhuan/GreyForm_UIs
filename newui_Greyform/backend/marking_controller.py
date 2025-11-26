# backend/marking_app.py
from fastapi import FastAPI, HTTPException
import subprocess
import threading
from typing import List, Optional

app = FastAPI()

pause_flag = threading.Event()
running_flag = threading.Event()

current_process: Optional[subprocess.Popen] = None
current_wall: Optional[int] = None
wall_queue: List[int] = []

total_walls: int = 0
excel_file_path: Optional[str] = None   # <--- NEW


def start_next_wall():
    """Start the next wall in the queue, unless paused."""
    global current_process, current_wall

    if pause_flag.is_set():
        print("Paused — not starting next wall.")
        return

    if not wall_queue:
        print("All walls completed.")
        current_wall = None
        return

    if not excel_file_path:
        print("No excel_file_path set, cannot start wall.")
        return

    current_wall = wall_queue.pop(0)
    print(f"Starting wall {current_wall} with Excel '{excel_file_path}'")

    running_flag.set()

    # ⬇⬇⬇ Excel file included as last argument ⬇⬇⬇
    current_process = subprocess.Popen(
        [
            "./run-marking.sh",
            "--pbu", "1",
            "--wall", str(current_wall),
            excel_file_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    threading.Thread(
        target=reader_thread,
        args=(current_process,),
        daemon=True,
    ).start()


def reader_thread(proc: subprocess.Popen):
    for line in proc.stdout:
        print(line.rstrip())

    proc.wait()
    running_flag.clear()
    print(f"Wall {current_wall} finished.")
    start_next_wall()


def start_marking_sequence(walls: List[int], excel_file: str):
    """Initialize queue and kick off first wall."""
    global total_walls, excel_file_path

    print("Starting marking sequence:", walls, "Excel:", excel_file)
    wall_queue.clear()
    wall_queue.extend(walls)

    total_walls = len(walls)
    excel_file_path = excel_file          # <--- store once

    pause_flag.clear()
    running_flag.clear()

    start_next_wall()


def pause_marking():
    print("Pause requested.")
    pause_flag.set()


def resume_marking():
    print("Resume requested.")
    pause_flag.clear()
    if not running_flag.is_set():
        start_next_wall()


@app.post("/marking/start")
def marking_start(body: dict):
    """
    BODY example from React:
    {
      "excel_file": "/path/to/working.xlsx",
      "walls": [
        { "wall": "1", "count": 21, "rows": [...] },
        { "wall": "2", "count": 9,  "rows": [...] },
        ...
      ]
    }
    """
    walls_payload = body.get("walls")
    excel_file = body.get("excel_file")

    if not walls_payload:
        raise HTTPException(status_code=400, detail="No 'walls' array provided")

    if not excel_file:
        raise HTTPException(status_code=400, detail="No 'excel_file' provided")

    try:
        wall_ids = sorted({int(item["wall"]) for item in walls_payload})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid walls payload: {e}")

    if not wall_ids:
        raise HTTPException(status_code=400, detail="No valid wall ids found")

    start_marking_sequence(wall_ids, excel_file)

    return {
        "ok": True,
        "message": "Started marking sequence",
        "walls": wall_ids,
        "max_walls": len(wall_ids),
        "excel_file": excel_file,
    }


@app.post("/marking/pause")
def marking_pause():
    pause_marking()
    return {"ok": True, "status": "paused"}


@app.post("/marking/resume")
def marking_resume():
    resume_marking()
    return {"ok": True, "status": "resumed"}


@app.get("/marking/status")
def marking_status():
    return {
        "running": running_flag.is_set(),
        "paused": pause_flag.is_set(),
        "current_wall": current_wall,
        "queue": wall_queue,
        "max_walls": total_walls,
        "excel_file": excel_file_path,
    }
