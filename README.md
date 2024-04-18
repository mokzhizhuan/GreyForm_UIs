Install python libraries using system commands<br>
(For linux is sudo(admin pricileges):<br>
pip/pip3 install pyvistaqt <br>
pip/pip3 install ifcopenshell <br>
pip/pip3 install vtk <br>
pip/pip3 install PyQt5 <br>
pip/pip3 install multiprocess <br>
pip/pip3 install pyqtgraph <br>
pip/pip3 install OpenGL <br>
pip/pip3 install numpy-stl<br>
pip/pip3 install meshio<br>
Enable robot function(I will implement later) : <br>
##

Extendsion Used:<br>
QtPython <br>
Python 3.11 <br> <br>

UI_Drawinng is included.
##
Steps on running the system:<br>
Run your cmd on your file location:<br>
cd file_path/GreyForm_UIs/GreyForm/Python_Application/<br>
python/python3 mainapplication.py
##
For Visual Studio: <br>
Open Folder to file_path/GreyForm_UIs/GreyForm/Python_Application/<br>
python/python3 mainapplication.py

##
Main Classes:<br>                               
MainApplication > Mainframe(main classes, consist of 6 pages) > Starting Menu > File Selection Mesh > Sequence Selection > Marking UI > Marking Button Ui > Setting UI

##
Sub Classes:<br>
createmesh > progressBarvtk > interactiveevent <br>
menu_confirm <br>
fileselectionmesh > progressBar <br>
menu_close <br>
setsequence 
enable_robot

##
Loading the STL link , using the STL file extension. <br>
This program is only load STL file for the frames. 
