#!/usr/bin/env python3
import rospy, pandas as pd 
from std_msgs.msg import String, Bool
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall
import re
import os, time, zipfile, shutil, tempfile, threading
try:
    import openpyxl
except Exception:
    openpyxl = None

FILE_TOPIC = "/file_extraction_topic"
SEL_TOPIC  = "/selection_wall_topic"
UI_STARTED = "/ui/wall_started"
UI_DONE    = "/ui/wall_done"
UI_ALLDONE = "/ui/all_done"

def _normalize_wall_token(v: object) -> str:
    """
    Turn '1', 1, 1.0, 'Wall 1', 'W1', '1 ' -> '1'
    Turn 'F', 'floor', 'Floor/Slab' -> 'F'
    Else return uppercased trimmed string for traceability.
    """
    s = str(v).strip().upper()
    m = re.search(r'(\d+)', s)
    if m:
        return m.group(1)               # just the digits
    if s in {"F", "FL", "FLOOR", "FLOOR/SLAB"}:
        return "F"
    return s

def _resolve_sheet_name(xl_sheets: dict, typeselection: str) -> str:
    """
    If typeselection matches a real sheet name (case-insensitive), return it.
    If not, return '' to indicate 'search ALL sheets'.
    """
    if not typeselection:
        return ""
    key = str(typeselection).strip().lower()
    # build case-insensitive map of sheet names
    cmap = {name.strip().lower(): name for name in xl_sheets.keys()}
    return cmap.get(key, "")

class ListenerNode:
    def __init__(self):
        rospy.init_node("listener_node", anonymous=True)

        self.latest_excel = None
        self.pending = None
        self.retry_timer = None

        # Track walls
        self.expected_walls = set()  # to be filled when file is loaded
        self.done_walls = set()

        self.__post_init_io()
        rospy.Subscriber(FILE_TOPIC, FileExtractionMessage, self.file_cb, queue_size=10)
        rospy.Subscriber(SEL_TOPIC,  SelectionWall,        self.selection_cb, queue_size=50)

        self.ui_wall_started_pub = rospy.Publisher(UI_STARTED, String, queue_size=10)
        self.ui_wall_done_pub    = rospy.Publisher(UI_DONE,    String, queue_size=10)
        self.ui_all_done_pub     = rospy.Publisher(UI_ALLDONE, Bool,   queue_size=10)


    # ---------- helpers ----------
    def _get_excel_path(self):
        """No latch. Use cached value or ROS param server."""
        if self.latest_excel:
            return self.latest_excel
        p = rospy.get_param("/excel_path", None)
        if p:
            self.latest_excel = p
            rospy.loginfo(f"[listener] Loaded Excel path from param: {p!r}")
            return p
        return None
    
    def __post_init_io(self):
        self._io_lock = threading.Lock()
        self._IO_RETRY_TRIES = 8
        self._IO_RETRY_SLEEP = 0.25

    def _is_valid_zip(self, path: str) -> bool:
        try:
            return os.path.getsize(path) > 1024 and zipfile.is_zipfile(path)
        except Exception:
            return False

    def _wait_stable(self, path: str, tries=None, sleep=None) -> bool:
        tries = tries or self._IO_RETRY_TRIES
        sleep = sleep or self._IO_RETRY_SLEEP
        last = -1
        for _ in range(tries):
            if not os.path.exists(path):
                time.sleep(sleep); continue
            cur = os.path.getsize(path)
            if cur == last and cur > 0:
                return True
            last = cur
            time.sleep(sleep)
        return False

    def _shadow_copy(self, src: str) -> str:
        """Copy to a same-dir temp file and return its path."""
        d = os.path.dirname(src) or "."
        fd, tmp = tempfile.mkstemp(prefix=".shadow_", suffix=".xlsx", dir=d)
        os.close(fd)
        shutil.copy2(src, tmp)
        return tmp

    def _safe_read_xl_dict(self, excel_path: str):
        """
        Robust reader:
          1) wait for stability
          2) verify zip header
          3) read from a shadow copy with pandas
          4) fallback to openpyxl (if available) to build dfs
        Returns dict(sheet_name -> DataFrame) or raises.
        """
        if not self._wait_stable(excel_path):
            raise IOError("file not stable")
        if not self._is_valid_zip(excel_path):
            raise IOError("not a valid .xlsx zip")

        shadow = None
        try:
            shadow = self._shadow_copy(excel_path)
            # Primary path: pandas + openpyxl
            try:
                return pd.read_excel(shadow, sheet_name=None, engine="openpyxl")
            except Exception as e1:
                # Fallback: openpyxl direct (sometimes succeeds where pandas+io stack fails)
                if openpyxl is None:
                    raise e1
                try:
                    wb = openpyxl.load_workbook(shadow, read_only=True, data_only=True)
                    out = {}
                    for ws in wb.worksheets:
                        rows = list(ws.iter_rows(values_only=True))
                        if not rows:
                            out[ws.title] = pd.DataFrame()
                            continue
                        header = [str(c) if c is not None else "" for c in rows[0]]
                        data = rows[1:] if len(rows) > 1 else []
                        out[ws.title] = pd.DataFrame(data, columns=header)
                    return out
                except Exception as e2:
                    raise e2
        finally:
            if shadow and os.path.exists(shadow):
                try: os.remove(shadow)
                except Exception: pass

    def _safe_write_xl_dict(self, excel_path: str, sheets: dict):
        """Atomic write: temp file then os.replace()."""
        d = os.path.dirname(excel_path) or "."
        fd, tmp = tempfile.mkstemp(prefix=".tmp_", suffix=".xlsx", dir=d)
        os.close(fd)
        try:
            with pd.ExcelWriter(tmp, engine="openpyxl") as w:
                for name, df in sheets.items():
                    pd.DataFrame(df).to_excel(w, sheet_name=name, index=False)
            os.replace(tmp, excel_path)
        except Exception:
            try: os.remove(tmp)
            except Exception: pass
            raise

    def _scan_and_mark(self, excel_path: str, wall: str, typ: str) -> bool:
        target = _normalize_wall_token(wall)

        with self._io_lock:  # prevent concurrent read/write
            # --- READ robustly ---
            try:
                xl = self._safe_read_xl_dict(excel_path)
            except Exception as e:
                rospy.logerr(f"[listener] Failed to open Excel '{excel_path}': {e}")
                return False

            chosen_sheet = _resolve_sheet_name(xl, typ)
            sheets_to_search = [chosen_sheet] if chosen_sheet else list(xl.keys())

            changed = False
            out = dict(xl)  # start with original frames

            for sheet_name in sheets_to_search:
                df = xl.get(sheet_name)
                if df is None or not isinstance(df, pd.DataFrame):
                    continue
                # Normalize columns if needed (openpyxl fallback may give non-string headers)
                df.columns = [str(c).strip() for c in df.columns]

                if "Wall Number" not in df.columns or "Status" not in df.columns:
                    continue

                tokens = df["Wall Number"].apply(_normalize_wall_token)
                mask = (tokens == target)
                if mask.any():
                    df.loc[mask, "Status"] = "done"
                    out[sheet_name] = df
                    changed = True

            if not changed:
                try:
                    samples = []
                    for s in sheets_to_search:
                        d = xl.get(s)
                        if isinstance(d, pd.DataFrame) and "Wall Number" in d.columns:
                            toks = d["Wall Number"].dropna().map(_normalize_wall_token).unique().tolist()
                            samples.append(f"{s}: {toks[:8]}")
                    rospy.loginfo(f"[listener] No match for wall {wall!r}. "
                                  f"Searched={sheets_to_search}. Examples -> {', '.join(samples)}")
                except Exception:
                    pass
                return False

            # --- WRITE atomically ---
            try:
                self._safe_write_xl_dict(excel_path, out)
                rospy.loginfo(f"[listener] Marked wall {wall!r} as done in '{excel_path}' "
                              f"(sheets searched={sheets_to_search})")
                return True
            except Exception as e:
                rospy.logerr(f"[listener] Excel write failed: {e}")
                return False

    def _retry_pending(self, _evt):
        """Timer callback to retry a deferred selection."""
        if not self.pending:
            if self.retry_timer:
                self.retry_timer.shutdown()
                self.retry_timer = None
            return

        wall, typ = self.pending
        excel = self._get_excel_path()
        if not excel:
            # keep waiting
            return

        if self._scan_and_mark(excel, wall, typ):
            self.ui_wall_done_pub.publish(String(data=str(wall)))
        self.pending = None
        if self.retry_timer:
            self.retry_timer.shutdown()
            self.retry_timer = None

    def _process_selection(self, wall: str, typ: str):
        excel = self._get_excel_path()
        if not excel:
            rospy.logwarn(f"[listener] No Excel path yet; deferring selection wall={wall!r}, typ={typ!r}")
            self.pending = (wall, typ)
            if not self.retry_timer:
                # retry every 0.5s until excel path appears (via param or file_cb)
                self.retry_timer = rospy.Timer(rospy.Duration(0.5), self._retry_pending)
            return

        if self._scan_and_mark(excel, wall, typ):
            self.ui_wall_done_pub.publish(String(data=str(wall)))

    # ---------- callbacks ----------
    def file_cb(self, msg: FileExtractionMessage):
        self.latest_excel = msg.excelfile
        rospy.set_param("/excel_path", self.latest_excel)  # mirror to param for robustness
        rospy.loginfo(f"[listener] Received Excel path: {self.latest_excel!r}")
        # If something was waiting, process now
        if self.pending:
            wall, typ = self.pending
            self._process_selection(wall, typ)

    def selection_cb(self, msg: SelectionWall):
        wall = str(msg.wallselection)          # may be '1', '6', 'F'
        typ  = str(msg.typeselection or "")    # may be 'Stage 2', 'Stage 3', or '1' (non-sheet)
        self.ui_wall_started_pub.publish(String(data=wall))
        excel = self._get_excel_path()
        if not excel:
            rospy.logwarn(f"[listener] No Excel path yet; deferring selection wall={wall!r}, typ={typ!r}")
            self.pending = (wall, typ)
            if not self.retry_timer:
                self.retry_timer = rospy.Timer(rospy.Duration(0.5), self._retry_pending)
            return
        if self._scan_and_mark(excel, wall, typ):
            self.ui_wall_done_pub.publish(String(data=str(wall)))
            self.done_walls.add(wall)

            if self.expected_walls and self.expected_walls.issubset(self.done_walls):
                rospy.loginfo("[listener] All walls completed, publishing /ui/all_done")
                self.ui_all_done_pub.publish(Bool(data=True))

def main():
    ListenerNode()
    rospy.spin()

if __name__ == "__main__":
    main()
