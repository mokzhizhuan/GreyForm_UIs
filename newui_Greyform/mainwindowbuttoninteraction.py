from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QProgressBar, QLabel, QApplication , QStyle, QWidget , QHBoxLayout
from PyQt5.QtCore import Qt, QBuffer, QByteArray, QIODevice
from PyQt5.QtGui import QFont , QPixmap
import subprocess
import launcher as launchers
import processlistenerrunner as process
import processloader as Thread
import pandas as pd
from pathlib import Path
import processingloader as loaddialogUI

# main window button interaction
class mainwindowbuttonUI(object):
    def __init__(
        self,
        mainwindow,
        stackedWidget,
        confirmButton,
        confirmButton_2,
        nextstepButton,
        labelstatus,
        ros_node,
        stl_file,
        args,
        window,
        renderWindowInteractor,
        wall_numbers_by_placement,
    ):
        # starting initialize
        super().__init__()
        self.mainwindow = window
        self.stackedWidget = stackedWidget
        self.confirmButton = confirmButton
        self.confirmButton_2 = confirmButton_2
        self.nextstepButton = nextstepButton
        self.labelstatus = labelstatus
        self.ros_node = ros_node
        self.stl_file = stl_file
        self.args = args
        self.renderWindowInteractor = renderWindowInteractor
        self.wall_numbers_by_placement = wall_numbers_by_placement
        self.button_UI()
        
    def payload_to_df(self, payload):
        if not payload: 
            return pd.DataFrame()
        return pd.DataFrame({
            "Name": payload["markingidentifiers"],
            "Wall Number": payload["Wall Number"],
            "LX": payload["Position X"],
            "LY": payload["Position Y"],
            "LZ": payload["Position Z"],
            "Marking Type": payload["Shape Type"],
            "Width": payload["width"],
            "Height": payload["height"],
            "Status": payload["Status"],
        })
    
    def mount_status_row(self, size=24):
        parent = self.labelstatus.parent()
        main_lay = parent.layout()
        idx = main_lay.indexOf(self.labelstatus)
        main_lay.removeWidget(self.labelstatus)
        self.status_row = QWidget(parent)
        row = QHBoxLayout(self.status_row)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        self.status_icon = QLabel(self.status_row)
        self.status_icon.setFixedSize(size, size)
        self.status_icon.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.labelstatus.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        row.addWidget(self.status_icon, 0, Qt.AlignVCenter)
        row.addWidget(self.labelstatus, 0, Qt.AlignVCenter)
        main_lay.insertWidget(idx, self.status_row, 0, Qt.AlignHCenter)

    def set_status_ok(self, text):
        style = self.labelstatus.style()  # or QApplication.style()
        pm = style.standardIcon(QStyle.SP_DialogApplyButton).pixmap(24, 24)
        self.status_icon.setPixmap(pm)
        self.labelstatus.setText(text)
    
    def ensure_status_icon_left_of(self, labelstatus, size=24):
        if getattr(labelstatus, "_icon_label", None):
            return labelstatus._icon_label
        icon_label = QLabel(labelstatus.parent())
        icon_label.setFixedSize(size, size)
        icon_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        labelstatus._icon_label = icon_label
        lay = labelstatus.parent().layout()
        if lay:
            idx = lay.indexOf(labelstatus)
            lay.insertWidget(idx, icon_label) if idx >= 0 else lay.addWidget(icon_label)
        return icon_label

    def set_status_with_builtin_icon(self, labelstatus, text, ok=True, size=24):
        icon_label = self.ensure_status_icon_left_of(labelstatus, size)
        icon_enum = QStyle.SP_DialogApplyButton if ok else QStyle.SP_MessageBoxWarning
        icon = labelstatus.style().standardIcon(icon_enum)
        pm = icon.pixmap(size, size)
        icon_label.setPixmap(pm)
        labelstatus.setText(text)
    
    # stacked widget page ui
    def start_scan(self):
        self.worker = Thread.WorkerThread(self.listenerdialog, self.stackedWidget)
        df_p1 =self.payload_to_df(self.wall_numbers_by_placement["placement1"])
        rows_p1 = df_p1.to_dict(orient="records")
        self.listenerdialog.run_execution(rows_p1, self.args.output_excel)
        self.worker.update_status.connect(self.update_status_label)
        self.worker.render_mesh.connect(self.create_mesh)  # Connect new signal
        self.worker.start()  # Start the worker thread

    def start_scan2(self):
        self.worker = Thread.WorkerThread(self.listenerdialog, self.stackedWidget)
        df_p2 =self.payload_to_df(self.wall_numbers_by_placement["placement2"])
        rows_p2 = df_p2.to_dict(orient="records")
        self.listenerdialog.run_execution(rows_p2, self.args.output_excel)
        self.worker.update_status.connect(self.update_status_label)
        self.worker.render_mesh.connect(self.finalize)  # Connect new signal
        self.worker.start()  # Start the worker thread

    def update_status_label(self, text: str):
        if not hasattr(self, "dialog") or self.dialog is None:
            self.dialog = loaddialogUI.LogDialog(self.mainwindow)
        self.dialog.set_text(text)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
        QApplication.processEvents() 

    def create_mesh(self):
        self.dialog.close()
        self.confirmButton.hide()
        self.mount_status_row(size=24)
        self.set_status_ok("Marking is completed. Please move the robot to the next position.")
        self.nextstepButton.show()
        self.nextstepButton.clicked.connect(lambda: self.movetothenextstep())

    def hide_status_icon(self):
        if getattr(self, "_movie", None):
            self._movie.stop()
            self._movie = None
        if hasattr(self, "status_icon") and self.status_icon:
            self._icon_w = getattr(self, "_icon_w", self.status_icon.width())
            self.status_icon.clear()
            self.status_icon.setVisible(False)
            self.status_icon.setFixedWidth(0)

    def movetothenextstep(self):
        self.nextstepButton.hide()
        self.confirmButton_2.show()
        self.hide_status_icon()
        icon = "placement2.png"
        html = f'<div style="text-align:center;"><img src="{icon}" width="800" height="600" style="display:block; margin:0 auto;"></div>'
        self.mainwindow.imagelabel.setTextFormat(Qt.RichText)
        self.mainwindow.imagelabel.setText(html)
        self.labelstatus.setText(f"Place the robot in the center of Placement 2\n(The wall that is clockwise of wall 1)")
        self.confirmButton_2.clicked.connect(lambda: self.start_scan2())

    def finalize(self):
        self.dialog.close()
        launchers.stop()
        self.mainwindow.close()

    def close_status_dialog(self):
        self.dialog.close()       # hides the window
        self.dialog.deleteLater() # cleanup
        self.dialog = None

    # button interaction ui
    def button_UI(self):
        self.listenerdialog = process.ListenerNodeRunner(
            self.ros_node, self.stl_file , self.labelstatus, self.stackedWidget
        )
        self.confirmButton.clicked.connect(lambda: self.start_scan())
