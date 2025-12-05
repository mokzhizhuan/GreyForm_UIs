# backend/marking_controller.py
# FINAL VERSION — STRING WALL LABELS + ROBOT ROW COUNTER (Option B)
# HOME POSITION CHECK SEPARATE API
# NOW WITH 5-SECOND FALLBACK COUNTER INSIDE /status

import subprocess
import threading
import re
import time
import os
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

wall_queue: List[str] = []
total_walls: int = 0

excel_file_path: str = ""
mesh_file_path: str = ""
current_phase: Optional[int] = None
current_folder: str = ""

state_lock = threading.Lock()
event_counter = 0

# row counter from robot output
wall_line_count = {}   # {2: 0, 3: 5, ...}

# NEW: fallback counter timestamps
fallback_counter = {}  # {2: last_timestamp}


# -------------------------------------------------------------------
# MODELS
# -------------------------------------------------------------------
class WallPayload(BaseModel):
    wall: str
    rows: list


class MarkingStartBody(BaseModel):
    walls: List[WallPayload]
    excelfile: str
    meshfile: str
    max_wall: int
    folder: str
    phase: Optional[int] = None


class HomeCheckBody(BaseModel):
    phase: int


# -------------------------------------------------------------------
# /homecheck — SEPARATE API
# -------------------------------------------------------------------
@app.post("/homecheck")
def home_position_check(body: HomeCheckBody):
    target = f"wall_{body.phase}"

    cmd = [
        "sshpass", "-p", "winsys",
        "ssh", "winsys@192.168.130.5",
        "python3",
        "/home/winsys/pbu_marking_ros/homeposcheck.py",
        "--file", "/home/winsys/pbu_marking_ros/pbu_data/mockup/poses.json",
        "--target", target,
    ]

    print(f"[HomeCheck] Running command:", cmd)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        out, _ = proc.communicate()

        print("[HomeCheck Output]")
        print(out)

        if proc.returncode != 0:
            raise HTTPException(400, "Home position check FAILED!")

        return {
            "ok": True,
            "target": target,
            "output": out,
        }

    except Exception as e:
        raise HTTPException(500, f"HomePosCheck error: {str(e)}")


# -------------------------------------------------------------------
# READER THREAD — READ ROWS FROM ROBOT SCRIPT
# -------------------------------------------------------------------
def reader_thread(proc: subprocess.Popen, wall_id: int):
    global last_completed_wall, current_process, event_counter

    detected_completion = False

    try:
        if proc.stdout:
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                print(line)

                # Count incremental rows
                row_match = re.search(r"row\D*(\d+)", line, re.IGNORECASE)
                if row_match:
                    wall_line_count[wall_id] = wall_line_count.get(wall_id, 0) + 1
                    print(f"[counter] Wall {wall_id}: row {wall_line_count[wall_id]}")
                    fallback_counter[wall_id] = time.time()  # reset fallback timer

                # Detect completion
                wall_match = re.search(r"wall\D*(\d+)", line, re.IGNORECASE)
                if wall_match:
                    finished = int(wall_match.group(1))
                    print(f"✔ Wall {finished} completed.")
                    with state_lock:
                        last_completed_wall = finished
                        event_counter += 1
                    detected_completion = True

        proc.wait()
        rc = proc.returncode
        print(f"[controller] Script exit RC={rc}")

        if rc == 0 and not detected_completion:
            # Script ended without "wall X" printed
            print(f"[controller] Auto-marking wall {wall_id} as completed")
            with state_lock:
                last_completed_wall = wall_id
                event_counter += 1

    finally:
        with state_lock:
            current_process = None
            running_flag.clear()

        time.sleep(1.5)
        _maybe_start_next_wall_after_finish()


# -------------------------------------------------------------------
# Decide Next Wall
# -------------------------------------------------------------------
def _maybe_start_next_wall_after_finish():
    with state_lock:
        if pause_flag.is_set():
            print("[controller] Paused — stop scheduling next wall.")
            return

        if not wall_queue:
            print("[controller] All walls completed for this phase.")
            return

    start_next_wall()


# -------------------------------------------------------------------
# Start Next Wall (NO HOME CHECK)
# -------------------------------------------------------------------
def start_next_wall():
    global current_wall, current_process, last_completed_wall

    with state_lock:
        if pause_flag.is_set():
            print("Paused → skipping next wall.")
            return

        if not wall_queue:
            print("No more walls.")
            current_wall = None
            return

        label = wall_queue.pop(0)
        m = re.search(r"(\d+)", label)
        wall_id = int(m.group(1))

        current_wall = wall_id
        running_flag.set()

        wall_line_count[wall_id] = 0
        fallback_counter[wall_id] = time.time()
        last_completed_wall = None

        folder = current_folder
        excel_rel = os.path.relpath(excel_file_path, folder)

    # Only marking process here
    marking_cmd = [
        "sshpass", "-p", "winsys",
        "ssh", "winsys@192.168.130.5",
        "/home/winsys/pbu_marking_ros/run_marking.sh",
        "--stage", "2",
        "--wall", str(wall_id),
        "--folder", folder,
        "--excel", excel_rel,
        "--mesh", mesh_file_path,
    ]

    print(f"[controller] 🚀 Starting marking wall {wall_id}")
    print(marking_cmd)

    try:
        proc = subprocess.Popen(
            marking_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as e:
        running_flag.clear()
        with state_lock:
            current_wall = None
        raise RuntimeError(f"Marking script failed: {e}")

    with state_lock:
        current_process = proc

    threading.Thread(
        target=reader_thread,
        args=(proc, wall_id),
        daemon=True,
    ).start()


# -------------------------------------------------------------------
# PAUSE / CONTINUE
# -------------------------------------------------------------------
@app.post("/pause")
def marking_pause():
    pause_flag.set()
    return {"paused": True}


@app.post("/continue")
def marking_continue():
    pause_flag.clear()
    with state_lock:
        should_start = (current_process is None) and bool(wall_queue)
    if should_start:
        start_next_wall()
    return {"resumed": True}


# -------------------------------------------------------------------
# START MARKING — NO HOME CHECK HERE
# -------------------------------------------------------------------
@app.post("/start")
def marking_start(body: MarkingStartBody):
    global wall_queue, excel_file_path, mesh_file_path
    global current_phase, total_walls, current_folder
    global current_wall, last_completed_wall, event_counter

    if not body.walls:
        raise HTTPException(400, "walls is empty")

    with state_lock:
        wall_queue = [str(w.wall).strip() for w in body.walls]
        excel_file_path = body.excelfile
        mesh_file_path = body.meshfile
        current_phase = body.phase
        current_folder = body.folder
        total_walls = body.max_wall

        current_wall = None
        last_completed_wall = None

        running_flag.clear()
        pause_flag.clear()

        event_counter += 1

        print("\n[controller] NEW MARKING SEQUENCE")
        print("Queue:", wall_queue)
        print("Phase:", current_phase)
        print("Folder:", current_folder)
        print("Excel:", excel_file_path)

    threading.Thread(target=start_next_wall, daemon=True).start()

    return {"ok": True, "queue": wall_queue}


# -------------------------------------------------------------------
# STATUS (NOW WITH FALLBACK 5-SECOND COUNTER)
# -------------------------------------------------------------------
@app.get("/status")
def marking_status():
    folder = current_folder or "/home/winsys/pbu_marking_ros/pbu_data/mockup"
    excel_rel = os.path.relpath(excel_file_path, folder) if excel_file_path else ""

    # ⭐ Fallback counter logic
    if current_wall:
        lc = wall_line_count.get(current_wall, 0)
        now = time.time()
        last = fallback_counter.get(current_wall, now)

        # If still 0 rows → increment every 5 seconds
        if lc == 0:
            if now - last >= 5:
                wall_line_count[current_wall] = 1
                fallback_counter[current_wall] = now
        else:
            # Reset fallback when valid row detected
            fallback_counter[current_wall] = now

    return {
        "running": running_flag.is_set(),
        "paused": pause_flag.is_set(),
        "startedWall": current_wall,
        "doneWall": last_completed_wall,
        "queue": list(wall_queue),
        "phase": current_phase,
        "maxWalls": total_walls,
        "excelFile": excel_rel,
        "folder": folder,
        "meshFile": mesh_file_path,
        "lineCount": wall_line_count.get(current_wall, 0),
        "eventID": event_counter,
    }
