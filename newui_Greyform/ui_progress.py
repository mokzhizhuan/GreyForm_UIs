from PyQt5.QtCore import QObject, pyqtSignal, Qt
import html

class ProgressUI(QObject):
    set_warning_sig  = pyqtSignal(str)
    set_progress_sig = pyqtSignal(str)

    # 🔹 add a tiny logger on the UI side too
    def _log(self, msg: str):
        try:
            print(msg)  # stdout is fine for UI layer
        except Exception:
            pass

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
        self.set_warning_sig.connect(self.warninglabel.setText,  type=Qt.QueuedConnection)
        self.set_progress_sig.connect(self._apply_progress_html, type=Qt.QueuedConnection)
        self.warninglabel.setTextFormat(Qt.RichText)
        self.progresslabel.setTextFormat(Qt.RichText)
        self.progresslabel.setWordWrap(False)
        self.progresslabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def _apply_progress_html(self, html_text: str):
        self.progresslabel.setTextFormat(Qt.RichText)
        self.progresslabel.setText(html_text)


    def _ensure_init(self):
        if not hasattr(self, "_done"):
            self._done = set()
        if not hasattr(self, "labels"):
            self.labels = []

    def mark_done(self, label):
        self._ensure_init()
        if label is None:
            return
        lab = str(label).strip()
        self._done.add(lab)
        self.set_progress_list(self.labels, done=self._done)


    def mark_done_subset(self, subset):
        self._ensure_init()
        if not subset:
            return
        subset = {str(x).strip() for x in subset}
        self._done |= subset
        self.set_progress_list(self.labels, done=self._done)


    def set_progress_list(self, wall_labels=None, done=None, cross=None, tick=None):
        import html as _html
        self._ensure_init()
        if wall_labels is not None:
            self.labels = [str(x).strip() for x in wall_labels]
        if done is not None:
            self._done = {str(x).strip() for x in done}
        cross = self.cross_icon_path if cross is None else cross
        tick  = self.tick_icon_path  if tick  is None else tick
        rows = [self.labels[i:i+2] for i in range(0, len(self.labels), 2)]
        parts = [
            "<div style='font-weight:700;margin-bottom:8px;font-size:20px'>Progress:</div>",
            "<table cellspacing='0' cellpadding='6' style='border-collapse:collapse;table-layout:fixed;width:100%;max-width:520px;'>"
        ]
        def _cell_html(label_str: str) -> str:
            esc = _html.escape(label_str, quote=True)
            is_done = (label_str in self._done)
            icon = tick if is_done else cross
            return (
                "<td style='vertical-align:middle;white-space:nowrap;width:50%;'>"
                f"  <img src='{icon}' width='40' height='40' style='vertical-align:middle;margin-right:6px'/>"
                f"  <span style='font-size:20px;'>Wall {esc}</span>"
                "</td>"
            )
        for pair in rows:
            parts.append("<tr>")
            parts.append(_cell_html(pair[0]))
            parts.append(_cell_html(pair[1]) if len(pair) == 2 else "<td style='width:50%;'></td>")
            parts.append("</tr>")
        parts.append("</table>")
        self.set_progress_sig.emit("".join(parts))

    def set_processing_warning(self, wall_label, img="processing.png"):
        wall_label = html.escape(str(wall_label), quote=True)
        self.set_warning_sig.emit(
            "<div style='display:inline-block;font-size:20px'>"
            f"<img src='{img}' width='40' height='40' style='vertical-align:middle;margin-right:8px'/>"
            f"<b>Please wait.</b> The robot is now marking wall <b>{wall_label}</b>."
            "</div>"
        )

    def set_all_done(self, message=None, check_icon_path="check.png"):
        n = len(self.labels)
        if message is None:
            message = f"All {n} walls have been marked. Marking is completed."
        html_msg = (
            "<table cellspacing='0' cellpadding='0' style='border-collapse:collapse;'>"
            "  <tr>"
            f"    <td style='vertical-align:top;padding-right:8px;'>"
            f"      <img src='{check_icon_path}' width='40' height='40'/>"
            "    </td>"
            f"    <td style='font-size:20px; line-height:1.4;'>"
            f"      {message}"
            "    </td>"
            "  </tr>"
            "</table>"
        )
        self.warninglabel.setTextFormat(Qt.RichText)
        self.set_warning_sig.emit(html_msg)

    def set_done_for_subset(self, subset: set) -> None:
        subset = {str(x).strip() for x in (subset or set()) if str(x).strip()}
        self._done |= subset
        self.set_progress_list(self.labels, done=self._done)
