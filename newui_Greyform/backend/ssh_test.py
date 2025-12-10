import subprocess

# This is the *remote* command that ssh will run
remote_command = (
    "cd /home/winsys/pbu_marking_ros; "
    "./run_marking.sh "
    "--folder /home/ros_user/pbu_data/mockup "
    "--excel PBU_TERRAHL2_out/PBU_TERRAHL2_out1_wall_2.xlsx "
    "--mesh SIMTech_L_PBU.stl "
    "--stage 2 "
    "--wall wall_2"
)

cmd = [
    "sshpass", "-p", "winsys",
      "ssh", "winsys@192.168.130.5",
    remote_command,
]

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,  # merge stderr into stdout
    text=True,
)

lines = []
for line in process.stdout:
    line = line.rstrip("\n")
    print(line)          # stream to console (optional)
    lines.append(line)   # also keep in a list

process.wait()

print("---- ALL LINES ----")
print(lines)

if process.returncode != 0:
    print(f"run_marking.sh failed (code {process.returncode})")
