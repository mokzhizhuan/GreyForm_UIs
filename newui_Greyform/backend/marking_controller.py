# backend/marking_controller.py
# FINAL VERSION — WALL 1 FIXED, NO SKIPPING WALL 4 OR 1

import subprocess
import threading
import re
import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# -------------------------------------------------------------------
# GLOBAL STATE
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
current_phase: Optional[int] = None

state_lock = threading.Lock()
event_counter = 0   # debug event marker


# -------------------------------------------------------------------
# MODELS
# -------------------------------------------------------------------
class WallPayload(BaseModel):
    wall: int
    rows: list  # The UI does not use this, but we keep for future use


class MarkingStartBody(BaseModel):
    walls: List[WallPayload]
    excelfile: str
    meshfile: str
    max_wall: int
    phase: Optional[int] = None


# -------------------------------------------------------------------
# READER THREAD — Detect wall completion
# -------------------------------------------------------------------
def reader_thread(proc: subprocess.Popen, wall_id: int):
    """
    Reads all stdout, detects completion, and ensures the UI receives:
        startedWall == doneWall == wall_id
    before continuing to the next wall.
    """
    global last_completed_wall, current_process, event_counter

    detected = False

    try:
        # Read live output
        if proc.stdout:
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                print(line)

                # Universal "wall x" detection
                m = re.search(r"wall\D*(\d+)", line, re.IGNORECASE)
                if m:
                    finished = int(m.group(1))
                    print(f"[controller] ✔ Detected completion of wall {finished}")
                    with state_lock:
                        last_completed_wall = finished
                        event_counter += 1
                    detected = True

        proc.wait()
        rc = proc.returncode
        print(f"[controller] Process exited RC={rc}")

        # If script exited cleanly but we never saw completion text
        if rc == 0 and not detected:
            print(f"[controller] ⭐ Auto-marking wall {wall_id} as completed")
            with state_lock:
                last_completed_wall = wall_id
                event_counter += 1

    finally:
        # Mark process finished
        with state_lock:
            current_process = None
            running_flag.clear()
            # KEEP current_wall AS THE FINISHED WALL
            # So UI sees startedWall == doneWall for a few seconds

        # Give React a stable window of 3 seconds for polling
        time.sleep(3.0)

        _maybe_start_next_wall_after_finish()


# -------------------------------------------------------------------
# DECIDE NEXT WALL
# -------------------------------------------------------------------
def _maybe_start_next_wall_after_finish():
    with state_lock:
        print(f"[DEBUG] maybe_start_next: paused={pause_flag.is_set()}, queue={wall_queue}, phase={current_phase}")

        if pause_flag.is_set():
            print("[controller] ⏸ Paused — stop scheduling next wall")
            return

        if not wall_queue:
            print("[controller] 🎉 All walls completed for this phase")
            return

    start_next_wall()


# -------------------------------------------------------------------
# START NEXT WALL
# -------------------------------------------------------------------
def start_next_wall():
    global current_wall, current_process, last_completed_wall

    with state_lock:
        if pause_flag.is_set():
            print("[controller] ⏸ Paused — abort start_next_wall()")
            return

        if not wall_queue:
            print("[controller] No more walls")
            current_wall = None
            return

        wall_id = wall_queue.pop(0)

        print(f"[DEBUG] Starting next wall → {wall_id}, remaining queue={wall_queue}")

        # Reset completion flag
        last_completed_wall = None

        current_wall = wall_id
        running_flag.set()

        if not excel_file_path or not mesh_file_path:
            raise RuntimeError("Excel or mesh path not set!")

        cmd = [
            "sshpass", "-p", "winsys",
            "ssh", "winsys@192.168.130.5",
            "/home/winsys/pbu_marking_ros/run_marking.sh",
            "--stage", "2",
            "--wall", str(wall_id),
            "--excel", excel_file_path,
            "--mesh", mesh_file_path,
        ]

        print(f"\n[controller] 🚀 Running wall {wall_id}")
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
            raise RuntimeError(f"Failed to run remote marking script: {e}")

        current_process = proc

    # Spawn reader thread
    threading.Thread(
        target=reader_thread,
        args=(proc, wall_id),
        daemon=True,
    ).start()


# -------------------------------------------------------------------
# PAUSE / RESUME
# -------------------------------------------------------------------
def pause_marking():
    pause_flag.set()
    print("[controller] ⏸ Pause after current wall requested")


def resume_marking():
    pause_flag.clear()
    print("[controller] ▶ Resume requested")

    with state_lock:
        should_start = (current_process is None) and bool(wall_queue)

    if should_start:
        start_next_wall()


# -------------------------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------------------------
@app.post("/start")
def marking_start(body: MarkingStartBody):
    """
    UI sends:
        walls: [{ wall:2 }, { wall:3 }, { wall:4 }]
        phase: 1 or 2
        excelfile: ...
        meshfile: ...
        max_wall: 6
    """
    global wall_queue, excel_file_path, mesh_file_path
    global last_completed_wall, current_wall, current_process
    global current_phase, total_walls, event_counter

    if not body.walls:
        raise HTTPException(400, "walls cannot be empty")

    with state_lock:
        if running_flag.is_set() and current_process:
            raise HTTPException(400, "Marking already in progress")

        # 💥 ABSOLUTELY ENSURE WALL 1 IS INCLUDED IF UI SENDS IT
        wall_queue = []
        for w in body.walls:
            if isinstance(w.wall, int):
                wall_queue.append(w.wall)
            else:
                print("[controller] ⚠ INVALID WALL PAYLOAD:", w)

        print(f"[DEBUG] Final wall_queue from UI:", wall_queue)

        total_walls = body.max_wall
        excel_file_path = body.excelfile
        mesh_file_path = body.meshfile
        current_phase = body.phase

        last_completed_wall = None
        current_wall = None
        current_process = None
        pause_flag.clear()
        running_flag.clear()

        event_counter += 1  # identifier for UI

        print("\n========================================")
        print("[controller] NEW MARKING SEQUENCE")
        print("Phase:", current_phase)
        print("Queue:", wall_queue)
        print("ExcelFile:", excel_file_path)
        print("MeshFile:", mesh_file_path)
        print("========================================\n")

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
def marking_resume_api():
    resume_marking()
    return {"resumed": True}


@app.get("/status")
def marking_status():
    with state_lock:
        print(f"[DEBUG STATUS] startedWall={current_wall}, doneWall={last_completed_wall}, queue={wall_queue}, phase={current_phase}")

        return {
            "running": running_flag.is_set(),
            "paused": pause_flag.is_set(),

            "startedWall": current_wall,
            "doneWall": last_completed_wall,

            "queue": list(wall_queue),
            "phase": current_phase,
            "maxWalls": total_walls,

            "excelFile": excel_file_path,
            "meshFile": mesh_file_path,

            "eventID": event_counter,
        }
