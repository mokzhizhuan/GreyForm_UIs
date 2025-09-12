# launcher.py
import os
import sys
import time
import socket
import signal
import subprocess
from pathlib import Path

HOST = "0.0.0.0"
PORT = 8000
APP = "backend.main:app"                 # matches backend/main.py -> app
PIDFILE = Path("/tmp/uvicorn_backend_main.pid")
CWD = Path(__file__).parent.resolve()    # project root

def is_listening(host=HOST, port=PORT, timeout=0.25) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0

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

def start():
    if is_listening():
        print(f"FastAPI already running on {HOST}:{PORT}")
        return 0
    cmd = [
        sys.executable, "-m", "uvicorn", APP,
        "--host", HOST, "--port", str(PORT),
        "--workers", "1",
        # "--reload",                      # uncomment in dev if you want auto-reload
    ]
    print("Starting:", " ".join(cmd))
    proc = subprocess.Popen(
        cmd,
        cwd=str(CWD),
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        start_new_session=True,          # detach from this shell
    )
    PIDFILE.write_text(str(proc.pid))
    # wait briefly until port opens
    for _ in range(40):
        if is_listening():
            return 0
        time.sleep(0.1)
    return 0

def stop(timeout=5):
    pid = read_pid()
    if not pid:
        os.system("fuser -k 8000/tcp >/dev/null 2>&1 || true")
        return 0
    if not is_alive(pid):
        PIDFILE.unlink(missing_ok=True)
        return 0
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        PIDFILE.unlink(missing_ok=True)
        return 0
    # wait for exit
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
    return 0

def restart():
    stop()
    return start()

def status():
    pid = read_pid()
    if pid and is_alive(pid):
        print(f"Running (pid {pid}) on {HOST}:{PORT}")
    else:
        print("Not running")
    return 0

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
