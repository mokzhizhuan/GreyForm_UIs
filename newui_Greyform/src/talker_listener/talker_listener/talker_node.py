# talker_node.py
import rospy
from std_msgs.msg import String, Int32, Bool
from my_robot_wallinterfaces.msg import (
    FileExtractionMessage,
    SelectionWall,
)


class TalkerNode:
    def __init__(self):
        if not rospy.core.is_initialized():
            rospy.init_node("talker_node", anonymous=True, disable_signals=True)
        self.file_pub = rospy.Publisher(
            "/file_extraction_topic", FileExtractionMessage, queue_size=10
        )
        self.sel_pub = rospy.Publisher(
            "/selection_wall_topic", SelectionWall, queue_size=10
        )
        self.ui_wall_started_pub = rospy.Publisher(
            "/ui/wall_started", String, queue_size=10, latch=True
        )
        self.ui_wall_done_pub = rospy.Publisher(
            "/ui/wall_done", String, queue_size=10, latch=True
        )
        self.ui_all_done_pub = rospy.Publisher(
            "/ui/all_done", Bool, queue_size=10, latch=True
        )

    def _wait_for_subscribers(self, pubs, timeout=1.0):
        start = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start) < timeout:
            if all(p.get_num_connections() > 0 for p in pubs):
                return
            rospy.sleep(0.05)

    def publish_file_message(self, directory: str, excel_path: str):
        msg = FileExtractionMessage()
        msg.directory = directory
        msg.excelfile = excel_path
        self.file_pub.publish(msg)

    def publish_selection_message(self, wallselection, picked_position, typeselection):
        lab = str(wallselection)
        try:
            self.ui_wall_started_pub.publish(String(data=lab))
        except Exception:
            pass
        self._wait_for_subscribers([self.sel_pub], timeout=0.5)
        msg = SelectionWall()
        msg.wallselection = lab
        msg.typeselection = str(typeselection)
        try:
            msg.sectionselection = 0
        except:
            pass
        try:
            msg.picked_position = [int(v) for v in picked_position]
        except:
            msg.picked_position = []
        try:
            msg.default_position = []
        except:
            pass
        self.sel_pub.publish(msg)

    def publish_wall_done(self, wallselection):
        lab = str(wallselection)
        try:
            self.ui_wall_done_pub.publish(String(data=lab))
        except Exception:
            pass

    def publish_all_done(self, is_done: bool):
        try:
            self.ui_all_done_pub.publish(Bool(data=bool(is_done)))
        except Exception:
            pass
