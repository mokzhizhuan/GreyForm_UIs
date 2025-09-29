# worker_exec.py
from PyQt5.QtCore import QObject, pyqtSignal
import time

class ExecWorker(QObject):
    finished = pyqtSignal(bool, str)  # ok, msg

    def __init__(self, listenerdialog, rows, excel_path):
        super().__init__()
        self.listenerdialog = listenerdialog
        self.rows = rows
        self.excel_path = excel_path
        self._stop = False

    def request_stop(self):
        self._stop = True

    def run(self):
        try:
            for r in self.rows:
                if self._stop:
                    self.finished.emit(False, "Stopped")
                    return
                # do a small chunk of work here
                # e.g. self.listenerdialog.process_row(self.excel_path, r)
                time.sleep(0.005)  # never tight-loop; allows stop to bite
            self.finished.emit(True, "Completed")
        except Exception as e:
            self.finished.emit(False, f"Error: {e}")
