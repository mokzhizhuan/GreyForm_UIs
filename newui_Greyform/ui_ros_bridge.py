import re, rospy
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from std_msgs.msg import String, Bool

class UiRosBridge(QObject):
    placement_done_qt = pyqtSignal()

    _started_ui  = pyqtSignal(str)
    _done_ui     = pyqtSignal(str)
    _finish_ui   = pyqtSignal()

    def _log(self, msg: str):
        try: rospy.loginfo(msg)
        except Exception:
            try: print(msg)
            except Exception: pass

    def __init__(self, pui, walls_ordered, parent=None):
        try: super().__init__(parent)
        except TypeError: super().__init__(None)
        self.pui   = pui
        self.walls = [self._canon(w) for w in walls_ordered]
        self.done  = set()
        self._active_subset = set()
        self._prev_started = None  # track last started wall
        self._started_ui.connect(self._on_started_ui, type=Qt.QueuedConnection)
        self._done_ui.connect(self._on_done_ui,       type=Qt.QueuedConnection)
        self._finish_ui.connect(self._finalize_ui,    type=Qt.QueuedConnection)
        if not rospy.core.is_initialized():
            rospy.init_node("ui_ros_bridge", anonymous=True, disable_signals=True)
        rospy.Subscriber("/ui/wall_started", String, self._on_started_ros)
        rospy.Subscriber("/ui/wall_done",    String, self._on_done_ros)
        rospy.Subscriber("/ui/all_done",     Bool,   self._on_all_done_ros)
        self.pui.set_progress_list(self.walls, done=self.done)

    @staticmethod
    def _canon(s: str) -> str:
        s = str(s)
        m = re.search(r'\b0*(\d+)\b', s)
        if m:
            try: return str(int(m.group(1)))
            except Exception: return m.group(1)
        if re.search(r'\b(F|FL|FLOOR)\b', s, flags=re.I):
            return 'F'
        m = re.search(r'\b([A-Za-z])\b', s)
        return m.group(1).upper() if m else s.strip().upper()

    def set_active_subset(self, labels_for_this_placement) -> None:
        self._active_subset = {
            self._canon(x) for x in (labels_for_this_placement or []) if str(x).strip()
        }

    def _on_started_ros(self, msg: String):
        lab = self._canon(getattr(msg, "data", ""))
        prev = getattr(self, "_prev_started", None)
        if prev and prev != lab:
            if prev not in self.done and (not self._active_subset or prev in self._active_subset):
                self.done.add(prev)
                self._log(f"[bridge:ROS] TICK previous '{prev}', done_now={sorted(self.done)}")
                self.pui.set_progress_list(self.walls, done=self.done)
                self._done_ui.emit(prev)
        try:
            self.pui.set_processing_warning(lab, img="processing.png")
        except Exception:
            pass

        self._started_ui.emit(lab)
        self._prev_started = lab

    def _on_done_ros(self, msg: String):
        lab = self._canon(getattr(msg, "data", ""))
        if self._active_subset and (lab not in self._active_subset):
            self._log(f"[bridge:ROS] IGNORE '{lab}' (not in active subset)")
            return
        if lab and (lab not in self.done):
            self.done.add(lab)
            self._log(f"[bridge:ROS] ADDED '{lab}', done_now={sorted(self.done)}")
            self.pui.set_progress_list(self.walls, done=self.done)
            self._done_ui.emit(lab)

    def _on_all_done_ros(self, msg: Bool):
        if getattr(msg, "data", False):
            self._finish_ui.emit()

    def _on_started_ui(self, lab: str):
        self._log(f"[bridge:UI] START slot '{lab}'")

    def _on_done_ui(self, lab: str):
        lab = self._canon(lab)
        self._log(f"[bridge:UI] DONE slot '{lab}' seen; done_now={sorted(self.done)}")
        self.pui.set_progress_list(self.walls, done=self.done)

    def _finalize_ui(self):
        subset = self._active_subset or set(self.walls)
        for lab in subset:
            if lab not in self.done:
                self.done.add(lab)
        self.pui.set_progress_list(self.walls, done=self.done)
        self._log(f"[bridge:UI] FINALIZE subset -> merged done={sorted(self.done)}")
        try: self.placement_done_qt.emit()
        except Exception: pass
