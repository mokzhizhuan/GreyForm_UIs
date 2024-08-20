#!/usr/bin/env python3
import rospy
from my_robot_wallinterfaces.msg import (
    SelectionWall,
    FileExtractionMessage,
)
from my_robot_wallinterfaces.srv import SetLed
from std_msgs.msg import String
from stl import mesh
import pandas as pd


class ListenerNode():
    def __init__(self):
        super().__init__()
        self.file_subscription_ = rospy.Subscriber(
            "file_extraction_topic",  # Correct topic
            FileExtractionMessage,  # Correct message type
            self.file_listener_callback,
            queue_size=10,
        )
        self.selection_subscription_ = rospy.Subscriber(
            "selection_wall_topic",  # Correct topic
            SelectionWall,  # Correct message type
            self.selection_listener_callback,
            queue_size=10,
        )
        self.file_callback = None
        self.selection_callback = None

    def file_listener_callback(self, msg):
        try:
            stl_data = bytes(msg.stl_data)  # Convert list of uint8 back to bytes
            rospy.loginfo("STL file received and processed: %s" % msg.stl_data[:100])
            with open('/tmp/temp_stl_file.stl', 'wb') as f:
                f.write(stl_data)
            stl_mesh = mesh.Mesh.from_file('/tmp/temp_stl_file.stl')
            rospy.loginfo("Excel file path: %s" % msg.excelfile)
            # Process the Excel file
            self.process_excel_data(msg.excelfile)
            if self.file_callback:
                self.file_callback(stl_mesh)
        except Exception as e:
            rospy.logerr(f"Failed to process received STL file: {e}")

    def selection_listener_callback(self, msg):
        try:
            rospy.loginfo(
                "Selection message received: wallselections=%d, typeselection=%s, sectionselection=%d"
                % (msg.wallselections, msg.typeselection, msg.sectionselection)
            )
            if self.selection_callback:
                self.selection_callback(msg)
        except Exception as e:
            rospy.logerr(f"Failed to process received selection message: {e}")

    def process_excel_data(self, excel_filepath):
        try:
            df = pd.read_excel(excel_filepath)
            rospy.loginfo("Excel data processed successfully.")
            # You can add further processing logic here
        except FileNotFoundError as e:
            rospy.logerr(f"Excel file not found: {e}")
        except Exception as e:
            rospy.logerr(f"Failed to process Excel file: {e}")

    def set_file_callback(self, callback):
        self.file_callback = callback

    def set_selection_callback(self, callback):
        self.selection_callback = callback

def main(args=None):
    rospy.init_node('listener_node', anonymous=True)
    listenerNode = ListenerNode()
    rospy.spin()


if __name__ == "__main__":
    main()
