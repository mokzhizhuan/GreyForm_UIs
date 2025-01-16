from PyQt5.QtCore import *
from vtk import *
import vtk
import pandas as pd
import numpy as np
import PythonApplication.processlistenerrunner as ProcessListener
import tkinter as tk
import PythonApplication.exceldatavtk as vtk_data_excel
from tkinter import ttk


# wall interaction to interact with ros listener and ros talker
class wall_Interaction(object):
    def __init__(
        self,
        interactor_style,
        setcamerainteraction,
        wall_identifiers,
        localizebutton,
        ros_node,
    ):
        # starting initialize
        super().__init__()
        self.interactor_style = interactor_style
        self.setcamerainteraction = setcamerainteraction
        self.wall_identifiers = wall_identifiers
        self.localizebutton = localizebutton
        self.render = setcamerainteraction[0]
        self.meshbound = setcamerainteraction[2]
        self.renderwindowinteractor = setcamerainteraction[1]
        self.file_path = setcamerainteraction[15]
        self.reader = setcamerainteraction[8]
        self.excelfiletext = setcamerainteraction[16]
        self.cubeactor = setcamerainteraction[9]
        self.dialog = setcamerainteraction[17]
        self.Stagetext = setcamerainteraction[18]
        self.floor = setcamerainteraction[19]
        self.wall = setcamerainteraction[20]
        self.wall_identifiers = setcamerainteraction[21]
        self.stagestorage = setcamerainteraction[22]
        self.currentindexstage = setcamerainteraction[23]
        self.Stagelabel = setcamerainteraction[24]
        self.walls = setcamerainteraction[25]
        self.wall_actors = setcamerainteraction[26]
        self.interaction_enabled = True
        self.ros_node = ros_node
        self.spacing = "\n"
        self.wallnumber = 0
        # self.markingitems = incurdatamethod.returndata()

    # middle click interaction for storing
    def setwallinteractiondata(self, obj, event):
        if (
            self.Stagetext == "Stage 1"
            or self.Stagetext == "Stage 2"
            or self.Stagetext == "Stage 3"
        ):
            self.wall_identifiers , self.walls , self.excelfiletext = vtk_data_excel.exceldataextractor()
            self.interactor_style.SetMotionFactor(8)
            click_pos = self.renderwindowinteractor.GetEventPosition()
            picker = vtk.vtkCellPicker()
            self.renderwindowinteractor.GetRenderWindow().GetInteractor().SetPicker(
                picker
            )
            picker.Pick(click_pos[0], click_pos[1], 0, self.render)
            self.pickedposition = [
                picker.GetPickPosition()[0],
                picker.GetPickPosition()[1],
                picker.GetPickPosition()[2],
            ]
            self.picked_position_quad = [
                picker.GetPickPosition()[0],
                picker.GetPickPosition()[1],
                picker.GetPickPosition()[2],
            ]
            self.wall_storing()
            self.localizebutton.show()
            self.localizebutton.clicked.connect(self.publish_message)

    # publisher to listener and talker node runner
    def wall_storing(self):
        self.markingitemsbasedonwallnumber = {}
        stage_data = self.wall_identifiers[self.Stagetext]
        items = stage_data.get("markingidentifiers", [])
        walls = stage_data.get("wall_numbers", [])
        positionx = stage_data.get("Position X (m)", [])
        positiony = stage_data.get("Position Y (m)", [])
        positionz = stage_data.get("Position Z (m)", [])
        shapetype = stage_data.get("Shape type", [])
        status = stage_data.get("Status", [])
        transformed = {}
        for wall, item, x, y, z, shape , statu in zip(
            walls, items, positionx, positiony, positionz, shapetype , status
        ):
            if wall not in transformed and statu != "done":
                transformed[wall] = []
            transformed[wall].append(
                {
                    "markingidentifier": item,
                    "Wall Number": wall,
                    "Position X (m)": x,
                    "Position Y (m)": y,
                    "Position Z (m)": z,
                    "Shape type": shape,
                }
            )
        for i, (wall, data) in enumerate(self.wall.items()):
            if (
                data["pos_x_range"][0]
                <= self.pickedposition[0]
                <= data["pos_x_range"][1]
                and data["pos_y_range"][0]
                <= self.pickedposition[1]
                <= data["pos_y_range"][1]
                and 145 <= self.pickedposition[2] <= data["height"]
            ):
                self.wallnumber = wall
                self.sectionnumber = self.determine_orientation(
                    self.pickedposition[0],
                    self.pickedposition[1],
                    self.pickedposition[2],
                    wall,
                )
                filtered_data = transformed.get(wall, [])
        self.markingitemsbasedonwallnumber = filtered_data
        if self.markingitemsbasedonwallnumber:
            self.show_message(
                f"Items that are near the wall are stored.{self.spacing}{self.markingitemsbasedonwallnumber}"
            )
        else:
            error_message = (
                f"There are no items avaiable to mark in the wall.{self.spacing}"
                f"Please choose another wall."
            )
            self.show_error_message(error_message)

    def determine_orientation(self, posx, posy, posz, wallnum):
        combined_2_and_4_width = self.wall[2]["width"] + self.wall[4]["width"]
        combined_3_and_5_width = self.wall[3]["width"] + self.wall[5]["width"]
        total_height = self.wall[1]["height"]
        orientation = 0
        for index, (wall, bounds) in enumerate(self.wall.items()):
            if wallnum == wall:
                if wall in [2, 4, 6]:  # Walls facing the X-axis (compare X and Z)
                    if posx > combined_2_and_4_width / 2:  # East
                        if posz > total_height / 2:  # Upper
                            orientation = 1  # Northeast (Upper)
                        else:  # Lower
                            orientation = 3  # Southeast (Lower)
                    else:  # West
                        if posz > total_height / 2:  # Upper
                            orientation = 2  # Northwest (Upper)
                        else:  # Lower
                            orientation = 4  # Southwest (Lower)
                elif wall in [1, 3, 5]:  # Walls facing the Y-axis (compare Y and Z)
                    if posy > combined_3_and_5_width / 2:  # North
                        if posz > total_height / 2:  # Upper
                            orientation = 1  # Northeast (Upper)
                        else:  # Lower
                            orientation = 3  # Southeast (Lower)
                    else:  # South
                        if posz > total_height / 2:  # Upper
                            orientation = 2  # Northwest (Upper)
                        else:  # Lower
                            orientation = 4  # Southwest (Lower)
        return orientation

    def publish_message(self):
        if self.markingitemsbasedonwallnumber:
            if self.file_path:
                if ".stl" in self.file_path:
                    self.publish_message_ros(
                        self.file_path, self.wallnumber, self.sectionnumber
                    )
                elif ".ifc" in self.file_path:
                    file = "output.stl"
                    self.publish_message_ros(file, self.wallnumber, self.sectionnumber)
                elif ".dxf" in self.file_path:
                    file = "output.stl"
                    self.publish_message_ros(file, self.wallnumber, self.sectionnumber)
                else:
                    if message_error == True:
                        self.show_error_message("File is invalid, please try again")
                        message_error = False
                    else:
                        return
        else:
            errormessage = (
                f"There is no object intact with the wall, Please click another wall"
                f"{self.spacing} Wall Number : {self.wallnumber}"
                f"{self.spacing} Data : {self.markingitemsbasedonwallnumber}"
                f"{self.spacing}Position : {self.pickedposition}"
            )
            self.show_error_message(errormessage)

    def show_message(self, message):
        root = tk.Tk()
        root.title("Message")
        root.geometry("500x300") 
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.config(state=tk.NORMAL) 
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)  
        close_button = ttk.Button(root, text="Close", command=root.destroy)
        close_button.pack(pady=10)
        root.mainloop()

    # include error message
    def show_error_message(self, message):
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Error", message)
        root.destroy()

    # message variable will be sent to process runner for running the talker node and listener node
    def publish_message_ros(self, file, wallnumber, sectionnumber):
        self.exceldata = self.excelfiletext
        self.listenerdialog = ProcessListener.ListenerNodeRunner(
            self.ros_node,
            file,
            self.exceldata,
            wallnumber,
            sectionnumber,
            self.markingitemsbasedonwallnumber,
            self.Stagetext,
            self.cubeactor,
            self.dialog,
            self.stagestorage,
            self.currentindexstage,
            self.Stagelabel
        )
        self.listenerdialog.show()

    # quadrant vision for wall
    def determine_quadrant(self, x, y):
        if x > 0 and y > 0:
            return 1  # Quadrant I
        elif x < 0 and y > 0:
            return 2  # Quadrant II
        elif x < 0 and y < 0:
            return 3  # Quadrant III
        elif x > 0 and y < 0:
            return 4  # Quadrant IV
        else:
            return None  # On the axes or at the origin
