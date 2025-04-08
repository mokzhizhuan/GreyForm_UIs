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

def start_fastapi():
    os.system("uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1")

@app.get("/api/launch_qt")
async def launch_qt():
    try:
        # Set the display environment variable explicitly
        env = os.environ.copy()
        env["DISPLAY"] = ":0"  # Adjust as needed

        # Launch the Qt UI as a separate process and capture errors
        process = subprocess.Popen(["python3", "mainwindow.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            error_message = stderr.decode("utf-8")
            print(f"Error launching Qt UI: {error_message}")
            return {"status": "error", "message": error_message}

        return {"status": "success", "message": "Qt UI launched"}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}
