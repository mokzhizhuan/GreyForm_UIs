# roscore_service.py
import os, signal, socket, subprocess, atexit, time, shutil
from typing import Optional

ROS_MASTER_URI = "http://localhost:11311"
ROS_PORT = 11311

_PROC: Optional[subprocess.Popen] = None
_PGID: Optional[int] = None
_OWNED: bool = False

def is_master_up(host="127.0.0.1", port=ROS_PORT, timeout=0.1) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def _wait_port_up(host="127.0.0.1", port=ROS_PORT, timeout=10.0) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        if is_master_up(host, port, timeout=0.25):
            return True
        time.sleep(0.2)
    return False

def start_roscore(log: bool = True) -> None:
    """Start roscore if not running; mark it owned and remember its process group."""
    global _PROC, _PGID, _OWNED

    # If something is already listening -> we don't own it.
    if is_master_up():
        _PROC = None
        _PGID = None
        _OWNED = False
        return

    if shutil.which("roscore") is None:
        raise RuntimeError("roscore not found. Did you `source /opt/ros/noetic/setup.bash`?")

    env = os.environ.copy()
    env["ROS_MASTER_URI"] = ROS_MASTER_URI
    # also helpful:
    env.setdefault("ROS_HOSTNAME", "localhost")

    # Start in a new process group so we can kill the whole tree later.
    popen_kwargs = {}
    if os.name == "posix":
        popen_kwargs["preexec_fn"] = os.setsid          # new session -> new pgid
    else:
        popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

    stdout = None if log else subprocess.DEVNULL
    stderr = None if log else subprocess.DEVNULL

    _PROC = subprocess.Popen(["roscore"], env=env, stdout=stdout, stderr=stderr, **popen_kwargs)
    _PGID = os.getpgid(_PROC.pid) if _PROC.pid else None
    _OWNED = True

    if not _wait_port_up(timeout=15.0):
        try:
            if _PGID is not None and os.name == "posix":
                os.killpg(_PGID, signal.SIGKILL)
            elif _PROC and _PROC.poll() is None:
                _PROC.kill()
        finally:
            _PROC = None
            _PGID = None
            _OWNED = False
        raise RuntimeError(f"Failed to start roscore on {ROS_MASTER_URI}")

    os.environ["ROS_MASTER_URI"] = ROS_MASTER_URI  # set for this process too

def stop_roscore(grace_seconds: float = 2.0) -> None:
    """Stop ONLY the roscore we started. No-op if it's external."""
    global _PROC, _PGID, _OWNED
    if not _OWNED or _PROC is None:
        return  # external master or nothing to stop

    try:
        if _PROC.poll() is None:
            if _PGID is not None and os.name == "posix":
                os.killpg(_PGID, signal.SIGTERM)
            else:
                _PROC.terminate()

            t0 = time.time()
            while time.time() - t0 < grace_seconds:
                if _PROC.poll() is not None:
                    break
                time.sleep(0.1)

            if _PROC.poll() is None:
                if _PGID is not None and os.name == "posix":
                    os.killpg(_PGID, signal.SIGKILL)
                else:
                    _PROC.kill()
    finally:
        _PROC = None
        _PGID = None
        _OWNED = False

@atexit.register
def _cleanup():
    try:
        stop_roscore()
    except Exception:
        pass