import subprocess
import os

WS = "/root/catkin_ws/newui_Greyform"

def start_listener():
    setup_script = os.path.join(WS, "devel/setup.bash")

    command = f"bash -c 'source {setup_script} && rosrun talker_listener listener.py'"

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
        executable="/bin/bash",
    )

    return process