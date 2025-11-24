# backend/build_subapp.py
import os, shlex, signal, time, subprocess
from pathlib import Path
from fastapi import FastAPI, HTTPException

build_app = FastAPI(title="Build API")

WS = Path("/root/catkin_ws/newui_Greyform")
SCRIPT = WS / "safe_catkin_make.sh"
PIDFILE = WS / ".build_pid"
LOCKFILE = WS / ".build_lock"
LOGFILE = WS / ".build_log.txt"


def _is_running() -> bool:
    if PIDFILE.exists():
        try:
            pid = int(PIDFILE.read_text().strip())
            os.kill(pid, 0)
            return True
        except Exception:
            return False
    return False


@build_app.post("/start")
def start_build():
    if not SCRIPT.exists():
        raise HTTPException(404, f"Script not found: {SCRIPT}")
    if LOCKFILE.exists() or _is_running():
        raise HTTPException(409, "A build is already running")

    LOGFILE.write_text("")  # reset log
    cmd = f"bash -lc 'source /opt/ros/noetic/setup.bash && {shlex.quote(str(SCRIPT))} 2>&1 | tee -a {shlex.quote(str(LOGFILE))}'"

    proc = subprocess.Popen(
        cmd,
        shell=True,
        cwd=str(WS),
        preexec_fn=os.setsid,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        env={**os.environ, "ROS_WORKSPACE": str(WS)},
    )
    LOCKFILE.write_text(str(time.time()))
    PIDFILE.write_text(str(proc.pid))
    return {"ok": True, "pid": proc.pid}


@build_app.get("/status")
def status():
    return {
        "running": _is_running(),
        "pid": (int(PIDFILE.read_text()) if _is_running() else None),
    }


@build_app.get("/log")
def log(tail: int = 5000):
    if not LOGFILE.exists():
        return {"log": ""}
    data = LOGFILE.read_text()
    return {"log": data[-tail:] if len(data) > tail else data}


@build_app.post("/stop")
def stop():
    if not _is_running():
        for f in (PIDFILE, LOCKFILE):
            try:
                f.unlink()
            except FileNotFoundError:
                pass
        return {"ok": True, "message": "No build running"}

    pid = int(PIDFILE.read_text().strip())
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        time.sleep(0.5)
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
    except ProcessLookupError:
        pass
    for f in (PIDFILE, LOCKFILE):
        try:
            f.unlink()
        except FileNotFoundError:
            pass
    return {"ok": True}
