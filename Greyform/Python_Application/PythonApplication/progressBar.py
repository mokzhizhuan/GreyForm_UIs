from PyQt5 import  QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QProgressBar, QLabel
from PyQt5.QtCore import QTimer
import pyvista as pv

class pythonProgressBar(QDialog):
    def __init__(self, value , plotterloader, plotterloader_2, file_path):
        super().__init__()
        progress_layout = QVBoxLayout()
        self.setWindowTitle("Progress Window")
        self.setGeometry(100, 100, 400, 200)
        self.setLayout(progress_layout)
        label = QLabel("Graphics is loading , please wait.")
        label.setGeometry(QtCore.QRect(50, 30, 170, 30))
        label.setWordWrap(True)
        label.setObjectName("label")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 130, 340, 30)
        self.value = value
        self.loader = plotterloader
        self.loader_2 = plotterloader_2
        self.filepath = file_path
        self.start_progress()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100) 
        progress_layout.addWidget(label)
        progress_layout.addWidget(self.progress_bar)

    def start_progress(self):
        # Start the progress after a delay
        QTimer.singleShot(self.value, self.add_mesh_later)

    def update_progress(self):
        value = self.progress_bar.value()
        if value < 100:
            self.progress_bar.setValue(value + 1) 
            QTimer.singleShot(100, self.update_progress)  # Update progress again after 100 milliseconds
        else:
            self.timer.stop()  # Stop the timer when progress reaches 100%
            self.progress_bar.setValue(0)  # Reset progress to 0
            self.timer.start(100)

    def add_mesh_later(self):
        self.update_progress()
        meshsplot = pv.read(self.filepath)
        self.loader.add_mesh(meshsplot, color=(230, 230, 250), show_edges=True, edge_color=(128,128,128) ,cmap="terrain", clim=[1,3] ,  name='roombuilding', opacity="linear")
        self.loader_2.add_mesh(meshsplot, color=(230, 230, 250), show_edges=True, edge_color=(128,128,128) ,cmap="terrain", clim=[1,3] ,  name='roombuilding', opacity="linear")
        #show Frame
        self.loader.show()
        self.loader_2.show()
        self.close()


