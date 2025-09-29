# ui_ros_bridge.py
import re, rospy
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from std_msgs.msg import String, Bool

class UiRosBridge(QObject):
    placement_done_qt = pyqtSignal()      # placement finished (all walls ✅)

    # hop-to-UI signals
    _started_ui  = pyqtSignal(str)
    _done_ui     = pyqtSignal(str)
    _finish_ui   = pyqtSignal()           # <-- NEW: finalize from UI thread

    def __init__(self, pui, walls_ordered, parent=None):
        try: super().__init__(parent)
        except TypeError: super().__init__(None)

        self.pui   = pui
        self.walls = [str(w) for w in walls_ordered]   # e.g. ['1','4','5','6','F']
        self.done  = set()
        self._current = None

        self.pui.set_progress_list(self.walls, done=self.done)

        # connect UI-thread handlers
        self._started_ui.connect(self._on_started_ui, type=Qt.QueuedConnection)
        self._done_ui.connect(self._on_done_ui,       type=Qt.QueuedConnection)
        self._finish_ui.connect(self._finalize_ui,    type=Qt.QueuedConnection)  # <-- NEW

        # ROS subscribers (don’t touch Qt from these)
        if not rospy.core.is_initialized():
            rospy.init_node("ui_ros_bridge", anonymous=True, disable_signals=True)
        rospy.Subscriber("/ui/wall_started", String, self._on_started_ros)
        rospy.Subscriber("/ui/wall_done",    String, self._on_done_ros)
        rospy.Subscriber("/ui/all_done",     Bool,   self._on_all_done_ros)


    @staticmethod
    def _canon(s: str) -> str:
        import re
        s = str(s).strip()
        m = re.search(r'([A-Za-z]+|\d+)\s*$', s)   # << last token (letters OR digits)
        return m.group(1) if m else s

        
    def _ensure_label(self, lab: str):
        if lab not in self.walls:
            self.walls.append(lab)

    # ---------- ROS thread → UI thread ----------
    def _on_started_ros(self, msg: String):
        self._started_ui.emit(self._canon(msg.data))

    def _on_done_ros(self, msg: String):
        self._done_ui.emit(self._canon(msg.data))

    def _on_all_done_ros(self, msg: Bool):
        if getattr(msg, "data", False) and len(self.done) == len(set(self.walls)):
            self._finish_ui.emit()

    # ---------- UI-thread slots ----------
    def _on_started_ui(self, lab: str):
        self._ensure_label(lab)
        # tick previous in order (your rule)
        try:
            i = self.walls.index(lab)
            if i > 0:
                prev = self.walls[i-1]
                if prev not in self.done:
                    self.done.add(prev)
                    self.pui.set_progress_list(self.walls, done=self.done)
        except ValueError:
            pass
        self._current = lab
        self.pui.set_processing_warning(lab, img="processing.png")

    def _on_done_ui(self, lab: str):
        self._ensure_label(lab)
        if lab not in self.done:
            self.done.add(lab)
            self.pui.set_progress_list(self.walls, done=self.done)
        self._maybe_emit_placement_done()

    def _finalize_ui(self):
        """Force completion of the active placement (UI thread)."""
        # Canonical, all-string set of walls:
        self.walls = [str(w) for w in self.walls]
        # ✅ Force every listed wall to done
        self.done = set(self.walls)
        self.pui.set_progress_list(self.walls, done=self.done)
        # Tell the controller the placement is finished
        try:
            self.placement_done_qt.emit()
        except Exception:
            pass

    def _maybe_emit_placement_done(self):
        if len(self.done) == len(set(self.walls)):
            self.placement_done_qt.emit()
