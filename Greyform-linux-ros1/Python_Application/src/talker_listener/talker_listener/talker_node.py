import rospy

import sys
from my_robot_wallinterfaces.msg import (
    FileExtractionMessage,
    SelectionWall,
)
from my_robot_wallinterfaces.srv import SetLed
from std_msgs.msg import String


class TalkerNode:
    def __init__(self):
        self.file_publisher_ = rospy.Publisher(
            "file_extraction_topic", FileExtractionMessage, queue_size=10
        )
        self.selection_publisher_ = rospy.Publisher(
            "selection_wall_topic", SelectionWall, queue_size=10
        )
        self.rate = rospy.Rate(10)  # 10 Hz

    def publish_file_message(self, file_path, excel_filepath):
        try:
            with open(file_path, "rb") as f:
                stl_data = f.read()
            msg = FileExtractionMessage()
            msg.stl_data = list(stl_data)  # Convert bytes to a list of uint8
            msg.excelfile = excel_filepath
            self.file_publisher_.publish(msg)
            rospy.loginfo("STL file published: %s" % stl_data[:100])
            rospy.loginfo("Excel file path: %s" % excel_filepath)
        except FileNotFoundError as e:
            rospy.logerr(f"File not found: {e}")
        except Exception as e:
            rospy.logerr(f"Failed to read and publish STL file: {e}")

    def publish_selection_message(self):
        try:
            msg = SelectionWall()
            msg.wallselections = 1
            msg.typeselection = "typeselection"
            msg.sectionselection = 2
            self.selection_publisher_.publish(msg)
            rospy.loginfo(
                "Selection message published: wallselections=%d, typeselection=%s, sectionselection=%d"
                % (msg.wallselections, msg.typeselection, msg.sectionselection)
            )
        except Exception as e:
            rospy.logerr(f"Failed to publish selection message: {e}")

    def timer_callback(self, event):
        msg = String()
        msg.data = f"Hello everyone {self.count}"
        self.publisher_.publish(msg)
        self.count += 1
        rospy.loginfo(f"Publishing {msg.data}")


def main(args=None):
    rospy.init(args=args)
    rospy.init_node("node_name", anonymous=True)
    talkerNode = TalkerNode()
    rospy.spin(talkerNode)
    talkerNode.destroy_node()
    rospy.shutdown()


if __name__ == "__main__":
    main()
