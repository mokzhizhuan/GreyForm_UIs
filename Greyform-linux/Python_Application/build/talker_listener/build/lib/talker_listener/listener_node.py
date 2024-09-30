import rclpy
from rclpy.node import Node
from my_robot_wallinterfaces.msg import (
    SelectionWall,
    FileExtractionMessage,
)
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from my_robot_wallinterfaces.srv import SetLed
from std_msgs.msg import String
from stl import mesh
import pandas as pd
import numpy as np
import sys
import tkinter as tk

sys.path.append("/home/ubuntu/ros2_ws/src/Greyform-linux/Python_Application")
import PythonApplication.dialoglogger as logs


class SingletonDialog:
    _instance = None

    @classmethod
    def show_info_dialog(cls, message, title):
        if cls._instance is None:
            cls._instance = logs.LogDialog(message, title, log_type="info")
            cls._instance.exec_()

    @classmethod
    def clear(cls):
        if cls._instance:
            cls._instance.destroy()
            cls._instance = None


class ListenerNode(Node):
    def __init__(self):
        super().__init__("listener_node")
        self.file_subscription_ = self.create_subscription(
            FileExtractionMessage,  # Correct message type
            "file_extraction_topic",  # Correct topic
            self.file_listener_callback,
            10,
        )
        self.selection_subscription_ = self.create_subscription(
            SelectionWall,  # Correct message type
            "selection_wall_topic",  # Correct topic
            self.selection_listener_callback,
            10,
        )
        self.file_callback = None
        self.selection_callback = None
        self.wallselection = None
        self.typeselection = None
        self.sectionselection = None
        self.picked_position = []
        self.message = ""
        self.spacing = "\n"
        self.title = "Listener Node"
        self.active_dialog = None


    def file_listener_callback(self, msg):
        try:
            stl_data = bytes(msg.stl_data)
            self.message += (
                f"{self.spacing}STL file received and processed: {msg.stl_data[:10]}"
            )
            with open("/tmp/temp_stl_file.stl", "wb") as f:
                f.write(stl_data)
            stl_mesh = mesh.Mesh.from_file("/tmp/temp_stl_file.stl")
            self.message += f"{self.spacing}Excel file path: {msg.excelfile}"
            # Process the Excel file
            self.process_excel_data(msg.excelfile)
            if self.file_callback:
                self.file_callback(stl_mesh)
        except Exception as e:
            message = f"Failed to process received STL file: {e}"
            print(message)

    def selection_listener_callback(self, msg):
        try:
            self.message += (
                f"{self.spacing}Selection message received:{self.spacing} wallselections={msg.wallselection}, "
                f"{self.spacing}typeselection={msg.typeselection},{self.spacing} sectionselection={msg.sectionselection}"
            )
            self.wallselection = msg.wallselection
            self.typeselection = msg.typeselection
            self.sectionselection = msg.sectionselection
            self.picked_position = msg.picked_position
            if self.selection_callback:
                self.selection_callback(msg)
        except Exception as e:
            message = f"Failed to publish selection message: {e}"
            print(message)

    def process_excel_data(self, excel_filepath):
        try:
            self.excelitems = pd.read_excel(excel_filepath, sheet_name=None)
            threshold_distance = 600
            processed_data = {}
            for sheet_name, data in self.excelitems.items():
                df = pd.DataFrame(data)
                for index, row in df.iterrows():
                    self.storedzpos = df.at[index, "Position Z (m)"]
                    if df.at[index, "Position Z (m)"] < 0:
                        df.at[index, "Position Z (m)"] = 0
                    wall_position = np.array(
                        [
                            row["Position X (m)"],
                            row["Position Y (m)"],
                            row["Position Z (m)"],
                        ]
                    )
                    distance = self.calculate_distance(
                        self.picked_position, wall_position
                    )
                    if distance <= threshold_distance:
                        self.message += f"{self.spacing}Picked position is near Wall Number {row['Wall Number']} on sheet {sheet_name}."
                        df.at[index, "Status"] = "done"
                    df.at[index, "Position Z (m)"] = self.storedzpos
                processed_data[sheet_name] = df
            with pd.ExcelWriter(excel_filepath, engine="openpyxl") as writer:
                for sheet_name, df in processed_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                self.message += f"{self.spacing}Excel data processed successfully."
            self.show_info_dialog(self.message)
        except FileNotFoundError as e:
            message = f"Excel file not found: {e}"
            print(message)
        except Exception as e:
            message = f"Failed to process Excel file: {e}"
            print(message)

    def set_file_callback(self, callback):
        self.file_callback = callback

    def set_selection_callback(self, callback):
        self.selection_callback = callback

    def calculate_distance(self, point1, point2):
        return np.linalg.norm(point1 - point2)

    def show_info_dialog(self, message):
        if self.active_dialog:
            self.active_dialog.close()
            self.active_dialog = None
        self.active_dialog = logs.LogDialog(message, self.title, log_type="info")
        self.active_dialog.exec_()


def main(args=None):
    rclpy.init(args=args)
    app = QApplication(sys.argv)
    listenerNode = ListenerNode()
    rclpy.spin(listenerNode)
    listenerNode.destroy_node()
    sys.exit(app.exec_())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
