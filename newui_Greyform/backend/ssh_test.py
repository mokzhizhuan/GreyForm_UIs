import subprocess

process = subprocess.Popen(
    ["ssh", "winsys@192.168.131.5", "ls", "/root/"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

for line in process.stdout:
    print(line)