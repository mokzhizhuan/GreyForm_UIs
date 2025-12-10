# backend/marking_controller.py
# FINAL VERSION — FALLBACK + POINT-BASED COUNTER
# Uses "Point ... done" lines to increment wall_line_count,
# AND keeps 5s fallback in /status for silent robots.

import subprocess
import threading
import re
import time
import os
import shlex
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
row_totals: dict[int, int] = {}  # {2: 6, 3: 8, 4: 4}

excel_file_path: str = ""
mesh_file_path: str = ""
current_folder: str = ""  # not really used now, but kept for completeness
current_phase: Optional[int] = None

state_lock = threading.Lock()
event_counter = 0

# robot line counter + fallback timestamps
wall_line_count: dict[int, int] = {}      # {2: 0, 3: 1, ...}
fallback_counter: dict[int, float] = {}   # {2: timestamp, ...}


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
    target: str  # expects "wall_3", "wall_4", etc.


# -------------------------------------------------------------------
# HOME CHECK — unchanged
# -------------------------------------------------------------------
@app.post("/homecheck")
def home_position_check(body: HomeCheckBody):

    m = re.search(r"(\d+)$", body.target)
    if not m:
        raise HTTPException(400, f"Invalid target format: {body.target}")

    wall_num = m.group(1)

    cmd = [
        "sshpass", "-p", "winsys",
        "ssh", "winsys@192.168.130.5",
        "python3",
        "/home/winsys/pbu_marking_ros/homeposcheck.py",
        "--file", "/home/winsys/pbu_marking_ros/pbu_data/mockup/poses.json",
        "--target", wall_num,
    ]

    print(f"[HomeCheck] Running:", cmd)

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        out, _ = proc.communicate()

        print("[HomeCheck Output]\n", out)

        if proc.returncode != 0:
            raise HTTPException(400, "Home position check FAILED!")

        return {"ok": True, "wall": wall_num, "output": out}

    except Exception as e:
        raise HTTPException(500, f"HomePosCheck error: {str(e)}")


# -------------------------------------------------------------------
# READER THREAD — ONLY reads output; counting uses "Point ... done"
# -------------------------------------------------------------------
def reader_thread(proc: subprocess.Popen, wall_id: int):
    global last_completed_wall, current_process, event_counter

    detected_completion = False

    try:
        if proc.stdout:
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                print(line)

                # --- POINT-BASED COUNTER ----------------------------------
                # Any line containing something like:
                #   "Point 20 is already done. Skipping..."
                # or generally "Point <num> ... done"
                done_match = re.search(r"Point\s+(\d+).*done", line, re.IGNORECASE)
                if done_match:
                    point_id = done_match.group(1)
                    with state_lock:
                        wall_line_count[wall_id] = wall_line_count.get(wall_id, 0) + 1
                        fallback_counter[wall_id] = time.time()
                        current_count = wall_line_count[wall_id]
                        total = row_totals.get(wall_id, 0)
                        print(
                            f"[point] Wall {wall_id}: Point {point_id} DONE "
                            f"({current_count}/{total})"
                        )

                # --- OPTIONAL: explicit script completion (if printed) -----
                wall_match = re.search(r"wall\D*(\d+)", line, re.IGNORECASE)
                if wall_match:
                    finished = int(wall_match.group(1))
                    print(f"✔ COMPLETED SIGNAL: Wall {finished}")
                    with state_lock:
                        last_completed_wall = finished
                        event_counter += 1
                    detected_completion = True

        proc.wait()
        rc = proc.returncode
        print(f"[controller] Script RC={rc}")

        # IMPORTANT: do NOT auto-complete here if silent.
        if rc == 0 and not detected_completion:
            print(
                f"[info] Script ended for wall {wall_id} without explicit completion. "
                f"Fallback/point counter will handle progression."
            )
    finally:
        with state_lock:
            current_process = None
            # running_flag is controlled by /status when we decide wall is done

        # Do NOT start next wall here. Progression handled in /status via fallback.


# -------------------------------------------------------------------
# START NEXT WALL
# -------------------------------------------------------------------
def start_next_wall():
    global current_wall, current_process, last_completed_wall

    with state_lock:
        if pause_flag.is_set():
            print("[controller] Paused → stop")
            return

        if not wall_queue:
            print("[controller] All walls done!")
            current_wall = None
            running_flag.clear()
            return

        label = wall_queue.pop(0)
        print(f"[DEBUG] RAW LABEL FROM QUEUE = '{label}'")

        wall_id = int(re.search(r"(\d+)", label).group(1))
        current_wall = wall_id

        # reset counters for this wall
        wall_line_count[wall_id] = 0
        fallback_counter[wall_id] = time.time()
        last_completed_wall = None
        running_flag.set()

        # we ignore body.folder here for the remote command and use
        # the fixed /home/ros_user/pbu_data/mockup as requested
        folder = "/home/ros_user/pbu_data/mockup"

        # excel_file_path is already a relative path like
        #   "PBU_TERRAHL2_out/PBU_TERRAHL2_out1.xlsx"
        # so we pass it as-is to the remote script
        excel_rel = excel_file_path

    # Build a single remote command string
    remote_command = (
        "cd /home/winsys/pbu_marking_ros && "
        "./run_marking.sh "
        "--stage 2 "
        f"--wall {shlex.quote(label)} "
        f"--folder {shlex.quote(folder)} "
        f"--excel {shlex.quote(excel_rel)} "
        f"--mesh {shlex.quote(mesh_file_path)}"
    )

    marking_cmd = [
        "sshpass", "-p", "winsys",
        "ssh", "winsys@192.168.130.5",
        remote_command,
    ]

    print(f"[controller] 🚀 Starting wall {wall_id}")
    print(marking_cmd)

    proc = subprocess.Popen(
        marking_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    with state_lock:
        current_process = proc

    threading.Thread(
        target=reader_thread, args=(proc, wall_id), daemon=True
    ).start()


# -------------------------------------------------------------------
# START MARKING
# -------------------------------------------------------------------
@app.post("/start")
def marking_start(body: MarkingStartBody):
    global wall_queue, excel_file_path, mesh_file_path
    global current_phase, total_walls, current_folder
    global current_wall, last_completed_wall, event_counter, row_totals

    with state_lock:
        # set queue as labels: "wall_2", "wall_3", ...
        wall_queue = [w.wall.strip() for w in body.walls]

        # build row_totals from rows length
        row_totals = {}
        for w in body.walls:
            m = re.search(r"(\d+)", w.wall)
            if m:
                row_totals[int(m.group(1))] = len(w.rows)

        print("[controller] New Marking Sequence")
        print("Queue:", wall_queue)
        print("Row totals:", row_totals)

        # we expect body.excelfile to be something like
        #   "PBU_TERRAHL2_out/PBU_TERRAHL2_out1.xlsx"
        excel_file_path = body.excelfile
        mesh_file_path = body.meshfile
        current_folder = body.folder
        total_walls = body.max_wall
        current_phase = body.phase

        # reset
        current_wall = None
        last_completed_wall = None
        event_counter += 1

        pause_flag.clear()

        # initialize counters
        wall_line_count.clear()
        fallback_counter.clear()
        for wid, total in row_totals.items():
            wall_line_count[wid] = 0
            fallback_counter[wid] = time.time()

    # start first wall
    threading.Thread(target=start_next_wall, daemon=True).start()
    return {"ok": True, "queue": wall_queue}


# -------------------------------------------------------------------
# PAUSE / CONTINUE
# -------------------------------------------------------------------
@app.post("/pause")
def pause():
    pause_flag.set()
    return {"paused": True}


@app.post("/continue")
def resume():
    pause_flag.clear()
    # if nothing is running but queue has items, start next
    with state_lock:
        should_start = (current_process is None) and bool(wall_queue)
    if should_start:
        threading.Thread(target=start_next_wall, daemon=True).start()
    return {"resumed": True}


# -------------------------------------------------------------------
# STATUS — point-based + 5s fallback
# -------------------------------------------------------------------
@app.get("/status")
def marking_status():
    global current_wall, last_completed_wall

    should_start_next = False

    with state_lock:
        # Fallback logic: increment current_wall's line count every 5s
        if current_wall is not None:
            cw = current_wall
            total = row_totals.get(cw, 0)
            lc = wall_line_count.get(cw, 0)
            now = time.time()
            last = fallback_counter.get(cw, now)

            # Fallback only if we haven't reached total yet
            if lc < total and now - last >= 5:
                lc += 1
                wall_line_count[cw] = lc
                fallback_counter[cw] = now
                print(f"[auto] Wall {cw}: {lc}/{total}")

            # When this wall is fully done:
            if total > 0 and lc >= total:
                if last_completed_wall != cw:
                    print(f"[auto] Wall {cw} COMPLETE ({lc}/{total})")
                last_completed_wall = cw

                # mark done + prepare next
                current_wall = None
                running_flag.clear()

                if wall_queue and not pause_flag.is_set():
                    should_start_next = True

        # Note: folder here is only for returning to client
        folder = current_folder or "/home/ros_user/pbu_data/mockup"
        excel_rel = excel_file_path or ""

        response = {
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
            "lineCount": wall_line_count.get(current_wall, 0) if current_wall else 0,
            "eventID": event_counter,
            "rowTotals": row_totals,
        }

    # Start next wall outside the lock to avoid deadlock
    if should_start_next:
        threading.Thread(target=start_next_wall, daemon=True).start()

    return response

# -------------------------------------------------------------------
# ERROR LOG API — returns raw log output exactly as printed
# -------------------------------------------------------------------
@app.get("/errorlog")
def get_error_log(wall: Optional[int] = None):
    """
    Return raw log/error lines exactly as printed by the script.
    - If ?wall=<id> is provided, return that wall's logs.
    - Else, use current_wall if available.
    """
    with state_lock:
        wid = wall or current_wall

        if wid is None:
            return {
                "ok": False,
                "wall": None,
                "error": ["No active or selected wall."]
            }

        logs = list(error_logs.get(wid, []))

    return {
        "ok": True,
        "wall": wid,
        "error": logs,
    }


@app.get("/errorlog/{wall_id}")
def get_error_log_by_path(wall_id: int):
    """
    Path-style error log access: /errorlog/2
    """
    with state_lock:
        logs = list(error_logs.get(wall_id, []))

    return {
        "ok": True,
        "wall": wall_id,
        "error": logs,
    }


@app.post("/errorlog/clear")
def clear_error_log(wall: Optional[int] = None):
    """
    Clear error logs.
    - If ?wall=<id> is provided: clear only that wall.
    - If no wall is provided: clear ALL logs.
    """
    with state_lock:
        if wall is None:
            error_logs.clear()
            return {
                "ok": True,
                "wall": None,
                "message": "All error logs cleared.",
            }

        if wall in error_logs:
            error_logs.pop(wall, None)
            return {
                "ok": True,
                "wall": wall,
                "message": f"Error log for wall {wall} cleared.",
            }

        return {
            "ok": False,
            "wall": wall,
            "message": f"No error log stored for wall {wall}.",
        }
