from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os

app = FastAPI()

# CORS configuration to allow all for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/api/start-fastapi")
def start_fastapi():
    try:
        env = os.environ.copy()
        env["DISPLAY"] = ":0"  # Adjust if needed
        process = subprocess.Popen(
            ["python3", "launcher.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            error_message = stderr.decode("utf-8")
            print(f"[launcher.py ERROR]: {error_message}")
            return {
                "status": "error",
                "message": f"launcher.py failed: {error_message}",
            }
        return {"status": "success", "message": "FastAPI started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/launch_qt")
async def launch_qt():
    try:
        env = os.environ.copy()
        env["DISPLAY"] = ":0"  # Adjust if needed
        # Then run mainwindow.py
        process = subprocess.Popen(
            ["python3", "mainwindow.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            error_message = stderr.decode("utf-8")
            print(f"[mainwindow.py ERROR]: {error_message}")
            return {
                "status": "error",
                "message": f"mainwindow.py failed: {error_message}",
            }
        return {"status": "success", "message": "Qt UI launched"}

    except Exception as e:
        import traceback

        print("Exception launching Qt UI:", traceback.format_exc())
        return {"status": "error", "message": str(e)}


@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}
