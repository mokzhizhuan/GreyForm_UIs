from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *
from vtkmodules.vtkCommonColor import vtkNamedColors


class doorMesh(object):
    def __init__(self):
        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName("door.stl")
        self.reader.Update()
        self.polydata = self.reader.GetOutput()
        self.includedimension()

    def includedimension(self):
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(self.reader.GetOutputPort())
        actor = vtkActor()
        actor.SetMapper(mapper)
        self.meshbounds = []

        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])

        minBounds = [self.meshbounds[0], self.meshbounds[2], self.meshbounds[4]]
        transform = vtkTransform()
        transform.Translate(-minBounds[0], -minBounds[1], -minBounds[2])
        transformFilter = vtkTransformPolyDataFilter()
        transformFilter.SetInputData(self.polydata)
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        transformedPolyData = transformFilter.GetOutput()
        fixedmapper = vtkPolyDataMapper()
        fixedmapper.SetInputData(transformedPolyData)
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(fixedmapper)
        for i in range(6):
            self.meshbounds[i] = int(self.actor.GetBounds()[i])
        return self.meshbounds
