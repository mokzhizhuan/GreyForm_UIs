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

    # marking shape event
    def MiddleButtonPressEvent(self, obj, event):
        clickPos = self.interactor_style.GetInteractor().GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.render)
        pickedPos = picker.GetPickPosition()
        for i in range(len(pickedPos)):
            self.pickerround.append(round(picker.GetPickPosition()[i]))
        if len(self.points) < 2:#2nd marking
            self.points.append(self.pickerround)
            print(f"Point {len(self.points)} picked at: {self.pickerround}")
            self.createCube()  # 1st marking recorded
            self.pickerround = []
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
                points_text = ", ".join(
                    str(point) for point in self.points
                )  # Format list of points into a string
                print(f"Two points picked: {points_text}")

                self.pointstorage.append(self.points)
            elif len(self.points) == 2:
                self.points.remove(self.points[1])
                self.render.RemoveActor(self.crossActor)
                self.append_filterpolydata.RemoveInputData(
                    self.crossActor.GetMapper().GetInput()
                )
                print(
                    "Error for the 2nd marking sequence , the 2nd marking sequence must be the same x, y axis or x , z axis. Please try again."
                )
        else:#reset array
            self.points = []

        self.interactor_style.OnMiddleButtonDown()
        return

    def createCube(self):
        size_yz = 40

        # Create a cube for marking
        cubeSource = vtk.vtkCubeSource()
        cubeSource.SetXLength(size_yz)
        cubeSource.SetYLength(size_yz)
        cubeSource.SetZLength(size_yz)

        # Create a mapper for the cube data
        self.crossMapper = vtk.vtkPolyDataMapper()
        self.crossMapper.SetInputConnection(cubeSource.GetOutputPort())

        self.crossActor = vtk.vtkActor()
        self.crossActor.SetPosition(
            self.pickerround[0], self.pickerround[1], self.pickerround[2]
        )
        self.crossActor.GetProperty().SetLineWidth(40)  # Set line width to 40 points
        self.crossActor.SetMapper(self.crossMapper)
        self.crossActor.GetProperty().SetColor(1, 0, 0)  # Red color
        self.render.AddActor(self.crossActor)#add actor to the render
        self.append_filterpolydata.AddInputData(self.crossActor.GetMapper().GetInput())#add input data for append filter
        self.renderwindowinteractors.GetRenderWindow().Render()
