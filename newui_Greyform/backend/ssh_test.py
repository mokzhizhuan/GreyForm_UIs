import subprocess
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--rootdir", type=Path, default=Path.cwd())
args = parser.parse_args()

ROOTDIR = args.rootdir.resolve()
print("ROOTDIR =", ROOTDIR)
"""process = subprocess.Popen(
    ["sshpass", "-p", "winsys", "ssh", "winsys@192.168.131.5", "ls", "/home/"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

for line in process.stdout:
    print(line)"""