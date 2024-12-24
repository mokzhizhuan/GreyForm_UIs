from PyQt5.QtCore import *
from vtk import *
import vtk
import pandas as pd
import numpy as np
import PythonApplication.processlistenerrunner as ProcessListener
import tkinter as tk
import PythonApplication.exceldatalegend as datalegends


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
        self.Stagelabel = setcamerainteraction[16]
        self.excelfiletext = setcamerainteraction[17]
        self.cubeactor = setcamerainteraction[9]
        self.dataseqtext = setcamerainteraction[18]
        self.markingreq = setcamerainteraction[19]
        self.maxlen = setcamerainteraction[20]
        self.counter = setcamerainteraction[21]
        self.dialog = setcamerainteraction[22]
        self.Stagetext = setcamerainteraction[23]
        self.interaction_enabled = True
        self.ros_node = ros_node
        self.spacing = "\n"
        incurdatamethod = datalegends.Exportexcelinfolegend(self.markingreq)
        self.markingitems = incurdatamethod.returndata()
        self.counter = 0

    # middle click interaction for storing
    def setwallinteractiondata(self, obj, event):
        if (
            self.Stagetext.text() == "Stage 1"
            or self.Stagetext.text() == "Stage 2"
            or self.Stagetext.text() == "Stage 3"
        ):
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
        else:
            self.show_error_message(
                "Invalid Stage , please click the Stage 1, 2, 3 button."
            )

    # publisher to listener and talker node runner
    def wall_storing(self):
        self.wall_filtered_identifiers = self.fliterbywallnum()
        self.wallnumber, self.sectionnumber = self.distance(
            self.pickedposition, self.picked_position_quad
        )
        self.markingitemsbasedonwallnumber = {}
        for stage, data in self.markingitems.items():
            filtered_data = {
                "markingidentifiers": [],
                "wall_numbers": [],
                "posX": [],
                "posY": [],
                "posZ": [],
                "Shape type": [],
            }

            for i, wall_number in enumerate(data["wall_numbers"]):
                if wall_number == self.wallnumber:
                    filtered_data["markingidentifiers"].append(
                        data["markingidentifiers"][i]
                    )
                    filtered_data["wall_numbers"].append(wall_number)
                    filtered_data["posX"].append(data["Position X (m)"][i])
                    filtered_data["posY"].append(data["Position Y (m)"][i])
                    filtered_data["posZ"].append(data["Position Z (m)"][i])
                    filtered_data["Shape type"].append(data["Shape type"][i])
            if filtered_data["wall_numbers"]:
                self.markingitemsbasedonwallnumber[stage] = filtered_data
        if self.markingitemsbasedonwallnumber:
            self.show_message(f"Items that are near the wall are stored.{self.spacing}{self.markingitemsbasedonwallnumber}")
        else:
            self.show_error_message("There are no items avaiable in the wall")

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
        root.withdraw()
        tk.messagebox.showinfo("Message", message)
        root.destroy()

    # include error message
    def show_error_message(self, message):
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Error", message)
        root.destroy()

    # filtered by wall number for specify which item was at the wall number
    def fliterbywallnum(self):
        df = pd.DataFrame(self.wall_identifiers)
        grouped = df.groupby("Wall Number")
        return grouped

    # message variable will be sent to process runner for running the talker node and listener node
    def publish_message_ros(self, file, wallnumber, sectionnumber):
        self.exceldata = self.excelfiletext.toPlainText()
        """self.talker_node.run_listernernode(
            file,
            exceldata,
            wall_number,
            sectionnumber,
            picked_position,
            Stagelabel,
            cube_actor,
        )"""
        self.listenerdialog = ProcessListener.ListenerNodeRunner(
            self.ros_node,
            file,
            self.exceldata,
            wallnumber,
            sectionnumber,
            self.markingitemsbasedonwallnumber,
            self.Stagelabel,
            self.cubeactor,
            self.dataseqtext,
            self.maxlen,
            self.counter,
            self.markingreq,
            self.dialog,
        )
        self.listenerdialog.show()

    # distance checker
    def distance(self, sequence_pos, sequence_pos_quad):
        self.threshold_distance = 220
        self.distances = 50
        self.distancerange = 600
        wall_number = None
        sectionnumber = None
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
            else:
                wall_number = "F"
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

    # distance calculation
    def calculate_distances(self, point1, point2):
        point1 = np.expand_dims(point1, axis=1)  # Shape (3,) becomes (3, 1)
        distances = np.linalg.norm(point1 - point2, axis=0)
        return distances

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

    # different between two distances
    def calculate_distance(self, point1, point2):
        return point1 - point2

    # check stage name
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
