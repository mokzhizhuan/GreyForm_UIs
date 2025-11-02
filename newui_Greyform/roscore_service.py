# roscore_service.py
import os
import time
import socket
import subprocess
import shutil
import atexit
from typing import Optional

ROS_MASTER_URI = "http://localhost:11311"
ROS_PORT = 11311

_PROC: Optional[subprocess.Popen] = None  # singleton handle


def is_master_up(
    host: str = "127.0.0.1", port: int = ROS_PORT, timeout: float = 0.1
) -> bool:
    """Quick TCP check for the ROS master port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _wait_port_up(
    host: str = "127.0.0.1", port: int = ROS_PORT, timeout: float = 10.0
) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        if is_master_up(host, port, timeout=0.25):
            return True
        time.sleep(0.2)
    return False


def start_roscore(log: bool = True) -> None:
    """
    Start roscore if it's not already running and wait until it's reachable
    at http://localhost:11311. Reuses an existing master if found.
    """
    global _PROC

    if is_master_up():
        return  # already running somewhere (maybe another terminal)

    if shutil.which("roscore") is None:
        raise RuntimeError(
            "roscore not found on PATH. Did you `source /opt/ros/noetic/setup.bash`?"
        )

    env = os.environ.copy()
    env["ROS_MASTER_URI"] = ROS_MASTER_URI

    popen_kwargs = {}
    if os.name == "posix":
        popen_kwargs["preexec_fn"] = os.setsid  # new process group
    else:
        # If not using WSL, this creates a new console process group (optional).
        popen_kwargs["creationflags"] = getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        )

    stdout = None if log else subprocess.DEVNULL
    stderr = None if log else subprocess.DEVNULL

    _PROC = subprocess.Popen(
        ["roscore"], env=env, stdout=stdout, stderr=stderr, **popen_kwargs
    )

    if not _wait_port_up(timeout=15.0):
        # failed to come up; clean up
        try:
            _PROC.kill()
        except Exception:
            pass
        _PROC = None
        raise RuntimeError(f"Failed to start roscore on {ROS_MASTER_URI}")

    # ensure the master URI is in this process too (for child processes you spawn later)
    os.environ["ROS_MASTER_URI"] = ROS_MASTER_URI


def stop_roscore(grace_seconds: float = 2.0) -> None:
    """Stop the roscore we started (no-op if we didn't start it)."""
    global _PROC
    if _PROC is None:
        return
    if _PROC.poll() is not None:
        _PROC = None
        return
    try:
        _PROC.terminate()
        _PROC.wait(timeout=grace_seconds)
    except Exception:
        try:
            _PROC.kill()
        except Exception:
            pass
    finally:
        _PROC = None


@atexit.register
def _cleanup():
    stop_roscore()
