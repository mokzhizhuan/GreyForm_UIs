# ui_progress.py
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import html

class ProgressUI(QObject):
    set_warning_sig  = pyqtSignal(str)
    set_progress_sig = pyqtSignal(str)

    def __init__(self, warning_label, progress_label, wall_labels,
                 cross_icon_path="cross.png", tick_icon_path="check.png", parent=None):
        try: super().__init__(parent)
        except TypeError: super().__init__(None)

        self.warninglabel  = warning_label
        self.progresslabel = progress_label
        self.labels        = list(map(str, wall_labels))
        self.cross_icon_path = cross_icon_path
        self.tick_icon_path  = tick_icon_path
        self._done = set()

        # deliver on UI thread
        self.set_warning_sig.connect(self.warninglabel.setText,  type=Qt.QueuedConnection)
        self.set_progress_sig.connect(self._apply_progress_html, type=Qt.QueuedConnection)

        # defaults
        self.warninglabel.setTextFormat(Qt.RichText)
        self.progresslabel.setTextFormat(Qt.RichText)
        self.progresslabel.setWordWrap(False)
        self.progresslabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def _apply_progress_html(self, html_text: str):
        # force RichText every time (in case someone set PlainText elsewhere)
        self.progresslabel.setTextFormat(Qt.RichText)
        self.progresslabel.setText(html_text)

    def set_progress_list(self, wall_labels=None, done=None, cross=None, tick=None):
        wall_labels = self.labels if wall_labels is None else list(map(str, wall_labels))
        done  = self._done if done is None else set(map(str, done))
        cross = self.cross_icon_path if cross is None else cross
        tick  = self.tick_icon_path  if tick  is None else tick

        parts = [
            "<div style='font-weight:700;margin-bottom:8px'>Progress:</div>",
            "<table cellspacing='0' cellpadding='6' style='border-collapse:collapse;'>"
        ]
        for lab in wall_labels:
            esc = html.escape(lab, quote=True)
            icon = tick if lab in done else cross
            parts.append(
                f"<tr data-wall='{esc}'>"
                f"<td style='padding-right:18px;white-space:nowrap;'>Wall {esc}</td>"
                f"<td class='icon'><img src='{icon}' width='20' height='20'/></td>"
                f"</tr>"
            )
        parts.append("</table>")
        self.set_progress_sig.emit("".join(parts))

    def set_processing_warning(self, wall_label, img="processing.png"):
        wall_label = html.escape(str(wall_label), quote=True)
        self.set_warning_sig.emit(
            "<div style='display:inline-block;font-size:16px'>"
            f"<img src='{img}' width='18' height='18' style='vertical-align:middle;margin-right:8px'/>"
            f"<b>Please wait.</b> The robot is now marking wall <b>{wall_label}</b>."
            "</div>"
        )

    def mark_done(self, wall_label):
        self._done.add(str(wall_label))
        self.set_progress_list()

    def set_all_done(self, message=None, check_icon_path="check.png"):
        n = len(self.labels)
        if message is None:
            message = f"All {n} walls have been marked. Marking is completed."
        html = (
            "<div style='font-size:14px'>"
            f"<img src='{check_icon_path}' width='16' height='16' "
            "style='vertical-align:middle;margin-right:8px'/>"
            f"{message}"
            "</div>"
        )
        self.warninglabel.setTextFormat(Qt.RichText)
        self.set_warning_sig.emit(html)
