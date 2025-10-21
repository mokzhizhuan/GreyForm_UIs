#!/usr/bin/env python3
"""
Controller node that orchestrates wall processing and publishes the Excel + STL file.
It now waits for an initialization payload (JSON on /controller/init) OR uses existing ROS params.
"""

import os
import json
import rospy
import threading
from std_msgs.msg import String, Bool
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall

from talker_node import TalkerNode  # reuse existing publisher helpers

FILE_TOPIC   = "/file_extraction_topic"
SEL_TOPIC    = "/selection_wall_topic"
UI_STARTED   = "/ui/wall_started"
UI_DONE      = "/ui/wall_done"
UI_ALLDONE   = "/ui/all_done"
CTRL_INIT    = "/controller/init"   # <— NEW: API publishes JSON init here

class ControllerNode:
    def __init__(self):
        rospy.init_node("controller_node", anonymous=True)

        # Use TalkerNode publishers/helpers
        self.talker = TalkerNode()

        # Defaults from params (act as fallback if no /controller/init message is sent)
        self.expected_walls = rospy.get_param("~expected_walls", [])   # e.g., ["1","2","3","F"]
        self.typeselection  = rospy.get_param("~typeselection", "")
        self.excel_path     = rospy.get_param("~excel_path", None)
        self.stl_path       = rospy.get_param("~stl_path", None)

        self.latch_file_publish = rospy.get_param("~latch_file_publish", False)
        if self.latch_file_publish:
            self.latched_file_pub = rospy.Publisher(FILE_TOPIC, FileExtractionMessage, queue_size=1, latch=True)
        else:
            self.latched_file_pub = None

        # timing and retries
        self.per_wall_timeout = rospy.get_param("~per_wall_timeout", 8.0)
        self.per_wall_retries = rospy.get_param("~per_wall_retries", 2)
        self.delay_between_publishes = rospy.get_param("~delay_between_publishes", 0.2)

        # events/locks
        self._done_event = threading.Event()
        self._init_event = threading.Event()     # <— NEW: wait here until init arrives
        self._last_done_wall = None
        self._lock = threading.Lock()

        # Subscribe to UI done confirmations
        rospy.Subscriber(UI_DONE, String, self._ui_done_cb, queue_size=10)

        # Subscribe to controller init payload (JSON)
        rospy.Subscriber(CTRL_INIT, String, self._on_init_cb, queue_size=1)

        # If we already have an excel_path via params, consider initialized
        if self.excel_path:
            self._init_event.set()

        rospy.loginfo("[controller] Init; expected_walls=%r excel=%r stl=%r", self.expected_walls, self.excel_path, self.stl_path)

    # ---------- NEW: init message handling ----------
    def _on_init_cb(self, msg: String):
        """
        Expected JSON example:
        {
          "excel_path": "/media/USB/master.xlsx",
          "stl_path": "/media/USB/empty_pbu.stl",        # optional
          "typeselection": "Stage2",                      # optional
          "expected_walls": ["1","2","3","4","F"]         # optional
        }
        """
        try:
            payload = json.loads(msg.data or "{}")
        except Exception as e:
            rospy.logerr("[controller] Bad JSON on %s: %s", CTRL_INIT, e)
            return

        excel_path = payload.get("excel_path")
        stl_path   = payload.get("stl_path")
        typeselection = payload.get("typeselection")
        expected_walls = payload.get("expected_walls")

        # Update internal state from payload if provided
        if excel_path:
            self.excel_path = excel_path
            rospy.set_param("~excel_path", self.excel_path)  # optional visibility

        if stl_path is not None:
            self.stl_path = stl_path
            rospy.set_param("~stl_path", self.stl_path)

        if typeselection is not None:
            self.typeselection = str(typeselection)
            rospy.set_param("~typeselection", self.typeselection)

        if expected_walls is not None:
            # Normalize to list of strings
            try:
                self.expected_walls = [str(w) for w in list(expected_walls)]
                rospy.set_param("~expected_walls", self.expected_walls)
            except Exception:
                rospy.logwarn("[controller] expected_walls in init is not a list; ignoring")

        rospy.loginfo("[controller] Received init: excel=%r stl=%r type=%r walls=%r",
                      self.excel_path, self.stl_path, self.typeselection, self.expected_walls)

        # Signal run() that we’re good to start
        if self.excel_path:
            self._init_event.set()
        else:
            rospy.logwarn("[controller] Init received but no excel_path set; still waiting...")

    # ------------------------------------------------

    def publish_file_message(self):
        if not self.excel_path:
            rospy.logwarn("[controller] No excel_path; skipping file publish")
            return

        # Try publishing real STL if configured
        if self.stl_path and os.path.isfile(self.stl_path):
            try:
                rospy.loginfo("[controller] Publishing STL (%s) + Excel (%s)", self.stl_path, self.excel_path)
                self.talker.publish_file_message(self.stl_path, self.excel_path)
                if self.latch_file_publish and self.latched_file_pub:
                    latched_msg = FileExtractionMessage()
                    with open(self.stl_path, "rb") as f:
                        latched_msg.stl_data = f.read()
                    latched_msg.excelfile = str(self.excel_path)
                    self.latched_file_pub.publish(latched_msg)
                rospy.sleep(self.delay_between_publishes)
                return
            except Exception as e:
                rospy.logerr("[controller] STL publish failed: %s", e)

        # Orchestration-only message
        msg = FileExtractionMessage()
        msg.stl_data = b""
        msg.excelfile = str(self.excel_path)
        rospy.loginfo("[controller] Publishing Excel path via FileExtractionMessage: %s", msg.excelfile)
        self.talker.file_pub.publish(msg)
        if self.latch_file_publish and self.latched_file_pub:
            self.latched_file_pub.publish(msg)
        rospy.sleep(self.delay_between_publishes)

    def _ui_done_cb(self, msg):
        wall = str(msg.data).strip()
        rospy.loginfo_throttle(5, "[controller] Received UI done for %r", wall)
        with self._lock:
            self._last_done_wall = wall
            self._done_event.set()

    def _publish_selection(self, wall):
        self.talker.publish_selection_message(
            wallselection=wall, picked_position=[], typeselection=self.typeselection
        )
        rospy.loginfo("[controller] Published selection for wall=%r", wall)
        rospy.sleep(self.delay_between_publishes)

    def run(self):
        # === NEW: wait for initialization ===
        if not self._init_event.is_set():
            rospy.loginfo("[controller] Waiting for init on %s or param ~excel_path ...", CTRL_INIT)
            while not rospy.is_shutdown() and not self._init_event.wait(timeout=0.2):
                pass
        if rospy.is_shutdown():
            return

        # Now initialized → publish file info first
        self.publish_file_message()

        if not self.expected_walls:
            rospy.loginfo("[controller] No expected_walls; nothing to do.")
            return

        for wall in self.expected_walls:
            if rospy.is_shutdown():
                return
            success = False
            for attempt in range(1, self.per_wall_retries + 2):
                rospy.loginfo("[controller] Processing wall %r (attempt %d)", wall, attempt)
                self._done_event.clear()
                with self._lock:
                    self._last_done_wall = None

                self._publish_selection(wall)

                waited = self._done_event.wait(timeout=self.per_wall_timeout)
                if waited:
                    with self._lock:
                        last = self._last_done_wall
                    if last == str(wall):
                        rospy.loginfo("[controller] Wall %r confirmed done", wall)
                        success = True
                        break
                    else:
                        rospy.logwarn("[controller] Got done for %r while waiting for %r; retrying", last, wall)
                else:
                    rospy.logwarn("[controller] Timeout for wall %r (attempt %d)", wall, attempt)

                rospy.sleep(0.5)

            if not success:
                rospy.logerr("[controller] Failed wall %r after retries; continuing", wall)

        rospy.loginfo("[controller] All walls attempted; publishing /ui/all_done")
        self.talker.publish_all_done(is_done=True)
        rospy.loginfo("[controller] Controller finished.")

def main():
    node = ControllerNode()
    node.run()
    rospy.spin()

if __name__ == "__main__":
    main()
