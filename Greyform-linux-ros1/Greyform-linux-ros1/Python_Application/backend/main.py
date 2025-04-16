from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import traceback

app = FastAPI()

# CORS configuration to allow all for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/api/launch_ui")
async def launch_ui():
    try:
        env = os.environ.copy()
        env["DISPLAY"] = ":0" 
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
                "message": f"UI failed: {error_message}",
            }
        return {"status": "success", "message": "UI launched"}
    except Exception as e:
        print("Exception launching Qt UI:", traceback.format_exc())
        return {"status": "error", "message": str(e)}


@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}
