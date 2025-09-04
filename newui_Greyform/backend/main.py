from fastapi import FastAPI, Form
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


@app.post("/api/launch_ui")
async def launch_ui(usb_path: str = Form(...)):
    try:
        env = os.environ.copy()
        env["DISPLAY"] = ":0"

        args = [
            "python3", "mainwindow.py",
            "UI_Design/mainframe.ui",
            "output.stl",
            "floor.stl",
            "Greyform TERRAHL2(JMB)-T1a BOM Checklist 20231211.xlsx",
            "PBU_TERRAHL2(final).xlsx",
            "--usb_path", usb_path,
        ]
        process = subprocess.Popen(
            args,
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
        return {"status": "success", "message": "UI launched", "output": stdout.decode("utf-8")}
    except Exception as e:
        print("Exception launching Qt UI:", traceback.format_exc())
        return {"status": "error", "message": str(e)}


@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}
