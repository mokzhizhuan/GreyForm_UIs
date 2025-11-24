import os
import json
import threading
import subprocess
import time
from typing import Callable, Dict, Any, Optional, List

import rospy
from src.talker_listener.talker_listener import talker_node as RosPublisher


# ============================================================
# 🚨 GLOBAL SINGLETON PROTECTION
# Ensures FastAPI reload does NOT create new runner instances
# ============================================================

_GLOBAL_RUNNER_SINGLETON = None
_GLOBAL_RUNNER_LOCK = threading.Lock()


class ListenerNodeRunner:
    """
    Reload-safe, singleton-safe runner for your ROS listener node.

    This class guarantees:
      - Only ONE listener subprocess at a time
      - Hot reload will NOT spawn new ROS nodes
      - Safe shutdown and cleanup
      - Publishing always works through single talker node
    """

    # ========================================================
    # ❤️ SINGLETON CONSTRUCTOR
    # ========================================================
    def __new__(cls, *args, **kwargs):
        global _GLOBAL_RUNNER_SINGLETON

        with _GLOBAL_RUNNER_LOCK:
            if _GLOBAL_RUNNER_SINGLETON is None:
                instance = super().__new__(cls)
                _GLOBAL_RUNNER_SINGLETON = instance
                return instance

            # Reuse existing instance (reload-safe)
            return _GLOBAL_RUNNER_SINGLETON

    # ========================================================
    # ❤️ NORMAL INIT (runs once because of singleton)
    # ========================================================
    def __init__(self, status_cb: Optional[Callable[[str], None]] = None):

        # Avoid re-running __init__ on reload
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self.status_cb = status_cb or (lambda m: print(m, flush=True))

        # ROS talker node (safe to reuse)
        self.talker_node = RosPublisher.TalkerNode()

        # Listener process management
        self.process: Optional[subprocess.Popen] = None
        self.listener_started = False
        self._pump_thread: Optional[threading.Thread] = None
        self._wait_thread: Optional[threading.Thread] = None

        self.working_excel_path: Optional[str] = None

        self._emit("[runner] ListenerNodeRunner initialized (reload-safe)")

    # ========================================================
    # 🟢 Public API
    # ========================================================

    def run_listener_node(self) -> None:
        """Start the ROS listener node, but only once."""
        if self._process_is_running():
            self._emit("[runner] Listener already running.")
            self.listener_started = True
            return

        self._emit("[runner] Starting listener process...")
        self.listener_started = False

        threading.Thread(target=self._run_process, daemon=True).start()

    def stop_listener_node(self) -> None:
        """Stop listener process safely."""
        if self._process_is_running():
            self._emit("[runner] Stopping listener...")
            self.process.terminate()

            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._emit("[runner] Killing unresponsive listener...")
                self.process.kill()

        self.process = None
        self.listener_started = False

    # ========================================================
    # 🟠 File Selection
    # ========================================================
    def file_selection_data(self, directory: str, excelfile: str) -> str:
        """Publish file message and wait for listener to set /excel_path."""
        self.talker_node.publish_file_message(directory, excelfile)
        self._emit(f"[runner] Sent file message: {directory=} {excelfile=}")

        timeout = 25.0
        start = time.time()

        last_path = None

        while time.time() - start < timeout:
            try:
                path = rospy.get_param("/excel_path", "")
            except Exception as e:
                self._emit(f"[runner] rosparam error: {e}")
                path = ""

            if path and os.path.exists(path):
                last_path = path
                break

            time.sleep(0.25)

        if not last_path:
            raise RuntimeError(
                "Timed out waiting for working Excel. "
                "Is listener_node running and subscribed to /file_extraction_topic?"
            )

        self.working_excel_path = last_path
        self._emit(f"[runner] Working Excel path: {last_path}")
        return last_path

    # ========================================================
    # 🟣 Execute Wall
    # ========================================================
    def run_execution_data(self, rows: List[Dict[str, Any]]) -> None:
        self._emit(f"[runner] run_execution_data: {len(rows)} rows")

        for data in rows:
            wn = data.get("Wall Number")

            picked_position = [
                int(round(float(data.get("Position X", 0) or 0))),
                int(round(float(data.get("Position Y", 0) or 0))),
                int(round(float(data.get("Position Z", 0) or 0))),
            ]

            self._emit(
                f"[runner] Publishing selection: wall={wn} pos={picked_position}"
            )

            self.talker_node.publish_selection_message(
                wn, picked_position, data.get("Marking Type")
            )

        self._emit("[runner] Publishing all_done")
        self.talker_node.publish_all_done(True)

    # ========================================================
    # 🔧 Internal Helpers
    # ========================================================

    def _process_is_running(self) -> bool:
        return (
            self.process is not None
            and self.process.poll() is None
        )

    def _run_process(self) -> None:
        """Spawn the listener node and pump output."""
        if self._process_is_running():
            return

        env = os.environ.copy()
        env.setdefault("ROS_MASTER_URI", "http://localhost:11311")
        env.setdefault("ROS_HOSTNAME", "localhost")

        ros_setup = "/opt/ros/noetic/setup.bash"
        ws_setup = "/root/catkin_ws/newui_Greyform/devel/setup.bash"

        shell_cmd = f"""
            set -e
            echo '[listener] Env: ROS_MASTER_URI=$ROS_MASTER_URI'
            source "{ros_setup}"
            source "{ws_setup}"
            rosrun talker_listener listener_node.py
        """

        try:
            self.process = subprocess.Popen(
                ["bash", "-lc", shell_cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env,
            )

            self.listener_started = True

            # Pump logs
            if self.process.stdout:
                self._pump_thread = threading.Thread(
                    target=self._pump_output,
                    args=(self.process.stdout,),
                    daemon=True,
                )
                self._pump_thread.start()

            # Watcher thread
            self._wait_thread = threading.Thread(
                target=self._wait_for_exit, daemon=True
            )
            self._wait_thread.start()

        except Exception as e:
            self._emit(f"[runner] Failed to start process: {e}")
            self.process_finished()

    def _pump_output(self, pipe):
        try:
            for line in pipe:
                if line:
                    self._emit(line.rstrip())
        finally:
            pipe.close()

    def _wait_for_exit(self):
        rc = self.process.wait()
        msg = "[listener] exited OK" if rc == 0 else f"[listener] crashed (rc={rc})"
        self._emit(msg)
        self.process_finished()

    def process_finished(self) -> None:
        self.listener_started = False
        self._emit("[runner] listener process finished")

    # ========================================================
    # 🔊 Logging
    # ========================================================

    def _emit(self, text: str) -> None:
        try:
            self.status_cb(text)
        except Exception:
            print(text, flush=True)

