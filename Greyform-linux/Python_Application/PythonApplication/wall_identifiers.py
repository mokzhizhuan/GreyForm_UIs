from PyQt5.QtCore import *
from vtk import *
import vtk
import pandas as pd


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
        self.seqlabel = setcamerainteraction[18]
        self.excelfiletext = setcamerainteraction[19]
        self.cubeactor = setcamerainteraction[11]
        self.ros_node = ros_node
        self.button_connected = False

    def setwallinteractiondata(self, obj, event):
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
        self.point_id = self.find_closest_point(self.reader, self.picked_position)
        self.localizebutton.show()
        if not self.button_connected:
            self.localizebutton.clicked.connect(self.publish_message)
            self.button_connected = True

    def find_closest_point(self, polydata, target_position):
        point_locator = vtk.vtkKdTreePointLocator()
        point_locator.SetDataSet(polydata)
        point_locator.BuildLocator()
        point_id = point_locator.FindClosestPoint(target_position)
        return point_id

    def publish_message(self):
        self.wall_filtered_identifiers = self.fliterbywallnum()
        wallnumber, sectionnumber = self.distance()
        if self.file_path:
            if ".stl" in self.file_path:
                self.publish_message_ros(self.file_path, wallnumber, sectionnumber)
            elif ".ifc" in self.file_path:
                file = "output.stl"
                self.publish_message_ros(file, wallnumber, sectionnumber)
            elif ".dxf" in self.file_path:
                file = "output.stl"
                self.publish_message_ros(file, wallnumber, sectionnumber)
        else:
            print("No STL file selected.")

    def fliterbywallnum(self):
        df = pd.DataFrame(self.wall_identifiers)
        grouped = df.groupby("Wall Number")
        return grouped

    def publish_message_ros(self, file, wallnumber, sectionnumber):
        self.exceldata = self.excelfiletext.toPlainText()
        self.ros_node.publish_file_message(file, self.exceldata)
        self.ros_node.publish_selection_message(
            wallnumber,
            sectionnumber,
            self.picked_position,
            self.seqlabel,
            self.cubeactor,
        )

    def distance(self):
        self.threshold_distance = 220
        self.distances = 50
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
                distance = self.calculate_distance(self.picked_position[0], max_x)
                if distance <= self.distances:
                    wall_number = wall_numbers
                    self.picked_position_quad[1] = self.picked_position[1] - (
                        self.meshbound[3] / 2
                    )
                    self.picked_position_quad[2] = self.picked_position[2] - (
                        self.meshbound[5] / 2
                    )
                    sectionnumber = self.determine_quadrant(
                        self.picked_position_quad[1], self.picked_position_quad[2]
                    )
            elif max_y - min_y <= self.threshold_distance:
                distance = self.calculate_distance(self.picked_position[1], max_y)
                if distance <= self.distances:
                    wall_number = wall_numbers
                    self.picked_position_quad[0] = self.picked_position[0] - (
                        self.meshbound[1] / 2
                    )
                    self.picked_position_quad[2] = self.picked_position[2] - (
                        self.meshbound[5] / 2
                    )
                    sectionnumber = self.determine_quadrant(
                        self.picked_position_quad[0], self.picked_position_quad[2]
                    )
            elif max_z - min_z <= self.threshold_distance:
                distance = self.calculate_distance(self.picked_position[2], max_z)
                if distance <= self.distances:
                    wall_number = wall_numbers
                    self.picked_position_quad[1] = self.picked_position[1] - (
                        self.meshbound[3] / 2
                    )
                    self.picked_position_quad[0] = self.picked_position[0] - (
                        self.meshbound[1] / 2
                    )
                    sectionnumber = self.determine_quadrant(
                        self.picked_position_quad[0], self.picked_position_quad[1]
                    )
        return wall_number, sectionnumber

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

    def calculate_distance(self, point1, point2):
        return point1 - point2
