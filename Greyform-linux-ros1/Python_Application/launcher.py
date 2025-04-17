import subprocess
import os
from threading import Thread
import time


def is_server_running(port=8000):
    try:
        # Use lsof to check if the port is in use
        result = subprocess.run(
            ["lsof", "-i", f"tcp:{port}"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        # If the return code is 0, the port is in use
        return result.returncode == 0
    except Exception as e:
        return False

# Function to start the FastAPI server
def start_fastapi():
    if is_server_running():
        print("FastAPI server is already running.")
        return
    try:
        print("Starting FastAPI server...")
        subprocess.Popen(
            ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
        )
    except Exception as e:
        print(f"Failed to start FastAPI: {str(e)}")

if __name__ == "__main__":
    fastapi_thread = Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    fastapi_thread.join()

