#!/usr/bin/env python3
import rospy
from std_msgs.msg import String, Bool
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall


class TalkerNode:
    """
    Lightweight ROS talker for the wall-marking system.

    Responsibilities:
    - Publish the Excel file selection to /file_extraction_topic
    - Publish wall selection + positions to /selection_wall_topic
    - Publish UI events to:
      - /ui/wall_started
      - /ui/wall_done
      - /ui/all_done
    """

    def __init__(self):
        # Avoid re-init if another node has already initialised rospy
        if not rospy.core.is_initialized():
            rospy.init_node("talker_node", anonymous=True, disable_signals=True)

        # Publishers
        self.file_pub = rospy.Publisher(
            "/file_extraction_topic", FileExtractionMessage, queue_size=10
        )
        self.sel_pub = rospy.Publisher(
            "/selection_wall_topic", SelectionWall, queue_size=10
        )

        # UI topics (latching so the latest state is held for new subscribers)
        self.ui_wall_started_pub = rospy.Publisher(
            "/ui/wall_started", String, queue_size=10, latch=True
        )
        self.ui_wall_done_pub = rospy.Publisher(
            "/ui/wall_done", String, queue_size=10, latch=True
        )
        self.ui_all_done_pub = rospy.Publisher(
            "/ui/all_done", Bool, queue_size=10, latch=True
        )

        rospy.loginfo("[talker] TalkerNode initialised.")

    # ------------------------------------------------------------------
    # Internal helper: wait for subscribers
    # ------------------------------------------------------------------
    def _wait_for_subscribers(self, pubs, timeout: float = 1.0) -> None:
        """
        Block until all publishers in `pubs` have at least one subscriber
        or the timeout (in seconds) elapses.
        """
        start = rospy.Time.now().to_sec()
        while not rospy.is_shutdown():
            if all(p.get_num_connections() > 0 for p in pubs):
                return
            if (rospy.Time.now().to_sec() - start) > timeout:
                break
            rospy.sleep(0.05)

    # ------------------------------------------------------------------
    # File selection message
    # ------------------------------------------------------------------
    def publish_file_message(self, directory: str, excel_path: str) -> None:
        """
        Tell the listener which Excel file to use.

        directory: base folder (matched by listener)
        excel_path: either absolute path or filename; listener will resolve.
        """
        msg = FileExtractionMessage()
        msg.directory = directory or ""
        msg.excelfile = excel_path or ""

        rospy.loginfo(
            f"[talker] Publishing FileExtractionMessage: "
            f"directory={msg.directory!r}, excelfile={msg.excelfile!r}"
        )

        # Ensure listener_node is listening before we fire the first message
        try:
            self._wait_for_subscribers([self.file_pub], timeout=2.0)
        except Exception:
            # Do not crash caller on wait error
            pass

        self.file_pub.publish(msg)

    # ------------------------------------------------------------------
    # Wall selection message
    # ------------------------------------------------------------------
    def publish_selection_message(
        self,
        wallselection,
        picked_position,
        typeselection,
    ) -> None:
        """
        Publish a SelectionWall message with:
        - wallselection  (e.g. 1..6 or 'F')
        - typeselection  (Stage 2, Stage 3, etc.)
        - picked_position [x, y, z] ints for the marking position
        """

        lab = str(wallselection)

        # UI feedback: wall started
        try:
            self.ui_wall_started_pub.publish(String(data=lab))
        except Exception:
            pass

        # Ensure the subscriber is present before first selection
        self._wait_for_subscribers([self.sel_pub], timeout=0.5)

        msg = SelectionWall()
        msg.wallselection = lab
        msg.typeselection = str(typeselection or "")

        # sectionselection: fixed 0 for now (kept for compatibility)
        try:
            msg.sectionselection = 0
        except Exception:
            pass

        # picked_position: best-effort conversion to int list
        try:
            msg.picked_position = [int(v) for v in picked_position]
        except Exception:
            msg.picked_position = []

        # default_position: currently unused, send empty
        try:
            msg.default_position = []
        except Exception:
            pass

        rospy.loginfo(
            f"[talker] Publishing SelectionWall: "
            f"wall={msg.wallselection}, type={msg.typeselection}, "
            f"picked_position={msg.picked_position}"
        )
        self.sel_pub.publish(msg)

    # ------------------------------------------------------------------
    # UI helpers (optional but useful for external callers)
    # ------------------------------------------------------------------
    def publish_wall_done(self, wallselection) -> None:
        """
        Manually publish /ui/wall_done if an external component decides
        that a wall has finished (usually listener_node does this).
        """
        lab = str(wallselection)
        try:
            self.ui_wall_done_pub.publish(String(data=lab))
            rospy.loginfo(f"[talker] UI wall_done published for wall={lab}")
        except Exception:
            pass

    def publish_all_done(self, is_done: bool) -> None:
        """
        Manually publish /ui/all_done (e.g. when all robot flows complete).
        """
        try:
            self.ui_all_done_pub.publish(Bool(data=bool(is_done)))
            rospy.loginfo(f"[talker] UI all_done published: {bool(is_done)}")
        except Exception:
            pass


