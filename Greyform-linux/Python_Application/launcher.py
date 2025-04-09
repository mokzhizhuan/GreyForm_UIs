import subprocess
import os


def start_fastapi():
    env = os.environ.copy()

    subprocess.Popen(
        [
            "uvicorn",
            "backend.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--workers",
            "1",
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("✅ FastAPI launched")


if __name__ == "__main__":
    start_fastapi()
