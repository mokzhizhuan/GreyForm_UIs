import rospy

import sys
from my_robot_wallinterfaces.msg import (
    FileExtractionMessage,
    SelectionWall,
)
from my_robot_wallinterfaces.srv import SetLed
import PythonApplication.exceldatavtk as exceldata
from std_msgs.msg import String
import pandas as pd
import numpy as np


class TalkerNode:
    def __init__(self):
        self.file_publisher_ = rospy.Publisher(
            "file_extraction_topic", FileExtractionMessage, queue_size=10
        )
        self.selection_publisher_ = rospy.Publisher(
            "selection_wall_topic", SelectionWall, queue_size=10
        )
        self.rate = rospy.Rate(10)  # 10 Hz

    def publish_file_message(
        self, file_path, excel_filepath, picked_position, point_id, reader
    ):
        try:
            with open(file_path, "rb") as f:
                stl_data = f.read()
            msg = FileExtractionMessage()
            msg.stl_data = list(stl_data)  # Convert bytes to a list of uint8
            msg.excelfile = excel_filepath
            self.threshold_distance = 50
            all_exceldatas = exceldata.excel_extractor(excel_filepath, reader)
            for sheet_name, data in all_exceldatas.items():
                if isinstance(data, dict):
                    df = pd.DataFrame(data)
                    df["Position X (m)"] = pd.to_numeric(
                        df["Position X (m)"], errors="coerce"
                    )
                    df["Position Y (m)"] = pd.to_numeric(
                        df["Position Y (m)"], errors="coerce"
                    )
                    df["Position Z (m)"] = pd.to_numeric(
                        df["Position Z (m)"], errors="coerce"
                    )
                    required_columns = {
                        "Position X (m)",
                        "Position Y (m)",
                        "Position Z (m)",
                        "wall_numbers",
                    }
                    if required_columns.issubset(df.columns):
                        for index, row in df.iterrows():
                            wall_position = np.array(
                                [
                                    row["Position X (m)"],
                                    row["Position Y (m)"],
                                    row["Position Z (m)"],
                                ]
                            )
                            distance = self.calculate_distance(
                                picked_position, wall_position
                            )
                        if distance <= self.threshold_distance:
                            rospy.loginfo(
                                f"Picked position is near Wall Number {row['wall_numbers']} at a distance of {distance:.2f} units on sheet {sheet_name}."
                            )
                    else:
                        rospy.loginfo(
                            f"Sheet {sheet_name} does not contain position data."
                        )
                else:
                    rospy.loginfo(f"Item {sheet_name} is not a DataFrame.")
            self.file_publisher_.publish(msg)
            rospy.loginfo("STL file published: %s" % stl_data[:100])
            rospy.loginfo("Excel file path: %s" % excel_filepath)
        except FileNotFoundError as e:
            rospy.logerr(f"File not found: {e}")
        except Exception as e:
            rospy.logerr(f"Failed to read and publish STL file: {e}")

    def calculate_distance(self, point1, point2):
        return np.linalg.norm(point1 - point2)

    def publish_selection_message(self):
        try:
            msg = SelectionWall()
            wallselections = msg.wallselections
            typeselection = msg.typeselection
            sectionselection = msg.sectionselection
            self.selection_publisher_.publish(msg)
            rospy.loginfo(
                "Selection message published: wallselections=%d, typeselection=%s, sectionselection=%d"
                % (wallselections, typeselection, sectionselection)
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
