import subprocess

process = subprocess.Popen(
        [
            "sshpass",
            "-p",
            "winsys",
            "ssh",
            "winsys@192.168.1.5",
            "python3 ",
            "/home/winsys/pbu_marking_ros/directorysearch.py ",
            "--directory ",
            "/home/winsys/pbu_marking_ros/pbu_data/",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
lines = [line.rstrip("\n") for line in process.stdout]
process.wait()
if process.returncode != 0:
    print(f"joint_target failed (code {process.returncode})")

print("-------- ALL LINES ---")
for l in lines:
    print(l)