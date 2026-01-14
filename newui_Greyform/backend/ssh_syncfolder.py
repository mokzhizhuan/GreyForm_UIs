import subprocess

LOCAL_FOLDER = "/root/catkin_ws/newui_Greyform/PBU_TERRAHL2"  # offline test
REMOTE_FOLDER = "/home/winsys/pbu_data/mockup"

cmd = [
    "sshpass",
    "-p",
    "winsys",
    "rsync",
    "-av",
    "--progress",
    LOCAL_FOLDER + "/",  # send contents
    f"winsys@192.168.130.5:{REMOTE_FOLDER}",
]

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

for line in process.stdout:
    print(line.rstrip())

process.wait()

if process.returncode != 0:
    raise RuntimeError("Folder transfer failed")
