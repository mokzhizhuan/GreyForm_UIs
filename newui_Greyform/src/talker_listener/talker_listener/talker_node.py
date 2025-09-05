#!/usr/bin/env python3
import rospy
from pathlib import Path
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall

class TalkerNode:
    def __init__(self):
        self.file_pub = rospy.Publisher(
            "file_extraction_topic", FileExtractionMessage, queue_size=10
        )
        self.sel_pub = rospy.Publisher(
            "selection_wall_topic", SelectionWall, queue_size=10
        )
        self.rate = rospy.Rate(10)

    def publish_file_message(self, stl_path, excel_path):
        msg = FileExtractionMessage()
        try:
            stl_path = Path(stl_path).expanduser().resolve()
            with stl_path.open("rb") as f:
                msg.stl_data = list(f.read())
        except Exception as e:
            rospy.logwarn(f"[talker] Could not read STL ({type(e).__name__}: {e}); sending empty stl_data.")
            msg.stl_data = []
        excel_path = Path(excel_path).expanduser().resolve()
        if not excel_path.exists():
            rospy.logwarn(f"[talker] Excel path does not exist: {excel_path}")
        msg.excelfile = str(excel_path)
        self.file_pub.publish(msg)
        rospy.loginfo(f"[talker] Published file message with Excel={msg.excelfile}")

    def publish_selection_message(self, wall_number, picked_position, markingtype):
        msg = SelectionWall()
        msg.wallselection = str(wall_number)  # can be "F" or "1".."6"
        msg.typeselection = str(markingtype)  # will be parsed numeric on listener side
        # round to nearest mm and cast to int for int32[]
        nums = [int(round(float(v))) for v in list(picked_position)[:3]]
        msg.picked_position = nums
        self.sel_pub.publish(msg)


def main():
    rospy.init_node("talker_node", anonymous=True)
    node = TalkerNode()
    rospy.loginfo("[talker] Node started. Use your UI to call publish_* methods.")
    rospy.spin()

if __name__ == "__main__":
    main()
