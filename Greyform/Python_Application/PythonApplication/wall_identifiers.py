from PyQt5.QtCore import *
from vtk import *
import vtk
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox

#wall interaction to interact with ros listener and ros talker
class wall_Interaction(object):
    def __init__(
        self,
        interactor_style,
        setcamerainteraction,
        wall_identifiers,
        localizebutton,
        ros_node,
    ):
        self.interactor_style = interactor_style
        self.setcamerainteraction = setcamerainteraction
        self.wall_identifiers = wall_identifiers
        self.localizebutton = localizebutton
        self.render = setcamerainteraction[2]
        self.meshbound = setcamerainteraction[4]
        self.renderwindowinteractor = setcamerainteraction[3]
        self.file_path = setcamerainteraction[17]
        self.reader = setcamerainteraction[10]
        self.Stagelabel = setcamerainteraction[18]
        self.excelfiletext = setcamerainteraction[19]
        self.cubeactor = setcamerainteraction[11]
        self.dataseqtext = setcamerainteraction[20]
        self.interaction_enabled = True
        self.ros_node = ros_node
        self.counter = 0
        self.picked_positions = []
        self.picked_position_quads = []

    #middle click interaction for storing
    def setwallinteractiondata(self, obj, event):
        if self.interaction_enabled != True:
            self.show_error_message(
                f"The sequence is already at the max limit of {self.counter}/{self.dataseqtext}. Interaction is disabled. "
            )
            return
        self.interactor_style.SetMotionFactor(8)
        click_pos = self.renderwindowinteractor.GetEventPosition()
        picker = vtk.vtkCellPicker()
        self.renderwindowinteractor.GetRenderWindow().GetInteractor().SetPicker(picker)
        picker.Pick(click_pos[0], click_pos[1], 0, self.render)
        self.picked_position_quad = [
            picker.GetPickPosition()[0],
            picker.GetPickPosition()[1],
            picker.GetPickPosition()[2],
        ]
        self.picked_position = [
            picker.GetPickPosition()[0],
            picker.GetPickPosition()[1],
            picker.GetPickPosition()[2],
        ]
        self.picked_positions.append(self.picked_position)
        self.picked_position_quads.append(self.picked_position_quad)
        if self.counter < self.dataseqtext:
            self.counter += 1
            if self.counter == self.dataseqtext:
                self.localizebutton.show()
                self.localizebutton.clicked.connect(self.publish_message)
                self.interaction_enabled = False

    #publisher to listener and talker node runner
    def publish_message(self):
        self.wall_filtered_identifiers = self.fliterbywallnum()
        message_error = True
        wallnumbers = []
        sectionnumbers = []
        for sequence_pos, sequence_pos_quad in zip(
            self.picked_positions,
            self.picked_position_quads,
        ):
            wallnumber, sectionnumber = self.distance(sequence_pos, sequence_pos_quad)
            wallnumbers.append(wallnumber)
            sectionnumbers.append(sectionnumber)
            if self.file_path:
                if ".stl" in self.file_path:
                    self.publish_message_ros(
                        self.file_path, wallnumbers, sectionnumbers
                    )
                elif ".ifc" in self.file_path:
                    file = "output.stl"
                    self.publish_message_ros(file, wallnumbers, sectionnumbers)
                elif ".dxf" in self.file_path:
                    file = "output.stl"
                    self.publish_message_ros(file, wallnumbers, sectionnumbers)
                else:
                    if message_error == True:
                        self.show_error_message("File is invalid, please try again")
                        message_error = False
                    else:
                        return

    #include error message
    def show_error_message(self, message):
        root = tk.Tk()
        root.mainloop()
        messagebox.showerror("Error", message)
        root.withdraw()
        root.destroy()

    #filtered by wall number for specify which item was at the wall number
    def fliterbywallnum(self):
        df = pd.DataFrame(self.wall_identifiers)
        grouped = df.groupby("Wall Number")
        return grouped

    #distance checker
    def distance(self, sequence_pos, sequence_pos_quad):
        self.threshold_distance = 220
        self.distances = 50
        self.distancerange = 600
        wall_number = None
        for wall_numbers, group in self.wall_filtered_identifiers:
            min_x, max_x = (
                group["Position X (m)"].min(),
                group["Position X (m)"].max(),
            )
            min_y, max_y = (
                group["Position Y (m)"].min(),
                group["Position Y (m)"].max(),
            )
            min_z, max_z = (
                group["Position Z (m)"].min(),
                group["Position Z (m)"].max(),
            )
            if max_x - min_x <= self.threshold_distance:
                distance = self.calculate_distance(sequence_pos[0], max_x)
                if distance <= self.distances:
                    wall_number = wall_numbers
                    wall_position = np.array(
                        [
                            group["Position X (m)"],
                            group["Position Y (m)"],
                            group["Position Z (m)"],
                        ]
                    )
                    distances = self.calculate_distances(sequence_pos, wall_position)
                    if (distances <= self.distancerange).all():
                        name = group["Point number/name"]
                        self.Stagename(self, name)
                    sequence_pos_quad[1] = sequence_pos[1] - (self.meshbound[3] / 2)
                    sequence_pos_quad[2] = sequence_pos[2] - (self.meshbound[5] / 2)
                    sectionnumber = self.determine_quadrant(
                        sequence_pos_quad[1], sequence_pos_quad[2]
                    )
            elif max_y - min_y <= self.threshold_distance:
                distance = self.calculate_distance(sequence_pos[1], max_y)
                if distance <= self.distances:
                    wall_number = wall_numbers
                    wall_position = np.array(
                        [
                            group["Position X (m)"],
                            group["Position Y (m)"],
                            group["Position Z (m)"],
                        ]
                    )
                    distances = self.calculate_distances(sequence_pos, wall_position)
                    if (distances <= self.distancerange).all():
                        name = group["Point number/name"]
                        self.Stagename(self, name)
                    sequence_pos_quad[0] = sequence_pos[0] - (self.meshbound[1] / 2)
                    sequence_pos_quad[2] = sequence_pos[2] - (self.meshbound[5] / 2)
                    sectionnumber = self.determine_quadrant(
                        sequence_pos_quad[0], sequence_pos_quad[2]
                    )
            elif max_z - min_z <= self.threshold_distance:
                distance = self.calculate_distance(sequence_pos[2], max_z)
                if distance <= self.distances:
                    wall_number = wall_numbers
                    wall_position = np.array(
                        [
                            group["Position X (m)"],
                            group["Position Y (m)"],
                            group["Position Z (m)"],
                        ]
                    )
                    distances = self.calculate_distances(sequence_pos, wall_position)
                    if (distances <= self.distancerange).all():
                        name = group["Point number/name"]
                        self.Stagename(self, name)
                    sequence_pos_quad[1] = sequence_pos[1] - (self.meshbound[3] / 2)
                    sequence_pos_quad[0] = sequence_pos[0] - (self.meshbound[1] / 2)
                    sectionnumber = self.determine_quadrant(
                        sequence_pos_quad[0], sequence_pos_quad[1]
                    )
        return wall_number, sectionnumber

    #distance calculation
    def calculate_distances(self, point1, point2):
        point1 = np.expand_dims(point1, axis=1)  # Shape (3,) becomes (3, 1)
        distances = np.linalg.norm(point1 - point2, axis=0)
        return distances

    #quadrant vision for wall
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

    #different between two distances
    def calculate_distance(self, point1, point2):
        return point1 - point2

    #check stage name
    def Stagename(self, name):
        if "CP" in name:
            index = name.index("CP") + 4
            if index < len(name) and name[index].isdigit():
                self.Stagelabel.setText(f"Stage {int(name[index])}")
                self.Stagelabel.repaint()
                return int(name[index])
        if "LP" in name:
            index = name.index("LP") + 4
            if index < len(name) and name[index].isdigit():
                self.Stagelabel.setText(f"Stage {int(name[index])}")
                self.Stagelabel.repaint()
                return int(name[index])
        if "SP" in name:
            index = name.index("SP") + 4
            if index < len(name) and name[index].isdigit():
                self.Stagelabel.setText(f"Stage {int(name[index])}")
                self.Stagelabel.repaint()
                return int(name[index])
        if "TMP" in name:
            index = name.index("TMP") + 5
            if index < len(name) and name[index].isdigit():
                self.Stagelabel.setText(f"Stage {int(name[index])}")
                self.Stagelabel.repaint()
                return int(name[index])
