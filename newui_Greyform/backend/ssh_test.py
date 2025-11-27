import subprocess
import argparse
from pathlib import Path

process = subprocess.Popen(
        [
            "sshpass",
            "-p", "winsys",
            "ssh", "winsys@192.168.130.5",
            "python3", "/home/winsys/pbu_marking_ros/catkin_ws/detectwalls.py",
            "--filename", "/home/winsys/pbu_marking_ros/catkin_ws/PBU_TERRAHL2_working.xlsx"
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