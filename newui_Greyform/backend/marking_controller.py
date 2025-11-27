# backend/marking_controller.py

import subprocess
import threading
import re
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# -------------------------------------------------------------------
# FastAPI App
# -------------------------------------------------------------------
app = FastAPI()

# -------------------------------------------------------------------
# Global State
# -------------------------------------------------------------------
pause_flag = threading.Event()
running_flag = threading.Event()

current_process: Optional[subprocess.Popen] = None
current_wall: Optional[int] = None
last_completed_wall: Optional[int] = None

wall_queue: List[int] = []
total_walls: int = 0

excel_file_path: str = ""
mesh_file_path: str = ""
current_phase: Optional[int] = None   # 1 or 2

state_lock = threading.Lock()

# -------------------------------------------------------------------
# Request Model
# -------------------------------------------------------------------
class MarkingStartBody(BaseModel):
    walls: List[int]           # e.g. [2,3,4] or [5,6,1]
    excelfile: str
    meshfile: str
    max_wall: int
    phase: Optional[int] = None   # 1 or 2


# -------------------------------------------------------------------
# Reader Thread — Detect wall completion
# -------------------------------------------------------------------
def reader_thread(proc: subprocess.Popen, wall_id: int):
    """
    Reads stdout from the remote process and detects completion.
    If no explicit 'wall X finished' text exists, but the process exits RC=0,
    we treat it as completion of wall_id.
    """
    global last_completed_wall, current_process

    detected = False  # whether regex found completion text

    try:
        if proc.stdout:
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                print(line)

                # Regex-based completion detection
                if ("wall" in line.lower() and
                    ("finish" in line.lower() or "done" in line.lower() or "complete" in line.lower())):

                    m = re.search(r"[Ww]all\s*(\d+)", line)
                    if m:
                        finished = int(m.group(1))
                        print(f"[controller] ✔ Detected completion of wall {finished}")

                        with state_lock:
                            last_completed_wall = finished
                        detected = True

        proc.wait()
        rc = proc.returncode
        print(f"[controller] Process exited RC={rc}")

        # ⭐ If RC=0 and no finish text was detected, mark completion manually
        if rc == 0 and not detected:
            print(f"[controller] ⭐ Auto-marking wall {wall_id} as completed (no finish text detected)")
            with state_lock:
                last_completed_wall = wall_id

    finally:
        with state_lock:
            current_process = None

        _maybe_start_next_wall_after_finish()



# -------------------------------------------------------------------
# Decide whether to start next wall after finishing
# -------------------------------------------------------------------
def _maybe_start_next_wall_after_finish():
    with state_lock:
        if pause_flag.is_set():
            print("[controller] ⏸ Paused — not starting next wall.")
            return

        if not wall_queue:
            print("[controller] ✅ All queued walls completed.")
            running_flag.clear()
            return

    start_next_wall()


# -------------------------------------------------------------------
# Start the next wall
# -------------------------------------------------------------------
def start_next_wall():
    global current_wall, current_process

    with state_lock:
        if pause_flag.is_set():
            print("[controller] ⏸ Paused — abort start_next_wall()")
            return

        if not wall_queue:
            print("[controller] No more walls to run.")
            running_flag.clear()
            current_wall = None
            return

        if not excel_file_path or not mesh_file_path:
            raise RuntimeError("Excel or mesh path not set!")

        wall_id = wall_queue.pop(0)
        current_wall = wall_id
        running_flag.set()

        cmd = [
            "sshpass", "-p", "winsys",
            "ssh", "winsys@192.168.130.5",
            "/home/winsys/pbu_marking_ros/run_marking.sh",
            "--stage", "1",
            "--wall", str(wall_id),
            "--excel", excel_file_path,
            "--mesh", mesh_file_path,
        ]

        print("\n[controller] 🚀 Starting Wall:", wall_id)
        print("[controller] CMD:", cmd, "\n")

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as e:
            running_flag.clear()
            current_wall = None
            raise RuntimeError(f"Failed to launch marking script: {e}")

        current_process = proc

    # Start listener thread
    threading.Thread(
        target=reader_thread,
        args=(proc, wall_id),
        daemon=True,
    ).start()


# -------------------------------------------------------------------
# Pause / Continue
# -------------------------------------------------------------------
def pause_marking():
    pause_flag.set()
    print("[controller] ⏸ Pause requested — will stop after current wall.")


def resume_marking():
    pause_flag.clear()
    print("[controller] ▶ Resume requested.")

    with state_lock:
        should_start = (current_process is None) and bool(wall_queue)

    if should_start:
        start_next_wall()


# -------------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------------
@app.post("/start")
def marking_start(body: MarkingStartBody):
    """
    Starts marking sequence for Phase 1 or Phase 2.
    """
    global wall_queue, total_walls, excel_file_path, mesh_file_path
    global last_completed_wall, current_wall, current_process, current_phase

    if not body.walls:
        raise HTTPException(status_code=400, detail="walls cannot be empty")

    with state_lock:
        if running_flag.is_set() and current_process:
            raise HTTPException(status_code=400, detail="Marking already in progress")

        wall_queue = list(body.walls)
        total_walls = body.max_wall
        excel_file_path = body.excelfile
        mesh_file_path = body.meshfile
        current_phase = body.phase

        last_completed_wall = None
        current_wall = None
        current_process = None

        pause_flag.clear()

        print(f"\n[controller] ===============================")
        print(f"[controller] New marking sequence started")
        print(f"[controller] Phase: {current_phase}")
        print(f"[controller] Queue: {wall_queue}")
        print(f"[controller] Excel: {excel_file_path}")
        print(f"[controller] Mesh:  {mesh_file_path}")
        print(f"[controller] ===============================\n")

    threading.Thread(target=start_next_wall, daemon=True).start()

    return {
        "ok": True,
        "queued": wall_queue,
        "phase": current_phase,
        "max_walls": total_walls,
    }


@app.post("/pause")
def marking_pause():
    pause_marking()
    return {"paused": True}


@app.post("/continue")
def marking_resume():
    resume_marking()
    return {"resumed": True}


@app.get("/status")
def marking_status():
    with state_lock:
        return {
            "running": running_flag.is_set(),
            "paused": pause_flag.is_set(),

            # What UI reads:
            "startedWall": current_wall,
            "doneWall": last_completed_wall,

            "queue": list(wall_queue),
            "phase": current_phase,
            "maxWalls": total_walls,

            "excelFile": excel_file_path,
            "meshFile": mesh_file_path,
        }
