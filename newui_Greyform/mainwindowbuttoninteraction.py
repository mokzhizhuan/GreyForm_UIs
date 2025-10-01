from PyQt5 import QtCore , QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QProgressBar, QLabel, QApplication , QStyle, QWidget , QHBoxLayout
from PyQt5.QtCore import Qt, QBuffer, QByteArray, QIODevice , QThread , pyqtSignal , QObject
from PyQt5.QtGui import QFont , QPixmap
import re
import processlistenerrunner as process
import processloader as Thread
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from ui_progress import ProgressUI
import requests, pathlib


def _parse_wall_int(x):
    """Return an int for '3', 3, 'Wall 3', else None."""
    if x is None:
        return None
    s = str(x)
    m = re.search(r"\d+", s)
    return int(m.group(0)) if m else None


def _is_seq(x):
    if isinstance(x, (list, tuple, set)):
        return True
    if np is not None and isinstance(x, np.ndarray):
        return True
    return False


# main window button interaction
class mainwindowbuttonUI(object):
    def __init__(
        self,
        mainwindow,
        stackedWidget,
        nextButton,
        leftButton,
        beginButton,
        rightButton,
        warninglabel,
        progresslabel,
        stl_file,
        ros_node,
        args,
        wall_numbers_by_placement,
        indicatelabel,
        nextstepButton
    ):
        super().__init__()
        self.mainwindow = mainwindow
        self.stackedWidget = stackedWidget
        self.nextButton = nextButton
        self.leftButton = leftButton
        self.beginButton = beginButton
        self.rightButton = rightButton
        self.warninglabel = warninglabel
        self.progresslabel = progresslabel
        self.indicatelabel = indicatelabel
        self.ros_node = ros_node
        self.stl_file = stl_file
        self.nextstepButton =  nextstepButton
        self.args = args
        self.wall_numbers_by_placement = wall_numbers_by_placement
        self.n = 0
        self._pui = None
        self._ros_bridge = None
        self.button_UI()
        
    def payload_to_df(self, payload):
        if not payload: 
            return pd.DataFrame()
        return pd.DataFrame({
            "Name": payload["markingidentifiers"],
            "Wall Number": payload["Wall Number"],
            "Position X": payload["Position X"],
            "Position Y": payload["Position Y"],
            "Position Z": payload["Position Z"],
            "Marking Type": payload["Shape Type"],
            "Width": payload["width"],
            "Height": payload["height"],
            "Status": payload["Status"],
        })

    def _stop_worker_if_running(self):
        w = getattr(self, "worker", None)
        if w is None:
            return
        try:
            if w.isRunning():
                w.stop()
        except Exception:
            pass
        try:
            w.deleteLater()
        except Exception:
            pass
        self.worker = None

    def _get_status_label(self):
        return getattr(self, "labelstatus", None) or getattr(self, "warninglabel", None)

    def set_status_ok(self, msg: str):
        lbl = self._get_status_label()
        if not lbl:
            return
        lbl.setTextFormat(Qt.RichText)
        lbl.setText(
            "<div style='font-size:14px'>"
            "<img src='check.png' width='16' height='16' "
            "style='vertical-align:middle;margin-right:8px'/>"
            f"{msg}"
            "</div>"
        )

    def set_status_error(self, msg: str):
        lbl = self._get_status_label()
        if not lbl:
            return
        lbl.setTextFormat(Qt.RichText)
        lbl.setText(
            "<div style='font-size:14px;color:#b00020'>"
            "<img src='cross.png' width='16' height='16' "
            "style='vertical-align:middle;margin-right:8px'/>"
            f"{msg}"
            "</div>"
        )
    
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
        if self.n == 1 :
            icon = "placement2.png"
            html = f'<div style="text-align:left;"><img src="{icon}" width="800" height="600" style="display:block; margin:0 auto;"></div>'
            self.mainwindow.imagelabel.setTextFormat(Qt.RichText)
            self.mainwindow.imagelabel.setText(html)
        self.nextButton.setEnabled(False)
        self.indicatelabel.hide()
        self.update_status_label("Please wait , the robot calculating its position.")
        self.worker = Thread.WorkerThread(self.listenerdialog, self.stackedWidget)
        self.worker.update_status.connect(self.update_status_label)
        self.worker.render_mesh.connect(self.beginmarking)
        self.worker.start()

    def beginmarking(self):
        icon = "check.png"
        icon_left = "left.png"
        icon_right = "right.png"
        text_left = "The robot is not correctly centered. Please move the robot to the left."
        text_right = "The robot is not correctly centered. Please move the robot to the left."
        text = "The robot is now correctly centered and is ready to mark the wall."
        html = f'<div style="text-align:center;"><img src="{icon}" width="50" height="50" style="display:block; margin:0 auto;">{text}</div>'
        self.warninglabel.setTextFormat(Qt.RichText)
        self.warninglabel.setText(html)
        self.beginButton.show()
        self.nextButton.hide()
        self.beginButton.clicked.connect(self.create_mesh)

    def update_status_label(self, text: str):
        icon = "processing.png"
        html = f'<div style="text-align:center;"><img src="{icon}" width="50" height="50" style="display:block; margin:0 auto;">{text}</div>'
        self.warninglabel.setTextFormat(Qt.RichText)
        self.warninglabel.setText(html)
        QApplication.processEvents() 

    def format_wall(self, n):
        try:
            return f"Wall {int(n):02d}"
        except Exception:
            return "Wall ----"

    def build_summary_text(self, data, icon="cross.png"):
        nums = data.get("Wall Number", [])
        counts = Counter(self.format_wall(n) for n in nums)
        lines = [f"{k} : {counts[k]} × {icon}" for k in sorted(counts, key=self.sort_key(k))]
        return "\n".join(lines)

    def sort_key(self, k: str):
        if k == "Wall ----":
            return (1, 9999)
        try:
            return (0, int(k.split()[1]))
        except Exception:
            return (1, 9999)

    def _sorted_global_labels(self):
        def _sort_key_wall_label(s: str):
            s = str(s).strip()
            m = re.search(r"\d+", s)
            return (0, int(m.group())) if m else (1, s)
        all_labels_set = set()
        for payload in self.wall_numbers_by_placement.values():
            for v in payload.get("Wall Number", []):
                sv = str(v).strip()
                if sv:
                    all_labels_set.add(sv)
        return sorted(all_labels_set, key=_sort_key_wall_label)

    def _bridge_done_now(self):
        try:
            return set(self._ros_bridge.done)
        except Exception:
            return set()

    def create_mesh(self):
        self.beginButton.hide()
        self.nextstepButton.setEnabled(False)
        self.nextstepButton.hide()
        key = f"placement{self.n + 1}"
        df = self.payload_to_df(self.wall_numbers_by_placement.get(key, {}))
        from ui_ros_bridge import UiRosBridge
        canon = UiRosBridge._canon
        all_labels_raw = self._sorted_global_labels()
        all_labels = [canon(v) for v in all_labels_raw]
        def _uniq_canon(seq):
            seen, out = set(), []
            for x in (seq or []):
                cx = canon(x)
                if cx and cx not in seen:
                    seen.add(cx); out.append(cx)
            return out
        p1_raw = (self.wall_numbers_by_placement.get("placement1") or {}).get("Wall Number", [])
        p1 = _uniq_canon(p1_raw)
        if any(x.isdigit() for x in p1):
            p1 = [x for x in p1 if x.isdigit()]
        p2 = [lab for lab in all_labels if lab not in set(p1)]
        placement_labels = p1 if (self.n == 0) else p2
        if not hasattr(self, "_pui") or self._pui is None:
            self._pui = ProgressUI(
                self.warninglabel, self.progresslabel, all_labels,
                cross_icon_path="cross.png", tick_icon_path="check.png",
            )
            self._pui.set_progress_list(all_labels, done=set())
        else:
            self._pui.labels = list(all_labels)
            self._pui.set_progress_list(all_labels, done=self._bridge_done_now())
        first_display = next((x for x in placement_labels if x.isdigit()), (placement_labels[0] if placement_labels else None))
        if first_display:
            self._pui.set_processing_warning(first_display, img="processing.png")
        self.progresslabel.show()
        if not hasattr(self, "_ros_bridge") or self._ros_bridge is None:
            self._ros_bridge = UiRosBridge(self._pui, all_labels)
        else:
            self._ros_bridge.walls = list(all_labels)
        self._ros_bridge.set_active_subset(set(placement_labels))
        try:
            import rospy
            rospy.loginfo(f"[ui] Placement {self.n+1} subset = {sorted(set(placement_labels))}")
        except Exception:
            print(f"[ui] Placement {self.n+1} subset = {sorted(set(placement_labels))}")
        rows = df.to_dict(orient="records")
        class ExecWorker(QObject):
            finished = pyqtSignal(bool, str)
            def __init__(self, listenerdialog, rows, excel_path, progresslabel, warninglabel):
                super().__init__()
                self.listenerdialog = listenerdialog
                self.rows = rows
                self.excel_path = excel_path
                self.progresslabel = progresslabel
                self.warninglabel = warninglabel
            def run(self):
                try:
                    self.listenerdialog.run_execution(
                        self.rows, self.excel_path, self.progresslabel, self.warninglabel
                    )
                    self.finished.emit(True, "Completed.")
                except Exception as e:
                    self.finished.emit(False, f"Error: {e}")
        _thread = QThread()
        _worker = ExecWorker(
            self.listenerdialog, rows, self.args.output_excel, self.progresslabel, self.warninglabel
        )
        def _after_thread_stopped():
            try: _worker.deleteLater()
            except: pass
            try: _thread.deleteLater()
            except: pass
            try:
                self._ros_bridge.placement_done_qt.disconnect()
            except Exception:
                pass
            self._ros_bridge.placement_done_qt.connect(self._wire_next_button)
            self._ros_bridge._finish_ui.emit()
        _worker.moveToThread(_thread)
        _thread.started.connect(_worker.run)
        def _on_worker_finished(ok: bool, msg: str):
            _thread.quit()
        _worker.finished.connect(_on_worker_finished)
        _thread.finished.connect(_after_thread_stopped)
        _thread.start()

    def _placement_count(self):
        return sum(1 for k in self.wall_numbers_by_placement.keys() if str(k).startswith("placement"))

    def _wire_next_button(self):
        self.nextstepButton.setEnabled(True)
        self.nextstepButton.show()
        count = self._placement_count()
        is_last = (self.n + 1) >= count
        try:
            self.nextstepButton.clicked.disconnect()
        except Exception:
            pass
        try:
            done_count = len(self._ros_bridge.done)  # how many walls are done globally
            self._pui.set_all_done(
                message=f"All {done_count} walls have been marked. Marking is completed."
            )
        except Exception:
            pass
        if is_last:
            self.nextstepButton.setText("Finish")
            iconindicator = "placementindicatorcompleted.png"
            htmlindicator = f'<div style="text-align:center;"><img src="{iconindicator}" style="display:block; margin:0 auto;"></div>'
            self.mainwindow.imageplacelabel.setTextFormat(Qt.RichText)
            self.mainwindow.imageplacelabel.setText(htmlindicator)
            self.nextstepButton.clicked.connect(self._finish_and_close)
        else:
            self.nextstepButton.setText("Proceed to the next Placement")
            self.nextstepButton.clicked.connect(lambda: (
                setattr(self, "n", self.n + 1),
                self.movetothenextstep()
            ))
        self.nextstepButton.setEnabled(True)
        self.nextstepButton.show()


    def _finish_and_close(self):
        try:
            self.set_status_ok("All walls have been marked. Marking is completed.")
        except Exception:
            pass
        try:
            self.finalize()
        except Exception:
            pass
        try:
            self.mainwindow.close()
        except Exception:
            try:
                self.mainwindow.accept()
            except Exception:
                pass

    def _parse_wall_int(self, v):
        if v is None:
            return None
        s = str(v)
        m = re.search(r"\d+", s)
        return int(m.group(0)) if m else None

    def _unique_walls_in_placement(self, placement_idx: int):
        key = f"placement{placement_idx}"
        payload = self.wall_numbers_by_placement.get(key, {})
        walls = payload.get("Wall Number", [])
        uniq = {self._parse_wall_int(w) for w in walls}
        uniq.discard(None)
        return sorted(uniq)

    def _unique_walls_all(self):
        uniq = set()
        for pdata in self.wall_numbers_by_placement.values():
            for w in pdata.get("Wall Number", []):
                wi = self._parse_wall_int(w)
                if wi is not None:
                    uniq.add(wi)
        return sorted(uniq)

    def completedplacement2(self):
        walls_here = self._unique_walls_in_placement(self.n + 1)
        count_here = len(walls_here)
        self.set_status_ok(f"All {count_here} walls have been marked.\nMarking is completed.")
        self.finalize()

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
        # Prepare UI for next placement; keep progress visible
        self.nextstepButton.hide()
        self.nextButton.show()
        self.nextButton.setEnabled(True)
        self.hide_status_icon()
        self.indicatelabel.show()
        self.progresslabel.hide()
        iconindicator = "placementindicator2.png"
        icon = "placement1-2.png"
        html = f'<div style="text-align:left;"><img src="{icon}" width="800" height="600" style="display:block; margin:0 auto;"></div>'
        htmlindicator = f'<div style="text-align:center;"><img src="{iconindicator}" style="display:block; margin:0 auto;"></div>'
        self.mainwindow.imagelabel.setTextFormat(Qt.RichText)
        self.mainwindow.imagelabel.setText(html)
        self.mainwindow.imageplacelabel.setTextFormat(Qt.RichText)
        self.mainwindow.imageplacelabel.setText(htmlindicator)
        self.warninglabel.setText("Place the robot in the center of the wall that is clockwise of wall 1")
        self.nextButton.clicked.connect(lambda: self.start_scan())

    def finalize(self):
        try:
            self.mainwindow.close()
        except Exception:
            pass
        pidfile = Path("/tmp/greyform_ui.pid")
        if pidfile.exists():
            txt = pidfile.read_text().strip()
            if txt.isdigit():
                requests.post(
                    "http://localhost:8000/api/ui_closed",
                    data={"pid": int(txt)},
                    timeout=1.0
                )
        app = QtWidgets.QApplication.instance()
        if app is not None:
            QtCore.QTimer.singleShot(0, app.quit)
        
    # button interaction ui
    def button_UI(self):
        self.listenerdialog = process.ListenerNodeRunner(
            self.ros_node, self.stl_file , self.warninglabel, self.stackedWidget
        )
        self.nextButton.clicked.connect(lambda: self.start_scan())