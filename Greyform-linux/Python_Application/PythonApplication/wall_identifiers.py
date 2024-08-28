from PyQt5.QtCore import *
from vtk import *
import vtk


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
        self.renderwindowinteractor = setcamerainteraction[3]
        self.file_path = setcamerainteraction[17]
        self.reader = setcamerainteraction[10]
        self.ros_node = ros_node

    def setwallinteractiondata(self, obj, event):
        self.interactor_style.SetMotionFactor(8)
        click_pos = self.renderwindowinteractor.GetEventPosition()
        picker = vtk.vtkCellPicker()
        self.renderwindowinteractor.GetRenderWindow().GetInteractor().SetPicker(picker)
        picker.Pick(click_pos[0], click_pos[1], 0, self.render)
        self.picked_position = [
            picker.GetPickPosition()[0],
            picker.GetPickPosition()[1],
            picker.GetPickPosition()[2],
        ]
        self.point_id = self.find_closest_point(self.reader, self.picked_position)
        self.localizebutton.show()
        self.localizebutton.clicked.connect(self.publish_message)

    def find_closest_point(self, polydata, target_position):
        point_locator = vtk.vtkKdTreePointLocator()
        point_locator.SetDataSet(polydata)
        point_locator.BuildLocator()
        point_id = point_locator.FindClosestPoint(target_position)
        return point_id

    def publish_message(self):
        self.exceldata = "exporteddatas.xlsx"
        print(self.file_path)
        if self.file_path:
            if ".stl" in self.file_path:
                self.ros_node.publish_file_message(
                    self.file_path,
                    self.exceldata,
                    self.picked_position,
                    self.point_id,
                    self.reader,
                )
            elif ".ifc" in self.file_path:
                file = "output.stl"
                self.ros_node.publish_file_message(
                    file,
                    self.exceldata,
                    self.picked_position,
                    self.point_id,
                    self.reader,
                )
            elif ".dxf" in self.file_path:
                file = "output.stl"
                self.ros_node.publish_file_message(
                    file,
                    self.exceldata,
                    self.picked_position,
                    self.point_id,
                    self.reader,
                )
        else:
            print("No STL file selected.")
