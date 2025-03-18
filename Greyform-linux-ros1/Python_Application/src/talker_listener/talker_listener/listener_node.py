#!/usr/bin/env python3
import rospy
import threading
import sys
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall
from stl import mesh
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication, QDialog, QTextEdit, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QThread

class ROSNotifier(QDialog):
    """ A PyQt5 dialog that accumulates ROS messages in a log window """

    log_signal = pyqtSignal(str)  # Signal to update log
    show_signal = pyqtSignal()    # Signal to show the dialog

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROS Log Messages")
        self.setGeometry(100, 100, 600, 400)

        # Layout and widgets
        layout = QVBoxLayout()
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # Make log read-only
        layout.addWidget(self.text_edit)

        # Close button
        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.hide)  # Hide instead of closing
        layout.addWidget(self.close_button)

        self.setLayout(layout)

        # Connect signals to functions
        self.log_signal.connect(self.update_log)
        self.show_signal.connect(self.show_window)

    def closeEvent(self, event):
        """ Override close event to hide instead of destroying window """
        self.hide()
        event.ignore()  # Prevent actual closing

    def update_log(self, message):
        """ Update the log window with new messages """
        self.text_edit.append(message)

    def show_window(self):
        """ Show the window only when `process_excel_data()` is called """
        self.showNormal()
        self.raise_()

class ListenerNode:
    """ A single instance of ListenerNode that uses one persistent log window """

    def __init__(self, notifier):
        self.notifier = notifier  # Use the same notifier instance
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

        # Store logs but do not show them until `process_excel_data()`
        self.log_buffer = []  # 🛑 Logs are buffered here until Excel processing

    def file_listener_callback(self, msg):
        """ Process STL and Excel file messages but DO NOT show logs yet """
        try:
            self.log_buffer.append(f"📥 STL file received: {msg.stl_data[:10]}")
            self.log_buffer.append(f"📁 Excel file path: {msg.excelfile}")

            # Process the Excel file
            self.process_excel_data(msg.excelfile)  # ✅ Show logs only after this step
        except Exception as e:
            self.log_buffer.append(f"❌ Error processing STL file: {e}")

    def selection_listener_callback(self, msg):
        """ Process selection messages but DO NOT show logs yet """
        try:
            self.log_buffer.append(f"✅ Selection received: Wall={msg.wallselection}, Type={msg.typeselection}, Position={msg.picked_position}")
            self.wallselection = msg.wallselection
            self.typeselection = msg.typeselection
            self.picked_position = msg.picked_position
        except Exception as e:
            self.log_buffer.append(f"❌ Failed to process selection: {e}")

    def process_excel_data(self, excel_filepath):
        """ Process Excel data and update logs (only now, the log window will appear) """
        try:
            self.log_buffer.append(f"Processing Excel file: {excel_filepath}")

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

        except FileNotFoundError as e:
            self.log_buffer.append(f"❌ Excel file not found: {e}")
        except Exception as e:
            self.log_buffer.append(f"❌ Failed to process Excel file: {e}")

        # ✅ Now send all logs to ROSNotifier and SHOW the dialog
        for log in self.log_buffer:
            rospy.loginfo(log) if "❌" not in log else rospy.logerr(log)
            self.notifier.log_signal.emit(log)  # Update PyQt5 UI
        
        self.log_buffer.clear()  # ✅ Clear buffer after displaying logs
        self.notifier.show_signal.emit()  # ✅ Now show the log window

def run_ros(listener):
    """ Run rospy.spin() in a separate thread to handle callbacks """
    rospy.spin()

def main():
    """ Main function to run PyQt5 and ROS together """
    app = QApplication(sys.argv)  # ✅ PyQt5 must run in the main thread
    notifier = ROSNotifier()  # ✅ Create log window

    # ✅ Initialize ROS in the main thread
    listener = ListenerNode(notifier)

    # ✅ Run rospy.spin() in a separate thread
    ros_thread = threading.Thread(target=run_ros, args=(listener,), daemon=True)
    ros_thread.start()

    sys.exit(app.exec_())  # ✅ Start the PyQt5 event loop in the main thread

if __name__ == "__main__":
    main()
