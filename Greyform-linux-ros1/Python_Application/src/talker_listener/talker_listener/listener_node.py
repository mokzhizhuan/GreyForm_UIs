#!/usr/bin/env python3
import rospy
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall
from stl import mesh
import pandas as pd
import numpy as np

class ListenerNode:
    """ A single instance of ListenerNode that runs without any GUI """

    def __init__(self):
        rospy.init_node("listener_node", anonymous=True)  # ✅ Initialize ROS in the main thread

        self.file_subscription_ = rospy.Subscriber(
            "file_extraction_topic",
            FileExtractionMessage,
            self.file_listener_callback,
            queue_size=10,
        )
        self.selection_subscription_ = rospy.Subscriber(
            "selection_wall_topic",
            SelectionWall,
            self.selection_listener_callback,
            queue_size=10,
        )

        self.log_buffer = []  # Store logs until Excel processing

    def file_listener_callback(self, msg):
        """ Process STL and Excel file messages but DO NOT show logs yet """
        try:
            self.log_buffer.append(f"📥 STL file received: {msg.stl_data[:10]}")
            self.log_buffer.append(f"📁 Excel file path: {msg.excelfile}")

            # Process the Excel file
            self.process_excel_data(msg.excelfile)
        except Exception as e:
            self.log_buffer.append(f"❌ Error processing STL file: {e}")

        # Print logs to console (no GUI)
        for log in self.log_buffer:
            rospy.loginfo(log)

    def selection_listener_callback(self, msg):
        """ Process selection messages but DO NOT show logs yet """
        self.wallselection = msg.wallselection
        self.typeselection = msg.typeselection
        self.picked_position = msg.picked_position

    def process_excel_data(self, excel_filepath):
        """ Process Excel data and update logs """
        self.excelitems = pd.read_excel(excel_filepath, sheet_name=None)
        processed_data = {}
        for stage, data in self.excelitems.items():
            df = pd.DataFrame(data)
            for index, row in df.iterrows():
                df.at[index, "Position X (mm)"] = df.at[index, "Position X (mm)"]
                df.at[index, "Position Y (mm)"] = df.at[index, "Position Y (mm)"]
                df.at[index, "Position Z (mm)"] = df.at[index, "Position Z (mm)"]

                wallnumberreq = str(df.at[index, "Wall Number"])
                if self.wallselection == wallnumberreq and self.typeselection == stage:
                    self.log_buffer.append(f"Marking positions in {self.picked_position} on sheet {stage}")
                    df.at[index, "Status"] = "done"

            processed_data[stage] = df

        with pd.ExcelWriter(excel_filepath, engine="openpyxl") as writer:
            for sheet_name, df in processed_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        self.log_buffer.append("✅ Excel data processed successfully.")

        # Print logs to console (no GUI)
        for log in self.log_buffer:
            rospy.loginfo(log)

def main():
    """ Main function to run ROS without GUI """
    listener = ListenerNode()
    rospy.spin()  # ✅ Run ROS event loop normally

if __name__ == "__main__":
    main()
