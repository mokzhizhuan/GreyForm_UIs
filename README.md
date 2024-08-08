Install python libraries using system commands<br>
(For linux is sudo(admin pricileges):<br>
pip/pip3 install pyvistaqt <br>
pip/pip3 install ifcopenshell <br>
pip/pip3 install vtk <br>
pip/pip3 install PyQt5 <br>
pip/pip3 install multiprocess <br>
pip/pip3 install pyqtgraph <br>
pip/pip3 install OpenGL <br>
pip/pip3 install numpy-stl <br>
pip/pip3 install meshio <br>
pip/pip3 install openxyl <br>
pip/pip3 install pandas <br>
Enable robot function must install ros2 <br>
ros humble software link:<br>
https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html <br>
setting up ros workspaces:<br>
https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html<br>
##

Extendsion Used:<br>
QtPython <br>
Python 3.11 <br> 
Python 3.10(linux) <br><br>

UI_Drawinng is included and including layout for uidesign and box layout <br>

##
Steps on running the system:<br>
Run your cmd on your file location:<br>
cd file_path/GreyForm_UIs/GreyForm/Python_Application/<br>
python/python3 mainapplication.py<br>
for ros running<br>
make sure the application run in ~/ros2_ws/src<br>
once the project folder in ~/ros2_ws/src , cd ~/ros2_ws/src/-----/PythonApplication(example)<br>
Type command colcon build <br>
after colcon build check for ament-cake and ros distro, rosidl_default_generator) , if dont have the installation . Please Install them <br>
after colcon build is fixed, type source /opt/ros/humble/setup.bash and source install/setup.bash to source the link of the setup.bash <br>
run python/python3 mainapplication.py<br>

##
For Visual Studio: <br>
Open Folder to file_path/GreyForm_UIs/GreyForm/Python_Application/<br>
python/python3 mainapplication.py<br>
<br>

##
insert interactive event for the stl mesh , left click is for moving the stl  <br>
Right click is to insert the actor in the room view , right click for room interact shower and toilet <br>
middle click is to insert an object tht was marked <br>
l key is to remove the actor in the room view and set the mesh to the original position <br>
m Key is to restore moving position <br>
Lastly , disable one movement. if the mesh struck collision . it will disable one movement key, this will prevent crashing the cameraactor program <br>
include thickness based on the dorr using revit and vtk thickness for stl <br>

##
IFC format: <br>
excel format <br> 
Stl Format to load pyvista <br>

##
configuration of ros <br>
ros publisher and Ros Subscriber are linked to qt Python GUI<br>

##
Main Classes:<br>                               
MainApplication > Mainframe(main classes, consist of 6 pages) > Starting Menu > File Selection Mesh > Sequence Selection > Marking UI > Marking Button Ui > Setting UI

##
Sub Classes:<br>
createmesh > progressBarvtk > interactiveevent <br>
menu_confirm <br>
fileselectionmesh > progressBar                          > load_pyvistaframe <br>
                  > ifcpythondialog > excel_export_info                      <br>
menu_close <br>
setsequence 
enable_robot
setting UI > Wifi <br>
           > About <br>
           > Service IP Address <br>
           > Services <br>
           > User Account <br> > Change Password Page <br>
                               > Upload Home BIM File > Upload BIM File > Localization File Progress UI > Select Localization Marking > Marking Completed <br>
                                                      > Delete BIM FIle <br>
           > Restart/Shutdown <br>
           > About <br>

##
Loading the STL link , using the STL file extension. <br>
This program is only load STL file for the frames. <br>
Ifc will be loaded and will convert to STL file format to load pyvista. <br>

##
Progress: <br>
None
