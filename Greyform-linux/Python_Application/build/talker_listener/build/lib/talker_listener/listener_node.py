import rclpy
import threading
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
from tkinter import Text, Scrollbar, Toplevel, Button, END, BOTH, RIGHT, Y, LEFT, X, ttk


# extra
class SingletonDialog:
    _instance = None

    @classmethod
    def show_info_dialog(cls, message, root, title="Information"):
        if cls._instance is None:
            cls._instance = ScrollableDialog(root, title, message)
            cls._instance.mainloop()

    @classmethod
    def clear(cls):
        if cls._instance:
            cls._instance.destroy()
            cls._instance = None


# listener node dialogwhen showing message
class ScrollableDialog(Toplevel):
    def __init__(self, root, title, message, listener):
        # starting initialize
        super().__init__(root)
        self.root = root
        self.title(title)
        self.geometry("400x300")
        style = ttk.Style()
        self.listener = listener
        self.message = message
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.text_widget = tk.Text(self, wrap="word", font=("Helvetica", 20))
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar = Scrollbar(self, command=self.text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_widget.config(yscrollcommand=scrollbar.set)
        self.text_widget.insert(END, self.message)
        self.text_widget.config(state=tk.DISABLED)
        style.configure("TButton", font=("Helvetica", 20))
        ok_button = ttk.Button(self, text="OK", command=self.closemessage)
        ok_button.grid(row=1, column=0, pady=5, sticky="ew")
        clear_button = ttk.Button(self, text="Clear", command=self.clear_text)
        clear_button.grid(row=2, column=0, pady=5, sticky="ew")

    # close message and clear
    def closemessage(self):
        self.listener.message = ""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)
        self.destroy()

    # clear text in dialog
    def clear_text(self):
        self.listener.message = ""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)


# listenerNode
class ListenerNode(Node):
    def __init__(self, root):
        # starting initialize
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
        self.root = root
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
        self.setup_tk_ui()

    # setup listener node dialog ui
    def setup_tk_ui(self):
        self.label = tk.Label(self.root, text="ROS Node Initialized")
        self.label.pack()
        self.show_message_button = tk.Button(
            self.root,
            text="Show Message",
            command=self.show_info_dialog
        )
        self.show_message_button.pack()
    
        # Adding a close button
        self.close_button = tk.Button(
            self.root,
            text="Close",
            command=self.root.destroy  
        )
        self.close_button.pack()
        

    # file listener callback implementation
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

    # selection listener callback implementation
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

    # process excel data for finalization
    def process_excel_data(self, excel_filepath):
        try:
            self.excelitems = pd.read_excel(excel_filepath, sheet_name=None)
            processed_data = {}
            for sheet_name, data in self.excelitems.items():
                df = pd.DataFrame(data)
                for index, row in df.iterrows():
                    original_x = df.at[index, "Position X (m)"]
                    original_y = df.at[index, "Position Y (m)"]
                    original_z = df.at[index, "Position Z (m)"]
                    if original_x < 0:
                        df.at[index, "Position X (m)"] = 0
                    if original_y < 0:
                        df.at[index, "Position Y (m)"] = 0
                    if original_z < 0:
                        df.at[index, "Position Z (m)"] = 0
                    wall_position = np.array(
                        [
                            df.at[index, "Position X (m)"],
                            df.at[index, "Position Y (m)"],
                            df.at[index, "Position Z (m)"],
                        ]
                    )
                    distance = self.calculate_distance(
                        self.picked_position, wall_position
                    )
                    wallnumberreq = str(df.at[index, "Wall Number"])
                    if distance == 0 and self.wallselection == wallnumberreq:
                        self.message +=  (
                            f"{self.spacing}Points in {self.picked_position} {row['Wall Number']} " 
                            f"on sheet {sheet_name} are marked."
                        )
                        df.at[index, "Status"] = "done"
                    df.at[index, "Position X (m)"] = original_x
                    df.at[index, "Position Y (m)"] = original_y
                    df.at[index, "Position Z (m)"] = original_z
                processed_data[sheet_name] = df
            with pd.ExcelWriter(excel_filepath, engine="openpyxl") as writer:
                for sheet_name, df in processed_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                self.message += f"{self.spacing}Excel data processed successfully."
        except FileNotFoundError as e:
            message = f"Excel file not found: {e}"
            print(message)
        except Exception as e:
            message = f"Failed to process Excel file: {e}"
            print(message)

    # set callback for listener and talker
    def set_file_callback(self, callback):
        self.file_callback = callback

    def set_selection_callback(self, callback):
        self.selection_callback = callback

    # distance calculation between two points
    def calculate_distance(self, point1, point2):
        return np.linalg.norm(point1 - point2)

    # show dialog
    def show_info_dialog(self):
        if self.active_dialog:
            self.active_dialog.destroy()
            self.active_dialog = None
        if self.message != "":
            self.active_dialog = ScrollableDialog(
                self.root, "Listener Node", self.message, self
            )
            self.active_dialog.mainloop()


# run ros
def run_ros_spin(listenerNode):
    rclpy.spin(listenerNode)


# main runner for ros process runner
def main(args=None):
    root = tk.Tk()
    rclpy.init(args=args)
    listenerNode = ListenerNode(root)
    ros_thread = threading.Thread(target=run_ros_spin, args=(listenerNode,))
    ros_thread.start()
    root.mainloop()
    listenerNode.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
