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
import numpy as np
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import tkinter as tk
from tkinter import Text, Scrollbar, Toplevel, Button, END, BOTH, RIGHT, Y, LEFT, X

sys.path.append("/root/catkin_ws/src/Greyform-linux/Python_Application")
import PythonApplication.dialoglogger as logs


class ScrollableDialog(Toplevel):
    def __init__(self, root, title, message):
        super().__init__(root)
        self.title(title)
        self.geometry("400x300") 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        text_widget = Text(self, wrap='word')
        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar = Scrollbar(self, command=text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.insert(END, message)
        text_widget.config(state=tk.DISABLED)  
        ok_button = Button(self, text="OK", command=self.destroy)
        ok_button.grid(row=1, column=0, columnspan=2, pady=5)


class ListenerNode(QMainWindow):
    def __init__(self, root):
        self.root = root
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
        self.wallselection = None
        self.typeselection = None
        self.sectionselection = None
        self.picked_position = []
        self.message = ""
        self.spacing = "\n"
        self.title = "Listener Node"
        self.label = tk.Label(root, text="ROS Node Initialized")
        self.label.pack()
        self.button = tk.Button(
            root, text="Show Message", command=self.show_info_dialog
        )
        self.button.pack()

    def file_listener_callback(self, msg):
        try:
            stl_data = bytes(msg.stl_data)  # Convert list of uint8 back to bytes
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
            self.show_error_dialog(message)

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
            self.show_error_dialog(message)

    def process_excel_data(self, excel_filepath):
        try:
            self.excelitems = pd.read_excel(excel_filepath, sheet_name=None)
            threshold_distance = 600
            processed_data = {}
            for sheet_name, data in self.excelitems.items():
                df = pd.DataFrame(data)
                for index, row in df.iterrows():
                    row["Position Z (m)"] = 0
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
                processed_data[sheet_name] = df
            with pd.ExcelWriter(excel_filepath, engine="openpyxl") as writer:
                for sheet_name, df in processed_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                self.message += f"{self.spacing}Excel data processed successfully."
            self.show_info_dialog(self.message)
        except FileNotFoundError as e:
            message = f"Excel file not found: {e}"
            self.show_error_dialog(message)
        except Exception as e:
            message = f"Failed to process Excel file: {e}"
            self.show_error_dialog(message)

    def set_file_callback(self, callback):
        self.file_callback = callback

    def set_selection_callback(self, callback):
        self.selection_callback = callback

    def calculate_distance(self, point1, point2):
        return np.linalg.norm(point1 - point2)

    def show_info_dialog(self, message):
        ScrollableDialog(self.root, self.title, message)

    def show_error_dialog(self, message):
        ScrollableDialog(self.root, self.title, message)


def main(args=None):
    root = tk.Tk()
    rospy.init_node("listener_node", anonymous=True)
    app = QApplication(sys.argv)
    listenerNode = ListenerNode(root)
    root.withdraw()
    root.mainloop()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass
    finally:
        rospy.signal_shutdown("Shutting down ROS node")


if __name__ == "__main__":
    main()
