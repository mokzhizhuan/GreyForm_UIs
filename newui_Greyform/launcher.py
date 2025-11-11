#!/usr/bin/env python3
import os
import sys
import time
import socket
import signal
import subprocess
from pathlib import Path

HOST     = os.getenv("HOST", "0.0.0.0")
PORT     = int(os.getenv("PORT", "800"))
APP      = os.getenv("APP", "backend.main:app")
WORKERS  = int(os.getenv("WORKERS", "1"))          # uvicorn --workers
RELOAD   = os.getenv("RELOAD", "0") == "1"         # uvicorn --reload (dev)
EXTRA    = os.getenv("UVICORN_EXTRA", "")          # any extra flags
CHECK_HOSTS = [
    os.getenv("CHECK_HOST", "127.0.0.1"),
    "localhost",
]

CWD     = Path(__file__).parent.resolve()
PIDFILE = Path("/tmp/uvicorn_backend_main.pid")
LOGFILE = Path("/tmp/uvicorn_backend_main.log")

def is_listening(hosts=CHECK_HOSTS, port=PORT, timeout=0.25) -> bool:
    for h in hosts:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((h, port)) == 0:
                    return True
        except Exception:
            continue
    return False

def read_pid():
    try:
        return int(PIDFILE.read_text().strip())
    except Exception:
        return None

def is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False

def _build_cmd():
    cmd = [
        sys.executable, "-m", "uvicorn", APP,
        "--host", HOST,
        "--port", str(PORT),
        "--workers", str(WORKERS),
        "--proxy-headers",
        "--forwarded-allow-ips", "*",
        "--log-level", "info",
    ]
    if RELOAD:
        cmd.append("--reload")
    if EXTRA.strip():
        cmd.extend(EXTRA.split())
    return cmd

def start():
    if is_listening():
        print(f"FastAPI already listening on {HOST}:{PORT}")
        return 0
    pid = read_pid()
    if pid and not is_alive(pid):
        PIDFILE.unlink(missing_ok=True)
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    log_f = open(LOGFILE, "ab", buffering=0)
    cmd = _build_cmd()
    print(f"Starting: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        cwd=str(CWD),
        env=os.environ.copy(),
        stdout=log_f,
        stderr=subprocess.STDOUT,
        start_new_session=True,      # detach
    )
    PIDFILE.write_text(str(proc.pid))
    for _ in range(40):
        if is_listening():
            print(f"Started (pid {proc.pid}) on {HOST}:{PORT}")
            return 0
        time.sleep(0.1)
    try:
        tail = LOGFILE.read_bytes()[-2000:].decode("utf-8", "ignore")
    except Exception:
        tail = "<no log>"
    print("WARN: server did not become ready in time.\n--- LOG TAIL ---\n" + tail)
    return 1

def stop(timeout=5):
    pid = read_pid()
    if not pid:
        os.system(f"fuser -k {PORT}/tcp >/dev/null 2>&1 || true")
        print("Stopped (no pidfile).")
        return 0
    if not is_alive(pid):
        PIDFILE.unlink(missing_ok=True)
        print("Stopped (stale pidfile).")
        return 0
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        PIDFILE.unlink(missing_ok=True)
        print("Stopped.")
        return 0
    t0 = time.time()
    while time.time() - t0 < timeout:
        if not is_alive(pid):
            PIDFILE.unlink(missing_ok=True)
            print("Stopped.")
            return 0
        time.sleep(0.2)
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    PIDFILE.unlink(missing_ok=True)
    print("Force-stopped.")
    return 0

def restart():
    stop()
    return start()

def status():
    pid = read_pid()
    if pid and is_alive(pid):
        print(f"Running (pid {pid}) on {HOST}:{PORT}")
        return 0
    print("Not running")
    return 3

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    if cmd == "start":
        sys.exit(start())
    elif cmd == "stop":
        sys.exit(stop())
    elif cmd == "restart":
        sys.exit(restart())
    elif cmd == "status":
        sys.exit(status())
    else:
        print("Usage: python3 launcher.py [start|stop|restart|status]")
        sys.exit(1)

if __name__ == "__main__":
    main()