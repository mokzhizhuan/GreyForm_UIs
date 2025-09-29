# Thread.py
from PyQt5.QtCore import QThread, pyqtSignal
import time

class WorkerThread(QThread):
    update_status = pyqtSignal(str)
    render_mesh   = pyqtSignal(object)

    def __init__(self, listenerdialog, stackedWidget, parent=None):
        super().__init__(parent)
        self.listenerdialog = listenerdialog
        self.stackedWidget  = stackedWidget

    def run(self):
        for step in range(100):
            if self.isInterruptionRequested():
                return
            # do a chunk of work...
            time.sleep(0.02)  # never tight-loop; lets interruption bite
        # when done:
        self.render_mesh.emit({"ok": True})

    def stop(self, timeout_ms=1000):
        """Ask the thread to stop and wait for it to finish."""
        if self.isRunning():
            self.requestInterruption()
            self.wait(timeout_ms)  # blocks this calling (GUI) thread until it exits
