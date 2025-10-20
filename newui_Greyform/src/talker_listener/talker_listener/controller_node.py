#!/usr/bin/env python3
"""
Controller node that orchestrates wall processing and publishes the Excel + STL file.

This version reuses TalkerNode for most publishes and will send a real STL file
if you provide a '~stl_path' ROS parameter (or pass via rosparam/launch).
"""
import os
import rospy
import threading
from std_msgs.msg import String, Bool
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall

from talker_node import TalkerNode  # reuse existing publisher helpers

FILE_TOPIC = "/file_extraction_topic"
SEL_TOPIC  = "/selection_wall_topic"
UI_STARTED = "/ui/wall_started"
UI_DONE    = "/ui/wall_done"
UI_ALLDONE = "/ui/all_done"


class ControllerNode:
    def __init__(self):
        rospy.init_node("controller_node", anonymous=True)

        # instantiate TalkerNode and reuse its publishers / helper methods
        # TalkerNode checks rospy.core.is_initialized() before init, so no conflict
        self.talker = TalkerNode()

        # configuration: list of walls to process (strings), e.g. ["1","2","3","F"]
        self.expected_walls = rospy.get_param("~expected_walls", [])
        # typeselection used when publishing SelectionWall (optional)
        self.typeselection = rospy.get_param("~typeselection", "")
        # Excel path to publish in FileExtractionMessage (optional)
        self.excel_path = rospy.get_param("~excel_path", None)
        # Path to the real STL file to embed in the FileExtractionMessage (optional)
        self.stl_path = rospy.get_param("~stl_path", None)

        self.latch_file_publish = rospy.get_param("~latch_file_publish", False)
        if self.latch_file_publish:
            # Create a latched publisher specifically for the file message.
            # This avoids changing TalkerNode implementation and preserves other talker behavior.
            self.latched_file_pub = rospy.Publisher(FILE_TOPIC, FileExtractionMessage, queue_size=1, latch=True)
        else:
            self.latched_file_pub = None

        # timing and retries
        self.per_wall_timeout = rospy.get_param("~per_wall_timeout", 8.0)  # seconds to wait for done
        self.per_wall_retries = rospy.get_param("~per_wall_retries", 2)    # retries per wall
        self.delay_between_publishes = rospy.get_param("~delay_between_publishes", 0.2)

        # subscribe to UI_DONE to observe listener confirmations
        rospy.Subscriber(UI_DONE, String, self._ui_done_cb, queue_size=10)

        # event used to wait for each wall completion
        self._done_event = threading.Event()
        self._last_done_wall = None
        self._lock = threading.Lock()

        rospy.loginfo("[controller] Init complete; expected_walls=%r", self.expected_walls)

    def publish_file_message(self):
        """
        Publish a FileExtractionMessage that contains the excel_path and, if configured,
        the actual STL file bytes (from ~stl_path). Behavior:
         - if ~stl_path is provided and valid, read the file and call TalkerNode.publish_file_message
           to publish the payload (which will publish via talker.file_pub).
         - if latch_file_publish is True, also publish the same message on a latched publisher
           so late subscribers get the message immediately.
         - if no stl_path is provided, send an orchestration-only message with empty stl_data.
        """
        if not self.excel_path:
            rospy.logwarn("[controller] No excel_path configured; skipping file publish")
            return

        # If a real stl file is provided, let TalkerNode read it and publish.
        if self.stl_path:
            if not os.path.isfile(self.stl_path):
                rospy.logerr("[controller] Provided stl_path does not exist: %r", self.stl_path)
                # fallback: publish excel path w/o stl payload so listener still gets the path
            else:
                try:
                    # Use TalkerNode helper which reads the STL file and publishes it.
                    # Note: TalkerNode.publish_file_message reads the file itself.
                    rospy.loginfo("[controller] Publishing STL (%s) and excel path (%s) via TalkerNode",
                                  self.stl_path, self.excel_path)
                    self.talker.publish_file_message(self.stl_path, self.excel_path)
                    # If the user requested a latched copy, also publish the same message on the latched pub.
                    if self.latch_file_publish and self.latched_file_pub:
                        # Build the message and publish latched copy
                        latched_msg = FileExtractionMessage()
                        with open(self.stl_path, "rb") as f:
                            latched_msg.stl_data = f.read()
                        latched_msg.excelfile = str(self.excel_path)
                        self.latched_file_pub.publish(latched_msg)
                    # small pause to allow subscribers to connect/process
                    rospy.sleep(self.delay_between_publishes)
                    return
                except Exception as e:
                    rospy.logerr("[controller] Failed to publish STL file: %s", e)
                    # fallthrough to publish empty-orchestration message

        # Default/orchestration-only publish: empty payload but advertise excel_path
        msg = FileExtractionMessage()
        msg.stl_data = b""
        msg.excelfile = str(self.excel_path)
        rospy.loginfo("[controller] Publishing excel path via FileExtractionMessage: %r", msg.excelfile)
        # reuse TalkerNode publisher (non-latched by default)
        self.talker.file_pub.publish(msg)
        # optionally also publish latched copy if requested
        if self.latch_file_publish and self.latched_file_pub:
            self.latched_file_pub.publish(msg)
        rospy.sleep(self.delay_between_publishes)

    def _ui_done_cb(self, msg):
        # called when listener reports a wall done: String.data contains the wall token
        wall = str(msg.data).strip()
        rospy.loginfo_throttle(5, "[controller] Received UI done for %r", wall)
        with self._lock:
            self._last_done_wall = wall
            self._done_event.set()

    def _publish_selection(self, wall):
        """
        Use the TalkerNode.publish_selection_message helper to send a selection request.
        That helper also publishes a /ui/wall_started message before sending the selection.
        """
        # reuse TalkerNode helper which builds the SelectionWall message and publishes it
        self.talker.publish_selection_message(wallselection=wall, picked_position=[], typeselection=self.typeselection)
        rospy.loginfo("[controller] Published selection for wall=%r via TalkerNode", wall)
        rospy.sleep(self.delay_between_publishes)

    def run(self):
        # publish the excel path (and optional STL) first so Listener has it
        self.publish_file_message()

        if not self.expected_walls:
            rospy.loginfo("[controller] No expected_walls configured; nothing to do.")
            return

        for wall in self.expected_walls:
            if rospy.is_shutdown():
                return
            success = False
            for attempt in range(1, self.per_wall_retries + 2):  # first attempt + retries
                rospy.loginfo("[controller] Processing wall %r (attempt %d)", wall, attempt)
                # clear event and publish selection
                self._done_event.clear()
                with self._lock:
                    self._last_done_wall = None
                self._publish_selection(wall)

                # wait for done for this specific wall
                waited = self._done_event.wait(timeout=self.per_wall_timeout)
                if waited:
                    with self._lock:
                        last = self._last_done_wall
                    if last == str(wall):
                        rospy.loginfo("[controller] Wall %r confirmed done", wall)
                        success = True
                        break
                    else:
                        rospy.logwarn("[controller] Received done for %r while waiting for %r; continuing wait/retry",
                                      last, wall)
                else:
                    rospy.logwarn("[controller] Timeout waiting for wall %r (attempt %d)", wall, attempt)
                # small backoff before retrying
                rospy.sleep(0.5)

            if not success:
                rospy.logerr("[controller] Failed to complete wall %r after retries; continuing to next", wall)

        # All walls attempted; publish all_done via TalkerNode to reuse the latched UI publisher
        rospy.loginfo("[controller] All walls attempted; publishing /ui/all_done")
        self.talker.publish_all_done(is_done=True)
        rospy.loginfo("[controller] Controller finished.")


def main():
    node = ControllerNode()
    node.run()
    # optionally keep node alive to respond to late events
    rospy.spin()


if __name__ == "__main__":
    main()