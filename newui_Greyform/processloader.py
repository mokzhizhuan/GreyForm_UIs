from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time  # Simulate work


class WorkerThread(QThread):
    update_progress = pyqtSignal(int)
    update_status = pyqtSignal(str)
    render_mesh = pyqtSignal()  # New signal to trigger mesh rendering

    def __init__(self, listenerdialog, stackedWidget):
        super().__init__()
        self.listenerdialog = listenerdialog
        self.stackedWidget = stackedWidget

    def run(self):
        for i in range(101):  # Simulate a task progressing from 0% to 100%
            time.sleep(0.05)
            self.update_progress.emit(i)
            self.update_status.emit(f"Please wait, the robot is currently marking the wall.")
        self.scancompleted()  # Run completion function

    def scancompleted(self):
        self.listenerdialog.run_listener_node()
        self.render_mesh.emit()  # Emit signal to update UI
