# backend/marking_controller.py
# FINAL VERSION — PER-WALL EXCEL MAPPING + EVENT-BASED POINT COUNTER
# - Bringup success when log contains:
#       "Service executed successfully"
# - Point counter increments on lines containing:
#       "Point" and "done"  (e.g. "Point 20 is already done. Skipping...")
# - Wall completes when:
#       point_count >= row_totals[wall_id]
# - On mismatch → error, stay at that wall, wait for Retry from frontend.
# - Each wall has its own Excel file (from frontend), mapped by wall id.

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

# Walls sequence & index (e.g. ["wall_2", "wall_3", "wall_4"])
wall_sequence: List[str] = []
queue_index: int = 0  # index into wall_sequence

total_walls: int = 0
row_totals: Dict[int, int] = {}          # {2: 6, 3: 8, 4: 4}
wall_point_count: Dict[int, int] = {}    # {2: 0, 3: 3, ...}
bringup_success: Dict[int, bool] = {}    # {2: True/False}
wall_error: Dict[int, bool] = {}         # {2: True if mismatch/error}

# PER-WALL EXCEL MAPPING (RELATIVE paths, e.g. "PBU_TERRAHL2_out/..._wall_2.xlsx")
excel_map: Dict[int, str] = {}

mesh_file_path: str = ""
current_folder: str = ""    # informational only (your local folder)
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
    wall: str          # e.g. "wall_2"
    rows: list         # rows for that wall
    excel: str         # FULL PATH from React (e.g. "/home/winsys/.../PBU_TERRAHL2_out/..._wall_2.xlsx")


class MarkingStartBody(BaseModel):
    walls: List[WallPayload]
    meshfile: str
    max_wall: int
    folder: str
    phase: Optional[int] = None  # just a logical phase flag


class HomeCheckBody(BaseModel):
    target: str  # expects "wall_2", "wall_3", etc.


# -------------------------------------------------------------------
# EXCEL PATH NORMALIZATION (TRIM TO RELATIVE)
# -------------------------------------------------------------------
def make_relative_excel(path: str) -> str:
    """
    React sends an ABSOLUTE path, e.g.:
      /home/winsys/pbu_marking_ros/pbu_data/mockup/PBU_TERRAHL2_out/PBU_TERRAHL2_out1_wall_2.xlsx

    We ONLY want:
      PBU_TERRAHL2_out/PBU_TERRAHL2_out1_wall_2.xlsx

    Logic:
      - Find "PBU_" in the path (e.g. "PBU_TERRAHL2_out/...")
      - Return from that position (no leading slash)
      - If not found, return the original path as-is.
    """
    if not path:
        return path

    # Try generic token "PBU_"
    token = "PBU_"
    idx = path.find(token)
    if idx != -1:
        return path[idx:]

    # Fallback: just strip any leading slash
    return path.lstrip("/")


# -------------------------------------------------------------------
# HOME CHECK
# -------------------------------------------------------------------
@app.post("/homecheck")
def home_position_check(body: HomeCheckBody):
    """
    Calls remote homeposcheck.py with:
      --file /home/winsys/pbu_marking_ros/pbu_data/mockup/poses.json
      --target <wall_number>
    """
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

        return {"ok": True, "wall": m , "output": out}

    except Exception as e:
        raise HTTPException(500, f"HomePosCheck error: {str(e)}")


# -------------------------------------------------------------------
# HELPER: append to error_logs[wall_id]
# -------------------------------------------------------------------
def _append_log(wall_id: int, line: str):
    if wall_id not in error_logs:
        error_logs[wall_id] = []
    error_logs[wall_id].append(line)
    if len(error_logs[wall_id]) > MAX_LOG_LINES_PER_WALL:
        error_logs[wall_id] = error_logs[wall_id][-MAX_LOG_LINES_PER_WALL:]


# -------------------------------------------------------------------
# READER THREAD — event-based bringup + point counting + logs
# -------------------------------------------------------------------
def reader_thread(proc: subprocess.Popen, wall_id: int):
    """
    - Watches process stdout line-by-line
    - Detects bringup success via: "Service executed successfully"
    - Counts points via lines containing both "Point" and "done"
    - After process ends, decides success/error purely from:
        * exit code
        * bringup_success[wall_id]
        * wall_point_count[wall_id] vs row_totals[wall_id]
    """
    global last_completed_wall, current_process, event_counter

    start_detected = False  # bringup success seen?

    try:
        if proc.stdout:
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                print(line)

                # Always store in raw logs
                with state_lock:
                    _append_log(wall_id, line)

                # 1) Bringup success
                if "Service executed successfully" in line:
                    with state_lock:
                        bringup_success[wall_id] = True
                    start_detected = True
                    print(f"[bringup] Wall {wall_id}: service executed successfully")

                # 2) Point counting (only after bringup success)
                # e.g. "Point 20 is already done. Skipping..."
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
                current_wall = wall_id  # stay on this wall

                msg_parts = []
                if rc != 0:
                    msg_parts.append(f"script exit code {rc}")
                if not ok_start:
                    msg_parts.append("bringup not successful")
                if total > 0 and count < total:
                    msg_parts.append(f"only {count}/{total} points done")

                summary = (
                    f"[ERROR] Wall {wall_id}: " + ", ".join(msg_parts)
                    if msg_parts else
                    f"[ERROR] Wall {wall_id}: unknown error"
                )
                _append_log(wall_id, summary)
                print(summary)

        if start_next:
            threading.Thread(target=start_next_wall, daemon=True).start()

    finally:
        # state handled above
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

        label = wall_sequence[queue_index]  # e.g. "wall_2"
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

        running_flag.set()

        # Excel file for this wall (RELATIVE)
        excel_rel = excel_map.get(wall_id, "")
        # remote folder is fixed for ROS script
        remote_folder = "/home/ros_user/pbu_data/mockup"
        mesh_value = mesh_file_path

    # Build remote command:
    #   cd /home/winsys/pbu_marking_ros &&
    #   ./run_marking.sh --stage 2 --wall wall_2 --folder /home/ros_user/pbu_data/mockup
    #                    --excel PBU_TERRAHL2_out/..._wall_2.xlsx --mesh SIMTech_L_PBU.stl
    remote_command = (
        "cd /home/winsys/pbu_marking_ros && "
        "./run_marking.sh "
        "--stage 2 "
        f"--wall {shlex.quote(label)} "
        f"--folder {shlex.quote(remote_folder)} "
        f"--excel {shlex.quote(excel_rel)} "
        f"--mesh {shlex.quote(mesh_value)}"
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
# START MARKING — per-wall Excel mapping
# -------------------------------------------------------------------
@app.post("/start")
def marking_start(body: MarkingStartBody):
    """
    Frontend calls this for Phase 1 (walls 2,3,4) and Phase 2 (walls 5,6,1):
      walls: [
        { wall: "wall_2", rows: [...], excel: "/home/.../PBU_TERRAHL2_out/..._wall_2.xlsx" },
        { wall: "wall_3", rows: [...], excel: "/home/.../PBU_TERRAHL2_out/..._wall_3.xlsx" },
        ...
      ]
    """
    global wall_sequence, queue_index
    global mesh_file_path, current_folder, current_phase, total_walls
    global current_wall, last_completed_wall, event_counter
    global row_totals, wall_point_count, bringup_success, wall_error, error_logs, excel_map

    if not body.walls:
        raise HTTPException(400, "walls is empty")

    with state_lock:
        # sequence from frontend (Phase 1: 2,3,4; Phase 2: 5,6,1)
        wall_sequence = [w.wall.strip() for w in body.walls]
        queue_index = 0

        # build row_totals
        row_totals = {}
        excel_map = {}
        for w in body.walls:
            # wall id
            m = re.search(r"(\d+)", w.wall)
            if not m:
                continue
            wid = int(m.group(1))
            row_totals[wid] = len(w.rows)

            # per-wall Excel (trim absolute to relative)
            rel_excel = make_relative_excel(w.excel)
            excel_map[wid] = rel_excel

        print("[controller] New Marking Sequence")
        print("Sequence:", wall_sequence)
        print("Row totals:", row_totals)
        print("Excel map (relative):", excel_map)

        mesh_file_path = body.meshfile
        current_folder = body.folder
        total_walls = body.max_wall
        current_phase = body.phase

        # reset global state
        current_wall = None
        last_completed_wall = None
        event_counter += 1

        pause_flag.clear()
        running_flag.clear()

        wall_point_count = {}
        bringup_success = {}
        wall_error = {}
        error_logs = {}

        # init per-wall state
        for wid, _total in row_totals.items():
            wall_point_count[wid] = 0
            bringup_success[wid] = False
            wall_error[wid] = False
            error_logs[wid] = []

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
        should_start = (
            current_process is None
            and current_wall is None
            and queue_index < len(wall_sequence)
        )
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
    global current_wall, current_process, queue_index

    with state_lock:
        if wall is None:
            if current_wall is None:
                raise HTTPException(400, "No wall specified and no current wall.")
            wall_id = current_wall
        else:
            wall_id = wall

        if current_process is not None:
            raise HTTPException(400, "Cannot retry while a process is still running.")

        label = f"wall_{wall_id}"
        if label not in wall_sequence:
            raise HTTPException(400, f"Wall label {label} not in sequence.")

        # force queue_index to this wall
        queue_index = wall_sequence.index(label)

        # reset this wall's state
        wall_point_count[wall_id] = 0
        bringup_success[wall_id] = False
        wall_error[wall_id] = False
        current_wall = None
        running_flag.clear()
        # keep error_logs[wall_id] so UI can still show history

    threading.Thread(target=start_next_wall, daemon=True).start()
    return {"ok": True, "wall": wall_id, "message": "Retry started."}


# -------------------------------------------------------------------
# STATUS — event-based only (no fallback)
# -------------------------------------------------------------------
@app.get("/status")
def marking_status():
    with state_lock:
        active_wall: Optional[int] = current_wall

        remaining_queue = (
            wall_sequence[queue_index + 1 :] if queue_index < len(wall_sequence) else []
        )

        has_error = False
        error_summary: Optional[str] = None
        point_count = 0
        total_points = 0

        if active_wall is not None:
            has_error = wall_error.get(active_wall, False)
            point_count = wall_point_count.get(active_wall, 0)
            total_points = row_totals.get(active_wall, 0)
            lines = error_logs.get(active_wall, [])
            if lines:
                error_summary = lines[-1]
        else:
            if last_completed_wall is not None and wall_error.get(last_completed_wall, False):
                has_error = True
                point_count = wall_point_count.get(last_completed_wall, 0)
                total_points = row_totals.get(last_completed_wall, 0)
                lines = error_logs.get(last_completed_wall, [])
                if lines:
                    error_summary = lines[-1]

        folder = current_folder or "/home/ros_user/pbu_data/mockup"

        response: Dict[str, Any] = {
            "running": running_flag.is_set(),
            "paused": pause_flag.is_set(),
            "startedWall": active_wall,
            "doneWall": last_completed_wall,
            "queue": remaining_queue,
            "phase": current_phase,
            "maxWalls": total_walls,
            "excelMap": excel_map,
            "folder": folder,
            "meshFile": mesh_file_path,
            "lineCount": point_count,       # points done
            "totalPoints": total_points,    # expected points
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
    Path-style error log access: /marking/errorlog/2
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

