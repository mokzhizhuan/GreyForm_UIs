import vtk
from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# this class is to scan the marking but for now it inserted a shape
"""For this implementation, the robot will scan the object and convert it to an stl object
read the stl image using vtk plugin and send it to the vtk frame as an actor , 
set the position where it mark with xyz coordinates and inserted in the vtkframe"""


class MiddleButtonPressed(object):
    def __init__(self, interactor_style, render, renderwindowinteractors):
        self.interactor_style = interactor_style
        self.render = render
        self.renderwindowinteractors = renderwindowinteractors
        self.points = []
        self.pointstorage = []
        self.pickerround = []

    def MiddleButtonPressEvent(self, obj, event):
        clickPos = self.interactor_style.GetInteractor().GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.render)
        pickedPos = picker.GetPickPosition()
        for i in range(len(pickedPos)):
            self.pickerround.append(round(picker.GetPickPosition()[i]))
        if len(self.points) < 2:
            self.points.append(self.pickerround)
            print("Point", len(self.points), "picked at:", self.pickerround)
            self.pickerround = []
            if len(self.pointstorage) == 0:
                if len(self.points) == 2:
                    """if (
                        len(self.points) == 2
                        and self.points[0][0] == self.points[1][0]
                        and self.points[0][1] == self.points[1][1]
                    ):"""
                    print("Two points picked:", self.points)
                    self.pointstorage.append(self.points)
                    print(self.pointstorage)
                    self.createCube()
                """elif len(self.points) == 2:
                    self.points.remove(self.points[1])
                    print(
                        "Error for the 2nd marking sequence , the 2nd marking sequence must be the same x, y axis. Please try again."
                    )"""
            elif (
                len(self.pointstorage) != 0
                and self.pointstorage[0][0][0] == self.points[0][0]
                and self.pointstorage[0][0][1] == self.points[0][1]
            ):
                if (
                    len(self.pointstorage) != 0
                    and len(self.points) == 2
                    and self.pointstorage[0][0][0] == self.points[1][0]
                    and self.pointstorage[0][0][1] == self.points[1][1]
                ):
                    print("Two points picked:", self.points)
                    self.pointstorage.append(self.points)
                    print(self.pointstorage)
                    # shape insertion method , temporary method
                    self.createCube()
                elif len(self.points) == 2:
                    """self.points.remove(self.points[1])
                    print(
                        "Error for the 2nd marking sequence , the 2nd marking sequence must be the same x, y axis. Please try again"
                    )#print error"""
            else:
                # reset as 0 array for the variable
                self.points = []
                print(
                    "Error marking sequence must be the same x, y axis. Please try again"
                )  # print error
        else:
            # Reset points if more than two are picked
            self.pickerround = []
            self.points = []

        self.interactor_style.OnMiddleButtonDown()
        return

    def createCube(self):
        if len(self.points) == 2:
            cubeSource = vtk.vtkCubeSource()
            cubeSource.SetCenter(
                (self.points[0][0] + self.points[1][0]) / 2,
                (self.points[0][1] + self.points[1][1]) / 2,
                (self.points[0][2] + self.points[1][2]) / 2,
            )
            cubeSource.SetXLength(40)
            cubeSource.SetYLength(40)
            cubeSource.SetZLength(abs(self.points[1][2] - self.points[0][2]))

            cubeMapper = vtk.vtkPolyDataMapper()
            cubeMapper.SetInputConnection(cubeSource.GetOutputPort())

            cubeActor = vtk.vtkActor()
            cubeActor.SetMapper(cubeMapper)
            cubeActor.GetProperty().SetColor(1, 0, 0)  # Red color
            self.render.AddActor(cubeActor)
            self.renderwindowinteractors.GetRenderWindow().Render()
