# talker_node.py (only showing the essentials)
import rospy
from std_msgs.msg import String, Int32, Bool
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall

class TalkerNode:
    def __init__(self):
        if not rospy.core.is_initialized():
            rospy.init_node("talker_node", anonymous=True, disable_signals=True)

        self.file_pub = rospy.Publisher(
            "file_extraction_topic",
            FileExtractionMessage,
            queue_size=10, )
        self.sel_pub  = rospy.Publisher("selection_wall_topic",   SelectionWall,       queue_size=10)

        # optional UI topics (keep if you use them elsewhere)
        self.ui_wall_started_pub = rospy.Publisher("/ui/wall_started", String, queue_size=10, latch=True)

        self.ui_all_done_pub = rospy.Publisher("/ui/all_done", Bool, queue_size=10, latch=True)

    def _wait_for_subscribers(self, pubs, timeout=1.0):
        start = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start) < timeout:
            if all(p.get_num_connections() > 0 for p in pubs):
                return
            rospy.sleep(0.05)

    # --- NO LABEL UPDATES HERE ---
    def publish_file_message(self, stl_file_path: str, excel_path: str):
        # read STL as bytes
        with open(stl_file_path, "rb") as f:
            ifc_bytes = f.read()

        msg = FileExtractionMessage()
        # uint8[] can be bytes/bytearray/list[int]
        msg.stl_data  = ifc_bytes # or just: msg.stl_data = data
        msg.excelfile = excel_path        # this matches your .msg

        self.file_pub.publish(msg)
        rospy.loginfo(f"[talker] Sent FileExtraction: bytes={len(ifc_bytes)} excel={excel_path}")


    # keep label/ROS UI updates here if desired
    def publish_selection_message(self, wallselection, picked_position, typeselection):
        try:
            self.ui_wall_started_pub.publish(Int32(int(wallselection)))
        except Exception:
            pass


        self._wait_for_subscribers([self.sel_pub], timeout=0.5)
        msg = SelectionWall()
        msg.wallselection = str(wallselection)
        # when a wall starts:
        self.ui_wall_started_pub.publish(String(data=str(wallselection)))
        msg.typeselection = str(typeselection)
        try:    msg.sectionselection = 0
        except: pass
        try:    msg.picked_position = [int(v) for v in picked_position]
        except: msg.picked_position = []
        try:    msg.default_position = []
        except: pass
        self.sel_pub.publish(msg)


def main():
    rospy.init_node("talker_node", anonymous=True)
    node = TalkerNode()
    rospy.spin()

if __name__ == "__main__":
    main()
