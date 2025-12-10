# backend/marking_controller.py
# FINAL VERSION — EVENT-BASED POINT COUNTER + BRINGUP DETECTION
# - Uses real robot output, NO time-based fallback.
# - Bringup success when:
#       success: True
#       message: "Service executed successfully"
# - Point counter increments on:
#       "Point ... done"
# - Wall completes when:
#       point_count == row_totals[wall_id]
# - On mismatch → error, stay at that wall, wait for Retry from frontend.

import subprocess
import threading
import re
import time
import os
import shlex
from typing import List, Optional, Dict, Any

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

# Walls sequence & index
wall_sequence: List[str] = []  # ["wall_2", "wall_3", ...]
queue_index: int = 0           # index into wall_sequence

total_walls: int = 0
row_totals: Dict[int, int] = {}          # {2: 6, 3: 8, 4: 4}
wall_point_count: Dict[int, int] = {}    # {2: 0, 3: 3, ...}
bringup_success: Dict[int, bool] = {}    # {2: True/False}
wall_error: Dict[int, bool] = {}         # {2: True if mismatch/error}

excel_file_path: str = ""   # EXPECTED RELATIVE, e.g. "PBU_TERRAHL2_out/PBU_TERRAHL2_out1.xlsx"
mesh_file_path: str = ""
current_folder: str = ""    # For info/status only
current_phase: Optional[int] = None

state_lock = threading.Lock()
event_counter = 0

# Raw logs per wall (for /errorlog)
error_logs: Dict[int, List[str]] = {}
MAX_LOG_LINES_PER_WALL = 400

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
# HELPER: append to error_logs[wall_id]
# -------------------------------------------------------------------
def _append_log(wall_id: int, line: str):
    if wall_id not in error_logs:
        error_logs[wall_id] = []
    error_logs[wall_id].append(line)
    # keep only last N lines
    if len(error_logs[wall_id]) > MAX_LOG_LINES_PER_WALL:
        error_logs[wall_id] = error_logs[wall_id][-MAX_LOG_LINES_PER_WALL:]


# -------------------------------------------------------------------
# READER THREAD — reads output; decides success/error only by logs
# -------------------------------------------------------------------
def reader_thread(proc: subprocess.Popen, wall_id: int):
    global last_completed_wall, current_process, event_counter
    start_detected = False  # whether we've seen "Service executed successfully"

    try:
        if proc.stdout:
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                print(line)

                # always log
                with state_lock:
                    _append_log(wall_id, line)

                # DETECT bringup success
                if "Service executed successfully" in line:
                    with state_lock:
                        bringup_success[wall_id] = True
                    start_detected = True
                    print(f"[bringup] Wall {wall_id}: service executed successfully")

                # DETECT marking points only AFTER bringup success
                # Matches lines like "Point 20 is already done. Skipping..."
                if start_detected and "Point" in line and "done" in line:
                    with state_lock:
                        wall_point_count[wall_id] = wall_point_count.get(wall_id, 0) + 1
                        count = wall_point_count[wall_id]
                        total = row_totals.get(wall_id, 0)
                        print(f"[point] Wall {wall_id}: {count}/{total} points done")

        proc.wait()
        rc = proc.returncode
        print(f"[controller] Script RC={rc}")

        # Decide success vs error based on counts & bringup
        start_next = False

        with state_lock:
            current_process = None
            running_flag.clear()

            total = row_totals.get(wall_id, 0)
            count = wall_point_count.get(wall_id, 0)
            ok_start = bringup_success.get(wall_id, False)

            if rc == 0 and ok_start and total > 0 and count >= total:
                # ✅ SUCCESSFUL WALL
                last_completed_wall = wall_id
                wall_error[wall_id] = False
                event_counter += 1
                print(f"[success] Wall {wall_id} COMPLETE ({count}/{total})")
                # advance queue index
                global queue_index, current_wall
                queue_index += 1
                current_wall = None

                # schedule next wall IF any & not paused
                if queue_index < len(wall_sequence) and not pause_flag.is_set():
                    start_next = True
            else:
                # ❌ ERROR — either rc!=0, or no bringup success, or insufficient points
                wall_error[wall_id] = True
                # Do NOT advance queue_index; stay on same wall
                current_wall = wall_id

                # add a summary error line
                msg_parts = []
                if rc != 0:
                    msg_parts.append(f"script exit code {rc}")
                if not ok_start:
                    msg_parts.append("bringup not successful")
                if total > 0 and count < total:
                    msg_parts.append(f"only {count}/{total} points done")

                summary = f"[ERROR] Wall {wall_id}: " + ", ".join(msg_parts) if msg_parts else f"[ERROR] Wall {wall_id}: unknown error"
                _append_log(wall_id, summary)
                print(summary)

        if start_next:
            threading.Thread(target=start_next_wall, daemon=True).start()

    finally:
        # nothing extra; state handled above
        pass


# -------------------------------------------------------------------
# START NEXT WALL (from wall_sequence[queue_index])
# -------------------------------------------------------------------
def start_next_wall():
    global current_wall, current_process, last_completed_wall, queue_index

    with state_lock:
        if pause_flag.is_set():
            print("[controller] Paused → stop")
            return

        if queue_index >= len(wall_sequence):
            print("[controller] All walls done! queue_index >= len(wall_sequence)")
            current_wall = None
            running_flag.clear()
            return

        label = wall_sequence[queue_index]
        print(f"[DEBUG] QUEUE INDEX={queue_index}, LABEL='{label}'")

        m = re.search(r"(\d+)", label)
        if not m:
            print(f"[ERROR] Invalid wall label: {label}")
            wall_error[-1] = True
            return

        wall_id = int(m.group(1))
        current_wall = wall_id

        # reset counters for this wall
        wall_point_count[wall_id] = 0
        bringup_success[wall_id] = False
        wall_error[wall_id] = False
        last_completed_wall = None

        # DO NOT clear error_logs[wall_id] automatically; keep history
        running_flag.set()

        # We respect the exact excelfile as provided (relative)
        excel_rel = excel_file_path  # e.g. "PBU_TERRAHL2_out/PBU_TERRAHL2_out1.xlsx"

    # Build remote command:
    #   folder MUST be /home/ros_user/pbu_data/mockup
    remote_command = (
        "cd /home/winsys/pbu_marking_ros && "
        "./run_marking.sh "
        "--stage 2 "
        f"--wall {shlex.quote(label)} "
        "--folder /home/ros_user/pbu_data/mockup "
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

    try:
        proc = subprocess.Popen(
            marking_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as e:
        with state_lock:
            current_process = None
            running_flag.clear()
            wall_error[wall_id] = True
            _append_log(wall_id, f"[ERROR] Failed to start marking script: {e}")
        raise RuntimeError(f"Marking script failed: {e}")

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
    global wall_sequence, queue_index
    global excel_file_path, mesh_file_path, current_folder
    global current_phase, total_walls
    global current_wall, last_completed_wall, event_counter
    global row_totals, wall_point_count, bringup_success, wall_error, error_logs

    if not body.walls:
        raise HTTPException(400, "walls is empty")

    with state_lock:
        wall_sequence = [w.wall.strip() for w in body.walls]
        queue_index = 0

        # Build row_totals
        row_totals = {}
        for w in body.walls:
            m = re.search(r"(\d+)", w.wall)
            if m:
                wall_id = int(m.group(1))
                row_totals[wall_id] = len(w.rows)

        print("[controller] New Marking Sequence")
        print("Sequence:", wall_sequence)
        print("Row totals:", row_totals)

        excel_file_path = body.excelfile  # MUST be like "PBU_TERRAHL2_out/PBU_TERRAHL2_out1.xlsx"
        mesh_file_path = body.meshfile
        current_folder = body.folder  # informational
        total_walls = body.max_wall
        current_phase = body.phase

        # reset
        current_wall = None
        last_completed_wall = None
        event_counter += 1

        pause_flag.clear()
        running_flag.clear()

        # reset per-wall state
        wall_point_count = {}
        bringup_success = {}
        wall_error = {}
        error_logs = {}

    # start first wall
    threading.Thread(target=start_next_wall, daemon=True).start()
    return {"ok": True, "queue": wall_sequence}


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
    with state_lock:
        should_start = (current_process is None) and (current_wall is None) and (queue_index < len(wall_sequence))
    if should_start:
        threading.Thread(target=start_next_wall, daemon=True).start()
    return {"resumed": True}


# -------------------------------------------------------------------
# RETRY API — rerun current or selected wall, no auto retry
# -------------------------------------------------------------------
@app.post("/retry")
def retry_wall(wall: Optional[int] = None):
    """
    Retry marking for a specific wall.
    - If ?wall=<id> is absent, retry current_wall (if any).
    - Does NOT auto-advance; re-runs the same wall.
    """

    global current_wall, current_process

    with state_lock:
        if wall is None:
            if current_wall is None:
                raise HTTPException(400, "No wall specified and no current wall.")
            wall_id = current_wall
        else:
            wall_id = wall

        # Ensure no process is running
        if current_process is not None:
            raise HTTPException(400, "Cannot retry while a process is still running.")

        # Find this wall in sequence; queue_index must point to it
        label = f"wall_{wall_id}"
        if label not in wall_sequence:
            raise HTTPException(400, f"Wall label {label} not in sequence.")

        # Force queue_index to this wall
        global queue_index
        queue_index = wall_sequence.index(label)

        # Reset state for that wall
        wall_point_count[wall_id] = 0
        bringup_success[wall_id] = False
        wall_error[wall_id] = False
        current_wall = None
        running_flag.clear()

        # Do NOT clear error_logs[wall_id] here; frontend can call /errorlog/clear if wanted

    threading.Thread(target=start_next_wall, daemon=True).start()
    return {"ok": True, "wall": wall_id, "message": "Retry started."}


# -------------------------------------------------------------------
# STATUS — event-based only (no fallback)
# -------------------------------------------------------------------
@app.get("/status")
def marking_status():
    with state_lock:
        # Choose "active wall" for counters & error reporting
        active_wall: Optional[int] = current_wall

        # derive queue (remaining walls after queue_index)
        remaining_queue = wall_sequence[queue_index + 1 :] if queue_index < len(wall_sequence) else []

        has_error = False
        error_summary: Optional[str] = None
        point_count = 0
        total_points = 0

        if active_wall is not None:
            has_error = wall_error.get(active_wall, False)
            point_count = wall_point_count.get(active_wall, 0)
            total_points = row_totals.get(active_wall, 0)
            # optional: last error line as summary
            lines = error_logs.get(active_wall, [])
            if lines:
                error_summary = lines[-1]
        else:
            # no active wall; if last_completed_wall had an error, report it
            if last_completed_wall is not None and wall_error.get(last_completed_wall, False):
                has_error = True
                point_count = wall_point_count.get(last_completed_wall, 0)
                total_points = row_totals.get(last_completed_wall, 0)
                lines = error_logs.get(last_completed_wall, [])
                if lines:
                    error_summary = lines[-1]

        folder = current_folder or "/home/ros_user/pbu_data/mockup"
        excel_rel = excel_file_path or ""

        response: Dict[str, Any] = {
            "running": running_flag.is_set(),
            "paused": pause_flag.is_set(),
            "startedWall": active_wall,
            "doneWall": last_completed_wall,
            "queue": remaining_queue,
            "phase": current_phase,
            "maxWalls": total_walls,
            "excelFile": excel_rel,
            "folder": folder,
            "meshFile": mesh_file_path,
            # use lineCount as "points done"
            "lineCount": point_count,
            "totalPoints": total_points,
            "eventID": event_counter,
            "rowTotals": row_totals,
            "hasError": has_error,
            "errorSummary": error_summary,
        }

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
        wid = wall if wall is not None else current_wall

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
