import vtk
from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# this class is to scan the marking but for now it inserted a shape for the point of an object
"""For this implementation, the robot will scan the object and convert it to an stl object
read the stl image using vtk plugin and send it to the vtk frame as an actor , 
set the position where it mark with xyz coordinates and inserted in the vtkframe"""


class MiddleButtonPressed(object):
    def __init__(
        self, interactor_style, render, renderwindowinteractors, append_filterpolydata
    ):
        self.interactor_style = interactor_style
        self.render = render
        self.renderwindowinteractors = renderwindowinteractors
        self.points = []
        self.pointstorage = []
        self.pickerround = []
        self.append_filterpolydata = append_filterpolydata

    def MiddleButtonPressEvent(self, obj, event):
        clickPos = self.interactor_style.GetInteractor().GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.render)
        pickedPos = picker.GetPickPosition()
        # Create a QMessageBox
        msg_box = QMessageBox()

        # Apply a stylesheet to the QMessageBox
        msg_box.setStyleSheet(
            "QLabel{color: red;} QPushButton{ width: 100px; font-size: 16px; }"
        )
        for i in range(len(pickedPos)):
            self.pickerround.append(round(picker.GetPickPosition()[i]))
        if len(self.points) < 2:
            self.points.append(self.pickerround)
            print(f"Point {len(self.points)} picked at: {self.pickerround}")
            self.createCube()
            self.pickerround = []
            if len(self.pointstorage) == 0:
                if (
                    len(self.points) == 2
                    and (
                        (
                            self.points[1][0] <= self.points[0][0] + 3
                            and self.points[1][0] >= self.points[0][0] - 3
                        )
                        and (
                            self.points[1][1] <= self.points[0][1] + 3
                            and self.points[1][1] >= self.points[0][1] - 3
                        )
                    )
                    or (
                        len(self.points) == 2
                        and (
                            self.points[1][0] <= self.points[0][0] + 3
                            and self.points[1][0] >= self.points[0][0] - 3
                        )
                        and (
                            self.points[1][2] <= self.points[0][2] + 3
                            and self.points[1][2] >= self.points[0][2] - 3
                        )
                    )
                ):
                    msg_box.setIcon(QMessageBox.Information)
                    msg_box.setWindowTitle("Success")
                    points_text = ", ".join(
                        str(point) for point in self.points
                    )  # Format list of points into a string
                    message = f"Two points picked: {points_text}"
                    msg_box.setText(message)
                    msg_box.setDefaultButton(QMessageBox.Ok)

                    # Show the message box
                    msg_box.exec_()
                    self.pointstorage.append(self.points)
                    points_texts = ", ".join(str(point) for point in self.pointstorage)
                    print(f"{points_texts}")
                elif len(self.points) == 2:
                    self.points.remove(self.points[1])
                    self.render.RemoveActor(self.crossActor)
                    self.append_filterpolydata.RemoveInputData(
                        self.crossActor.GetMapper().GetInput()
                    )
                    # Set the icon, title, text and buttons for the message box
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setWindowTitle("Error")
                    msg_box.setText(
                        "Error for the 2nd marking sequence , the 2nd marking sequence must be the same x, y axis or x , z axis. Please try again."
                    )
                    msg_box.setStandardButtons(QMessageBox.Ok)

                    # Show the message box
                    msg_box.exec_()
        else:
            self.points = []

        self.interactor_style.OnMiddleButtonDown()
        return

    def createCube(self):
        # Define the size of the cross
        size_yz = 40

        # Create points for the cross shape
        points = vtk.vtkPoints()
        points.InsertNextPoint(0, 0, 0)  # Center point
        points.InsertNextPoint(0, size_yz / 2, 0)  # Top point
        points.InsertNextPoint(0, -size_yz / 2, 0)  # Bottom point
        points.InsertNextPoint(0, 0, size_yz / 2)  # Front point
        points.InsertNextPoint(0, 0, -size_yz / 2)  # Back point

        # Create lines to connect the points
        lines = vtk.vtkCellArray()
        # Y-axis lines
        lines.InsertNextCell(2)
        lines.InsertCellPoint(0)
        lines.InsertCellPoint(1)
        lines.InsertNextCell(2)
        lines.InsertCellPoint(0)
        lines.InsertCellPoint(2)
        # Z-axis lines
        lines.InsertNextCell(2)
        lines.InsertCellPoint(0)
        lines.InsertCellPoint(3)
        lines.InsertNextCell(2)
        lines.InsertCellPoint(0)
        lines.InsertCellPoint(4)

        # Create a polydata to hold the points and lines
        self.polydata = vtk.vtkPolyData()
        self.polydata.SetPoints(points)
        self.polydata.SetLines(lines)

        self.crossMapper = vtk.vtkPolyDataMapper()
        self.crossMapper.SetInputData(self.polydata)

        self.crossActor = vtk.vtkActor()
        self.crossActor.SetPosition(
            self.pickerround[0], self.pickerround[1], self.pickerround[2]
        )
        self.crossActor.GetProperty().SetLineWidth(40)  # Set line width to 40 points
        self.crossActor.SetMapper(self.crossMapper)
        self.crossActor.GetProperty().SetColor(1, 0, 0)  # Red color
        self.render.AddActor(self.crossActor)
        self.append_filterpolydata.AddInputData(self.crossActor.GetMapper().GetInput())
        self.renderwindowinteractors.GetRenderWindow().Render()
