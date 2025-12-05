import subprocess
import argparse
from pathlib import Path

process = subprocess.Popen(
        [
        "sshpass", "-p", "winsys",
        "ssh", "winsys@192.168.130.5",
        "python3",
        "/home/winsys/pbu_marking_ros/homeposcheck.py",
        "--file", "/home/winsys/pbu_marking_ros/pbu_data/mockup/poses.json",
        "--target", "wall_2",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

lines = [line.rstrip("\n") for line in process.stdout]
process.wait()
print(lines)
if process.returncode != 0:
    print(f"read_directory failed (code {process.returncode}")