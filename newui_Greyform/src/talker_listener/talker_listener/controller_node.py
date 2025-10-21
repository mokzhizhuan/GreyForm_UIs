#!/usr/bin/env python3
"""
Controller node that orchestrates wall processing and publishes the Excel + STL file.
It waits for an initialization payload (JSON on /controller/init) OR uses existing ROS params.
Also republishes CP JSON on a dedicated, latched topic /cp/json for the camera driver.
"""

import os
import json
import threading
from typing import List

import rospy
from std_msgs.msg import String, Bool
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall
from talker_node import TalkerNode  # reuse existing publisher helpers

# Topics
FILE_TOPIC   = "/file_extraction_topic"
SEL_TOPIC    = "/selection_wall_topic"
UI_STARTED   = "/ui/wall_started"
UI_DONE      = "/ui/wall_done"
UI_ALLDONE   = "/ui/all_done"
CTRL_INIT    = "/controller/init"   # API publishes init JSON here
CP_TOPIC     = "/cp/json"           # dedicated CP JSON topic (latched)

class ControllerNode:
    def __init__(self):
        rospy.init_node("controller_node", anonymous=True)
        # Publishers/helpers
        self.talker = TalkerNode()
        self.cp_pub = rospy.Publisher(CP_TOPIC, String, queue_size=1, latch=True)
        # Params (act as fallbacks if no init message is received)
        self.expected_walls = rospy.get_param("~expected_walls", [])    # e.g. ["1","2","3"]
        self.typeselection  = rospy.get_param("~typeselection", "")
        self.excel_path     = rospy.get_param("~excel_path", None)
        self.stl_path       = rospy.get_param("~stl_path", None)
        self.model_sides    = rospy.get_param("~model_sides", None)     # 4 or 6 (optional)
        # Optional latched file publisher
        self.latch_file_publish = rospy.get_param("~latch_file_publish", False)
        self.latched_file_pub = (rospy.Publisher(FILE_TOPIC, FileExtractionMessage, queue_size=1, latch=True)
                                 if self.latch_file_publish else None)
        # Timing
        self.per_wall_timeout = rospy.get_param("~per_wall_timeout", 8.0)
        self.per_wall_retries = rospy.get_param("~per_wall_retries", 2)
        self.delay_between_publishes = rospy.get_param("~delay_between_publishes", 0.2)
        # State & sync
        self._done_event = threading.Event()
        self._init_event = threading.Event()
        self._last_done_wall = None
        self._lock = threading.Lock()
        self.cp_json = None  # cache of CP JSON if provided in init
        # Subscriptions
        rospy.Subscriber(UI_DONE, String, self._ui_done_cb, queue_size=10)
        rospy.Subscriber(CTRL_INIT, String, self._on_init_cb, queue_size=1)
        # If params already provide enough info, derive walls if needed and mark initialized
        if self.excel_path and (self.expected_walls or self.model_sides):
            if not self.expected_walls and self.model_sides:
                self.expected_walls = self._compute_walls(int(self.model_sides))
                rospy.set_param("~expected_walls", self.expected_walls)
            self._init_event.set()
        rospy.loginfo("[controller] Init; excel=%r stl=%r type=%r walls=%r sides=%r",
                      self.excel_path, self.stl_path, self.typeselection,
                      self.expected_walls, self.model_sides)

    # ---------- helpers ----------
    @staticmethod
    def _compute_walls(model_sides: int) -> List[str]:
        if model_sides not in (4, 6):
            rospy.logwarn("[controller] model_sides must be 4 or 6; got %r", model_sides)
            return []
        return [str(i) for i in range(1, model_sides + 1)]

    # ---------- subscribers ----------
    def _on_init_cb(self, msg: String):
        """
        Expected JSON:
        {
        "excel_path": "/media/USB/master.xlsx",
        "stl_path": "/media/USB/empty_pbu.stl",    # optional
        "typeselection": "Stage2",                 # optional
        "expected_walls": ["1","2","3","4"],       # optional; else use model_sides
        "model_sides": 4,                          # optional; used when expected_walls absent
        "cp_json": {...}                           # optional; forwarded to /cp/json
        }
        """
        try:
            payload = json.loads(msg.data or "{}")
        except Exception as e:
            rospy.logerr("[controller] Bad JSON on %s: %s", CTRL_INIT, e)
            return
        # 1) Read fields
        excel_path     = payload.get("excel_path")
        stl_path       = payload.get("stl_path")
        typeselection  = payload.get("typeselection")
        model_sides    = payload.get("model_sides")
        expected_walls = payload.get("expected_walls")
        cp_json        = payload.get("cp_json")
        # 2) Apply to state (and mirror as rosparams if you like)
        if excel_path:
            self.excel_path = excel_path
            rospy.set_param("~excel_path", self.excel_path)
        if stl_path is not None:
            self.stl_path = stl_path
            rospy.set_param("~stl_path", self.stl_path)
        if typeselection is not None:
            self.typeselection = str(typeselection)
            rospy.set_param("~typeselection", self.typeselection)
        if model_sides is not None:
            try:
                self.model_sides = int(model_sides)
                rospy.set_param("~model_sides", self.model_sides)
            except Exception:
                rospy.logwarn("[controller] model_sides not an int: %r", model_sides)
        # 3) Prefer explicit walls; else derive from model_sides
        if expected_walls is not None:
            try:
                self.expected_walls = [str(w) for w in list(expected_walls)]
                rospy.set_param("~expected_walls", self.expected_walls)
            except Exception:
                rospy.logwarn("[controller] expected_walls is not a list; ignoring")
        elif self.model_sides:
            self.expected_walls = self._compute_walls(int(self.model_sides))
            rospy.set_param("~expected_walls", self.expected_walls)
        # 4) Forward CP JSON to separate topic (latched) if provided
        if cp_json is not None:
            self.cp_json = cp_json
            try:
                self.cp_pub.publish(String(data=json.dumps(self.cp_json, ensure_ascii=False)))
                rospy.loginfo("[controller] Published CP JSON to %s (sheets=%d)",
                            CP_TOPIC, len(self.cp_json or {}))
            except Exception as e:
                rospy.logerr("[controller] Failed to publish CP JSON: %s", e)
        rospy.loginfo("[controller] Init received: excel=%r, stl=%r, type=%r, walls=%r, sides=%r",
                    self.excel_path, self.stl_path, self.typeselection,
                    self.expected_walls, self.model_sides)
        # 5) Signal run() to start
        if self.excel_path and self.expected_walls:
            self._init_event.set()
        else:
            rospy.logwarn("[controller] Waiting: need excel_path AND expected_walls/model_sides.")


    def _ui_done_cb(self, msg):
        wall = str(msg.data).strip()
        rospy.loginfo_throttle(5, "[controller] Received UI done for %r", wall)
        with self._lock:
            self._last_done_wall = wall
            self._done_event.set()

    # ---------- publishes ----------
    def publish_file_message(self):
        if not self.excel_path:
            rospy.logwarn("[controller] No excel_path; skipping file publish")
            return
        # Try publishing real STL if configured
        if self.stl_path and os.path.isfile(self.stl_path):
            try:
                rospy.loginfo("[controller] Publishing STL (%s) + Excel (%s)", self.stl_path, self.excel_path)
                self.talker.publish_file_message(self.stl_path, self.excel_path)
                if self.latched_file_pub:
                    latched_msg = FileExtractionMessage()
                    with open(self.stl_path, "rb") as f:
                        latched_msg.stl_data = f.read()
                    latched_msg.excelfile = str(self.excel_path)
                    self.latched_file_pub.publish(latched_msg)
                rospy.sleep(self.delay_between_publishes)
                return
            except Exception as e:
                rospy.logerr("[controller] STL publish failed: %s", e)
        msg = FileExtractionMessage()
        msg.stl_data = b""
        msg.excelfile = str(self.excel_path)
        rospy.loginfo("[controller] Publishing Excel path via FileExtractionMessage: %s", msg.excelfile)
        self.talker.file_pub.publish(msg)
        if self.latched_file_pub:
            self.latched_file_pub.publish(msg)
        rospy.sleep(self.delay_between_publishes)

    def _publish_selection(self, wall):
        self.talker.publish_selection_message(
            wallselection=wall, picked_position=[], typeselection=self.typeselection
        )
        rospy.loginfo("[controller] Published selection for wall=%r", wall)
        rospy.sleep(self.delay_between_publishes)

    # ---------- main ----------
    def run(self):
        # Wait for initialization
        if not self._init_event.is_set():
            rospy.loginfo("[controller] Waiting for init on %s or params (~excel_path + (expected_walls|model_sides)) ...", CTRL_INIT)
            while not rospy.is_shutdown() and not self._init_event.wait(timeout=0.2):
                pass
        if rospy.is_shutdown():
            return
        self.publish_file_message()
        if not self.expected_walls:
            rospy.loginfo("[controller] No expected_walls; nothing to do.")
            return
        # Process each wall
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
