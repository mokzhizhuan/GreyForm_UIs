import os
import json
import threading
import subprocess
from typing import Callable, Iterable, Dict, Any, Optional

from src.talker_listener.talker_listener import talker_node as RosPublisher


class ListenerNodeRunner:
    def __init__(self, file: str, status_cb: Optional[Callable[[str], None]] = None):
        self.file = file
        self.status_cb = status_cb or (lambda m: print(m, flush=True))
        self.listener_started = False
        self.spacing = "\n"
        self.talker_node = RosPublisher.TalkerNode()
        self.process: Optional[subprocess.Popen] = None
        self._pump_thread: Optional[threading.Thread] = None
        self._wait_thread: Optional[threading.Thread] = None

    def run_listener_node(self) -> None:
        if self.listener_started:
            self._emit("Listener already started.")
            return
        try:
            threading.Thread(target=self._run_process, daemon=True).start()
            self.send_status(
                "The robot is now correctly centered and is ready to mark the wall.",
                icon="check.png",
            )
            self.listener_started = True
        except Exception as e:
            self._emit(f"Status: Error - {e!r}")

    def stop_listener_node(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                self._emit("Please wait, robot is calculating its position")
            except subprocess.TimeoutExpired:
                self.process.kill()
                self._emit("Please wait, robot is calculating its position")
        self.process = None

    def run_execution_data(self, rows, excel_path):
        self.talker_node.publish_file_message(self.file, excel_path)

        for data in rows:
            wn = data.get("Wall Number")

            picked_position = [
                int(round(float(data.get("Position X", 0) or 0))),
                int(round(float(data.get("Position Y", 0) or 0))),
                int(round(float(data.get("Position Z", 0) or 0))),
            ]
            markingtype = data.get("Marking Type")

            # Publish the STARTED event
            self.talker_node.publish_selection_message(wn, picked_position, markingtype)
        self.talker_node.publish_all_done(True)

    def run_jointvalues(self, jointvalues, placementcoord):
        self.talker_node.publish_jointvalues_msg(jointvalues, placementcoord)
        

    def _run_process(self) -> None:
        env = os.environ.copy()
        env["ROS_MASTER_URI"] = env.get("ROS_MASTER_URI", "http://localhost:11311")
        env["ROS_HOSTNAME"] = env.get("ROS_HOSTNAME", "localhost")

        ros_setup = "/opt/ros/noetic/setup.bash"
        ws_setup = "/root/catkin_ws/newui_Greyform/devel/setup.bash"

        shell_cmd = f"""
            set -e
            source "{ros_setup}"
            source "{ws_setup}"
            rosrun talker_listener listener_node.py
        """

        try:
            self.process = subprocess.Popen(
                ["bash", "-lc", shell_cmd],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,  # silence stderr as per original
                bufsize=1,
                universal_newlines=True,
            )

            # Pump stdout lines to status callback
            if self.process.stdout:
                self._pump_thread = threading.Thread(
                    target=self._pump_out, args=(self.process.stdout,), daemon=True
                )
                self._pump_thread.start()

            # Wait for process exit in the background
            def _waiter():
                rc = self.process.wait()
                msg = "Node exited normally." if rc == 0 else f"Node exited with code {rc}."
                self._emit(msg)
                self.process_finished()

            self._wait_thread = threading.Thread(target=_waiter, daemon=True)
            self._wait_thread.start()

        except Exception as e:
            self._emit(f"Process failed: {e!r}")
            self.process_finished()

    def _pump_out(self, pipe):
        try:
            for line in pipe:
                if line:
                    self._emit(line.rstrip())
        finally:
            try:
                pipe.close()
            except Exception:
                pass


    def send_status(self, text: str, icon: Optional[str] = None, gif: Optional[str] = None) -> None:
        """Send a structured or plain status message through the callback."""
        if icon or gif:
            payload = {"text": text}
            if icon:
                payload["icon"] = icon
            if gif:
                payload["gif"] = gif
            self._emit(json.dumps(payload))
        else:
            self._emit(text)

    def process_finished(self) -> None:
        self.send_status(
            "The robot is now correctly centered and is ready to mark the wall.",
            icon="check.png",
        )
        self.listener_started = True

    def _emit(self, text: str) -> None:
        try:
            self.status_cb(text)
        except Exception:
            # Always avoid crashing on user-provided callbacks
            print(text, flush=True)
                         