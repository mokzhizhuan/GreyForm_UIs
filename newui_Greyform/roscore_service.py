import os
import signal
import socket
import subprocess
import time
from typing import Optional

# ============================================================
# ROS MASTER CONFIG
# ============================================================
ROS_MASTER_URI = "http://localhost:11311"
ROS_PORT = 11311

_PROC: Optional[subprocess.Popen] = None   # roscore process
_PGID: Optional[int] = None                # process group ID
_OWNED = False                             # did WE start roscore?


# ============================================================
# Check if ROS Master is alive
# ============================================================
def is_master_up(host: str = "127.0.0.1", port: int = ROS_PORT) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=0.3)
        s.close()
        return True
    except OSError:
        return False


# ============================================================
# Start roscore WITH SOURCED environment
# ============================================================
def start_roscore(log: bool = False):
    """
    Start roscore in a fully sourced ROS environment.

    FIXES:
    - Must start with `bash -c "source setup.bash && roscore"`
    - Must run in new process group so FastAPI worker won't kill it accidentally
    - Must avoid double-starting
    """
    global _PROC, _PGID, _OWNED

    # Already running?
    if is_master_up():
        print("[roscore_service] ROS master already running.")
        _OWNED = False
        return

    if _PROC is not None:
        print("[roscore_service] roscore process handle exists — checking...")
        if _PROC.poll() is None:
            print("[roscore_service] roscore already alive.")
            return
        else:
            _PROC = None  # stale handle

    print("[roscore_service] Starting ROS core...")

    # Use bash + sourced environment
    cmd = (
        "source /opt/ros/noetic/setup.bash && "
        "echo '[roscore_service] Environment sourced' && "
        "roscore"
    )

    # Launch in new process group
    _PROC = subprocess.Popen(
        ["bash", "-c", cmd],
        stdout=subprocess.PIPE if log else subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
        preexec_fn=os.setsid     # NEW PROCESS GROUP
    )

    _PGID = os.getpgid(_PROC.pid)
    _OWNED = True

    # Wait until master responds (max 10 sec)
    for _ in range(20):
        if is_master_up():
            print("[roscore_service] ROS master is online.")
            return
        time.sleep(0.3)

    raise RuntimeError("Failed to start roscore — ROS master never came online.")


# ============================================================
# Stop roscore safely
# ============================================================
def stop_roscore():
    global _PROC, _PGID, _OWNED

    if not _OWNED:
        print("[roscore_service] Not stopping roscore — not owned by this process.")
        return

    if _PROC is None:
        print("[roscore_service] No roscore process to stop.")
        return

    try:
        print("[roscore_service] Stopping ROS core...")
        os.killpg(_PGID, signal.SIGTERM)
    except Exception as e:
        print("[roscore_service] Error during stop:", e)

    _PROC = None
    _PGID = None
    _OWNED = False

    time.sleep(0.5)


# ============================================================
# Debugging Utility
# ============================================================
if __name__ == "__main__":
    print("Testing roscore start/stop...")
    start_roscore(log=True)
    time.sleep(2)
    print("Stopping roscore...")
    stop_roscore()
