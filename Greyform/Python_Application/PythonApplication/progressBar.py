from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QProgressBar,
    QLabel,
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
import pyvista as pv
import PythonApplication.createmesh as Createmesh
import PythonApplication.loadpyvista as loadingstl
from stl import mesh


# progress bar to load the imported stl to pyvista or gl view widget
class pythonProgressBar(QDialog):
    def __init__(
        self,
        value,
        plotterloader,
        plotterloader_2,
        file_path,
        renderer,
        renderWindowInteractor,
        Xlabel,
        Ylabel,
        Xlabel_before,
        Ylabel_before,
        Zlabel_before,
        seq1Button,
        seq2Button,
        seq3Button,
        NextButton_Page_3,
        Seqlabel,
    ):
        super().__init__()
        progress_layout = QVBoxLayout()
        self.setWindowTitle("Progress Window")
        self.setGeometry(100, 100, 600, 200)
        self.setLayout(progress_layout)
        label = QLabel("Graphics is loading , please wait.")
        label.setGeometry(QtCore.QRect(50, 30, 200, 100))
        label.setFont(QFont('Arial', 30)) 
        label.setWordWrap(True)
        label.setObjectName("label")
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFont(QFont('Arial', 30))
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setGeometry(30, 130, 340, 200)
        self.value = value
        self.loader = plotterloader
        self.loader_2 = plotterloader_2
        self.filepath = file_path
        self.meshsplot = None
        self.renderer = renderer
        self.renderWindowInteractor = renderWindowInteractor
        self.Ylabel = Ylabel
        self.Xlabel = Xlabel
        self.Xlabel_before = Xlabel_before
        self.Ylabel_before = Ylabel_before
        self.Zlabel_before = Zlabel_before
        self.seq1Button = seq1Button
        self.seq2Button = seq2Button
        self.seq3Button = seq3Button
        self.NextButton_Page_3 = NextButton_Page_3
        self.Seqlabel = Seqlabel
        self.start_progress()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)
        progress_layout.addWidget(label)
        progress_layout.addWidget(self.progress_bar)

    def start_progress(self):
        if self.meshsplot:
            self.loader.remove_actor(self.meshsplot)
            self.loader_2.remove_actor(self.meshsplot)
        QTimer.singleShot(self.value, self.add_mesh_later)

    def update_progress(self):
        value = self.progress_bar.value()
        if value < 100:
            self.progress_bar.setValue(value + 1)
            QTimer.singleShot(100, self.update_progress)
        else:
            self.timer.stop()  
            self.progress_bar.setValue(0)  # Reset progress to 0
            self.timer.start(100)

    # add mesh in pyvista frame
    def add_mesh_later(self):
        self.update_progress()
        input_stl_path = self.filepath
        scale_factor = 1.5  # Increase size by 150%
        output_stl_path = "output.stl"
        self.resize_stl(input_stl_path, scale_factor, output_stl_path)
        self.meshsplot = pv.read(output_stl_path)
        loadingstl.StLloaderpyvista(self.meshsplot, self.loader , self.loader_2)
        Createmesh.createMesh(
            self.renderer,
            output_stl_path,
            self.renderWindowInteractor,
            self.Ylabel,
            self.Xlabel,
            self.Xlabel_before,
            self.Ylabel_before,
            self.Zlabel_before,
            self.seq1Button,
            self.seq2Button,
            self.seq3Button,
            self.NextButton_Page_3,
            self.Seqlabel,
        )
        self.close()

    def resize_stl(self, file_path, scale_factor, output_path):
        Mesh = mesh.Mesh.from_file(file_path)
        Mesh.vectors *= scale_factor
        Mesh.update_normals()
        Mesh.save(output_path)
