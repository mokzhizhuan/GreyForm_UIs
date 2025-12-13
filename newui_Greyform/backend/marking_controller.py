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

# Track which points were skipped per wall, and the "current point" while reading logs
skipped_points: Dict[int, List[int]] = {}
current_point: Dict[int, Optional[int]] = {}

# PER-WALL EXCEL MAPPING (RELATIVE paths)
excel_map: Dict[int, str] = {}

mesh_file_path: str = ""
current_folder: str = ""    # informational only (your local folder)
current_phase: Optional[int] = None

state_lock = threading.Lock()
event_counter = 0

# Raw logs per wall (for /errorlog)
error_logs: Dict[int, List[str]] = {}
MAX_LOG_LINES_PER_WALL = 400

homecheck_pending: bool = False
homecheck_wall: Optional[int] = None
homecheck_output: Optional[str] = None


# -------------------------------------------------------------------
# MODELS
# -------------------------------------------------------------------
class WallPayload(BaseModel):
    wall: str          # e.g. "wall_2"
    rows: list         # rows for that wall
    excel: str         # FULL PATH from React


class MarkingStartBody(BaseModel):
    walls: List[WallPayload]
    meshfile: str
    max_wall: int
    folder: str                # e.g. "/home/ros_user/pbu_data/mockup"
    phase: Optional[int] = None  # just a logical phase flag


class HomeCheckBody(BaseModel):
    target: str  # expects "wall_2", "wall_3", etc.


# -------------------------------------------------------------------
# EXCEL PATH NORMALIZATION (USING FOLDERDIRECTORY)
# -------------------------------------------------------------------
def make_relative_excel(path: str, folder: Optional[str] = None) -> str:
    """
    Convert any absolute or semi-absolute Excel path to a path
    that is *relative to the folderdirectory*.

    Examples:
      folder = "/home/ros_user/pbu_data/mockup"

      1) path = "/home/winsys/pbu_marking_ros/pbu_data/mockup/test_points_tmp_out/test_points_tmp_out1_wall_1.xlsx"
         -> "test_points_tmp_out/test_points_tmp_out1_wall_1.xlsx"

      2) path = "mockup/test_points_tmp_out/test_points_tmp_out1_wall_1.xlsx"
         -> "test_points_tmp_out/test_points_tmp_out1_wall_1.xlsx"

      3) path = "/home/.../pbu_data/mockup/PBU_TERRAHL2_out/PBU_TERRAHL2_out1_wall_2.xlsx"
         -> "PBU_TERRAHL2_out/PBU_TERRAHL2_out1_wall_2.xlsx"

      4) path = "/home/.../PBU_TERRAHL2_out/PBU_TERRAHL2_out1_wall_2.xlsx"
         -> "PBU_TERRAHL2_out/PBU_TERRAHL2_out1_wall_2.xlsx"
    """
    if not path:
        return path

    # Normalise folder (folderdirectory)
    folder = (folder or "").rstrip("/")

    # 1) If the path already starts with the folderdirectory, strip it
    #    e.g. "/home/ros_user/pbu_data/mockup/test_points/..." with folder "/home/ros_user/pbu_data/mockup"
    if folder and path.startswith(folder + "/"):
        return path[len(folder) + 1 :]

    # 2) If the path starts with "mockup/", drop that prefix:
    #    "mockup/test_points_tmp_out/..." -> "test_points_tmp_out/..."
    if path.startswith("mockup/"):
        return path[len("mockup/") :]

    # 3) If the path contains "/mockup/", strip everything up to and including that:
    #    "/.../mockup/test_points_tmp_out/..." -> "test_points_tmp_out/..."
    marker = "/mockup/"
    idx = path.find(marker)
    if idx != -1:
        return path[idx + len(marker) :]

    # 4) If we have a folderdirectory, try using just its basename:
    #    folder "/home/ros_user/pbu_data/mockup" -> base "mockup"
    #    path "...mockup/test_points/..." -> "test_points/..."
    if folder:
        base = folder.split("/")[-1]
        marker2 = base + "/"
        idx2 = path.find(marker2)
        if idx2 != -1:
            return path[idx2 + len(marker2) :]

    # 5) Fallback: old PBU_ logic, for files like ".../PBU_TERRAHL2_out/..."
    token = "PBU_"
    idx3 = path.find(token)
    if idx3 != -1:
        return path[idx3:]

    # 6) Last fallback — just strip leading slash
    return path.lstrip("/")


# -------------------------------------------------------------------
# HOME CHECK
# -------------------------------------------------------------------
@app.post("/homecheck")
def home_position_check(body: HomeCheckBody):
    global homecheck_pending, homecheck_wall, homecheck_output

    target = body.target.strip()
    if not target:
        raise HTTPException(400, "Missing target for homecheck")

    m = re.search(r"(\d+)", target)
    if not m:
        raise HTTPException(400, f"Invalid wall label {target}")

    wall_id = int(m.group(1))

    cmd = [
        "sshpass", "-p", "winsys",
        "ssh", "winsys@192.168.130.5",
        "python3",
        "/home/winsys/pbu_marking_ros/homeposcheck.py",
        "--file", "/home/winsys/pbu_marking_ros/pbu_data/mockup/poses.json",
        "--target", target,
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out, _ = proc.communicate()

    if proc.returncode != 0:
        # script itself failed
        with state_lock:
            homecheck_pending = True
            homecheck_wall = wall_id
            homecheck_output = out
        raise HTTPException(400, out)

    # --------------------------------------------------
    # PARSE PASS/FAIL FROM homeposcheck.py OUTPUT
    # Expect somewhere in stdout: "True" or "False"
    # --------------------------------------------------
    passed: Optional[bool] = None
    for line in out.splitlines():
        t = line.strip()
        if t == "True":
            passed = True
            break
        if t == "False":
            passed = False
            break

    # If homeposcheck.py didn't print True/False, treat as fail
    if passed is None:
        passed = False

    # --------------------------------------------------
    # STORE HOME CHECK STATE (gate)
    # - passed => clear gate
    # - failed => keep gate (blocked)
    # --------------------------------------------------
    with state_lock:
        homecheck_output = out

        if passed:
            print(f"[HOME CHECK] Wall {wall_id} passed → starting marking")
            threading.Thread(target=start_next_wall, daemon=True).start()
        else:
            homecheck_pending = True
            homecheck_wall = wall_id
    
    return {
        "ok": True,
        "wall": wall_id,
        "passed": passed,
        "error": None if passed else "Home check failed (homeposcheck.py returned False).",
        "output": out,  # UI can still parse table from this
    }



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

                # --------------------------------------
                # 1) DETECT bringup success
                # --------------------------------------
                if "Service executed successfully" in line:
                    with state_lock:
                        bringup_success[wall_id] = True
                    start_detected = True
                    print(f"[bringup] Wall {wall_id}: service executed successfully")

                # --------------------------------------
                # 2) DETECT which point is currently running
                #    pattern: "Now working on point 2 of frame wall_2"
                # --------------------------------------
                m_point = re.search(
                    r"Now working on point\s+(\d+)\s+of frame wall", line
                )
                if m_point:
                    p = int(m_point.group(1))
                    with state_lock:
                        current_point[wall_id] = p
                    # optional debug
                    print(f"[point] Wall {wall_id}: now working on point {p}")

                # --------------------------------------
                # 3) DETECT "skipped" points
                #    pattern: "Writing into excel - ROW: X COLUMN: 8 VALUE skipped"
                # --------------------------------------
                if "VALUE skipped" in line:
                    with state_lock:
                        p = current_point.get(wall_id)
                        if p is not None:
                            skipped_points.setdefault(wall_id, []).append(p)
                            # Add a clean SKIP line into error log
                            _append_log(
                                wall_id,
                                f"[SKIP] Wall {wall_id}: point {p} skipped"
                            )
                            print(f"[skip] Wall {wall_id}: point {p} skipped")

                # --------------------------------------
                # 4) DETECT marking points only AFTER bringup success
                #    (still for your normal "Point ... done" pattern if present)
                # --------------------------------------
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
                current_wall = wall_id

                # add a summary error line
                msg_parts = []
                if rc != 0:
                    msg_parts.append(f"script exit code {rc}")
                if not ok_start:
                    msg_parts.append("bringup not successful")
                if total > 0 and count < total:
                    msg_parts.append(f"only {count}/{total} points done")

                # 🔥 include skipped points in summary if any
                skips = skipped_points.get(wall_id, [])
                if skips:
                    msg_parts.append(
                        "skipped points: " + ", ".join(str(p) for p in sorted(skips))
                    )

                summary = (
                    f"[ERROR] Wall {wall_id}: " + ", ".join(msg_parts)
                    if msg_parts
                    else f"[ERROR] Wall {wall_id}: unknown error"
                )
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
        if homecheck_pending:
            print("[BLOCKED] HomeCheck pending — marking not allowed")
            return
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

        # Excel file for this wall (RELATIVE to folderdirectory)
        excel_rel = excel_map.get(wall_id, "")
        # remote folder is fixed for ROS script
        remote_folder = "/home/ros_user/pbu_data/mockup"
        mesh_value = mesh_file_path

    # Build remote command:
    #   cd /home/winsys/pbu_marking_ros &&
    #   ./run_marking.sh --stage 2 --wall wall_2 --folder /home/ros_user/pbu_data/mockup
    #                    --excel test_points_tmp_out/..._wall_2.xlsx --mesh SIMTech_L_PBU.stl
    remote_command = (
        "cd /home/winsys/pbu_marking_ros && "
        "./run_marking.sh "
        "--stage 0 "
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
        { wall: "wall_2", rows: [...], excel: "/home/.../mockup/..._wall_2.xlsx" },
        { wall: "wall_3", rows: [...], excel: "/home/.../mockup/..._wall_3.xlsx" },
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

        # build row_totals & excel_map
        row_totals = {}
        excel_map = {}
        for w in body.walls:
            # wall id
            m = re.search(r"(\d+)", w.wall)
            if not m:
                continue
            wid = int(m.group(1))
            row_totals[wid] = len(w.rows)

            # per-wall Excel (trim absolute/semi-absolute to relative using folderdirectory)
            rel_excel = make_relative_excel(w.excel, body.folder)
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

        # reset per-wall state
        wall_point_count = {}
        bringup_success = {}
        wall_error = {}
        error_logs = {}

        # reset skipped tracking
        skipped_points = {}
        current_point = {}

        # init per-wall state
        for wid, _total in row_totals.items():
            wall_point_count[wid] = 0
            bringup_success[wid] = False
            wall_error[wid] = False
            error_logs[wid] = []

        first_label = wall_sequence[0]
        m = re.search(r"(\d+)", first_label)
        homecheck_pending = True
        homecheck_wall = int(m.group(1))
        homecheck_output = None

    # start first wall
    return {
            "ok": True,
            "queue": wall_sequence,
            "homeCheckRequired": True,
            "firstWall": homecheck_wall
        }



# -------------------------------------------------------------------
# PAUSE / CONTINUE
# -------------------------------------------------------------------
@app.post("/pause")
def pause():
    pause_flag.set()
    return {"paused": True}


@app.post("/continue")
def resume():
    global current_wall, queue_index

    pause_flag.clear()

    with state_lock:
        if current_wall is None:
            return {"resumed": False, "message": "No wall to continue from"}

        # Move queue forward ONLY ONCE
        idx = wall_sequence.index(f"wall_{current_wall}")
        queue_index = idx + 1

        current_wall = None
        running_flag.clear()

        # 🔐 REQUIRE HOME CHECK FOR NEXT WALL
        if queue_index < len(wall_sequence):
            next_label = wall_sequence[queue_index]
            m = re.search(r"(\d+)", next_label)
            next_wall = int(m.group(1))

            global homecheck_pending, homecheck_wall, homecheck_output
            homecheck_pending = True
            homecheck_wall = next_wall
            homecheck_output = None

            return {
                "resumed": True,
                "next_wall": next_wall,
                "homeCheckRequired": True
            }

    return {"resumed": True, "next_wall": None}



# -------------------------------------------------------------------
# RETRY API — rerun current or selected wall, no auto retry
# -------------------------------------------------------------------
@app.post("/retry")
def retry_wall(wall: Optional[int] = None):
    global current_wall, current_process, queue_index
    global skipped_points, current_point   # 🔥 ADD THIS

    with state_lock:
        if wall is None:
            if current_wall is None:
                raise HTTPException(400, "No wall specified and no current wall.")
            wall_id = current_wall
        else:
            wall_id = wall
        if current_process:
            try:
                current_process.kill()
            except:
                pass
            current_process = None

        if current_process is not None:
            raise HTTPException(400, "Cannot retry while a process is still running.")

        label = f"wall_{wall_id}"
        if label not in wall_sequence:
            raise HTTPException(400, f"Wall label {label} not in sequence.")

        # force queue_index to this wall
        queue_index = wall_sequence.index(label)

        # 🔥 RESET ALL WALL STATE (IMPORTANT)
        wall_point_count[wall_id] = 0
        bringup_success[wall_id] = False
        wall_error[wall_id] = False

        # 🔥 CLEAR SKIPPED TRACKING
        skipped_points[wall_id] = []     # 🔥 reset skipped
        wall_point_count[wall_id] = 0
        bringup_success[wall_id] = False
        wall_error[wall_id] = False

        homecheck_pending = True
        homecheck_wall = wall_id
        homecheck_output = None

        current_wall = None
        running_flag.clear()

        # keep error_logs so UI can show history if needed

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
            "homeCheckPending": homecheck_pending,
            "homeCheckWall": homecheck_wall,
            "homeCheckOutput": homecheck_output,
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
