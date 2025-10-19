#!/usr/bin/env python3
"""
Listener node that receives file-extraction and selection messages and updates Excel sheets.

- Subscribes to:
  - /file_extraction_topic : FileExtractionMessage  (updates latest Excel path param)
  - /selection_wall_topic  : SelectionWall         (requests marking a wall as 'done')

- Publishes UI status on:
  - /ui/wall_started
  - /ui/wall_done
  - /ui/all_done

The node safely reads/writes the Excel (.xlsx) using a shadow copy and retries to
handle transient file I/O issues. It normalizes wall tokens and can search across
multiple sheets in the workbook.
"""
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
    Normalize a wall identifier into a canonical token used for matching.

    Rules applied:
    - Convert to string, strip whitespace, uppercase.
    - If digits are present, return only the digits (first match).
    - Map certain floor-like names ("F", "FL", "FLOOR", "FLOOR/SLAB") to "F".
    - Otherwise return the cleaned string.

    Parameters:
    - v: any object representing the wall token.

    Returns:
    - str: normalized token suitable for comparison/matching.
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
    Resolve a typeselection value to an exact sheet name from the loaded Excel dict.

    Parameters:
    - xl_sheets: dict mapping sheet names to DataFrames (as returned by pandas.read_excel(..., sheet_name=None))
    - typeselection: user-provided typeselection string which is matched case-insensitively
                     against available sheet names.

    Returns:
    - str: the exact sheet name if found (matching lowercased key), otherwise empty string.
    """
    if not typeselection:
        return ""
    key = str(typeselection).strip().lower()
    cmap = {name.strip().lower(): name for name in xl_sheets.keys()}
    return cmap.get(key, "")

class ListenerNode:
    def __init__(self):
        """
        Initialize the ListenerNode.

        Responsibilities:
        - Initialize a rospy node (listener_node).
        - Initialize state variables used for pending selections, retry timers,
          and tracking expected/done walls.
        - Create subscribers for FILE_TOPIC and SEL_TOPIC and UI publishers.

        Behavior:
        - The listener maintains self.latest_excel which is the path to the current
          Excel workbook (either from an incoming FileExtractionMessage or the
          /excel_path parameter).
        - On receiving a SelectionWall message it will attempt to mark the corresponding
          wall row(s) "done" in the workbook (searching across sheets if necessary).
        - If the workbook is not yet available, it defers processing and periodically retries.
        """
        rospy.init_node("listener_node", anonymous=True)
        self.latest_excel = None
        self.pending = None
        self.retry_timer = None
        self.expected_walls = set()  
        self.done_walls = set()
        self.__post_init_io()
        rospy.Subscriber(FILE_TOPIC, FileExtractionMessage, self.file_cb, queue_size=10)
        rospy.Subscriber(SEL_TOPIC,  SelectionWall,        self.selection_cb, queue_size=50)
        self.ui_wall_started_pub = rospy.Publisher(UI_STARTED, String, queue_size=10)
        self.ui_wall_done_pub    = rospy.Publisher(UI_DONE,    String, queue_size=10)
        self.ui_all_done_pub     = rospy.Publisher(UI_ALLDONE, Bool,   queue_size=10)

    def _get_excel_path(self):
        """
        Return the current Excel path to use for reads/writes.

        Priority:
        - If self.latest_excel is set (e.g., from a received FileExtractionMessage), return it.
        - Otherwise check the ROS parameter '/excel_path' and mirror it into self.latest_excel.

        Returns:
        - str or None: the path to the Excel file, or None if not known.
        """
        if self.latest_excel:
            return self.latest_excel
        p = rospy.get_param("/excel_path", None)
        if p:
            self.latest_excel = p
            rospy.loginfo(f"[listener] Loaded Excel path from param: {p!r}")
            return p
        return None
    
    def __post_init_io(self):
        """
        Internal initialization for I/O related parameters and locks.

        Sets:
        - self._io_lock: threading.Lock protecting file read/write/safe operations.
        - self._IO_RETRY_TRIES: number of attempts to check file stability.
        - self._IO_RETRY_SLEEP: sleep seconds between stability checks.
        """
        self._io_lock = threading.Lock()
        self._IO_RETRY_TRIES = 8
        self._IO_RETRY_SLEEP = 0.25

    def _is_valid_zip(self, path: str) -> bool:
        """
        Heuristic check that a .xlsx file is a valid zip archive and of reasonable size.

        Parameters:
        - path: filesystem path to check.

        Returns:
        - bool: True if file exists, size > 1024 and zipfile.is_zipfile returns True; False otherwise.
        """
        try:
            return os.path.getsize(path) > 1024 and zipfile.is_zipfile(path)
        except Exception:
            return False

    def _wait_stable(self, path: str, tries=None, sleep=None) -> bool:
        """
        Wait until the given file path stops changing size (stable), or until tries exhausted.

        This helps avoid reading a file that is still being written.

        Parameters:
        - path: filesystem path to monitor.
        - tries: maximum number of checks (defaults to self._IO_RETRY_TRIES).
        - sleep: seconds between checks (defaults to self._IO_RETRY_SLEEP).

        Returns:
        - bool: True if the file size was stable (>0) across two consecutive checks, False otherwise.
        """
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
        """
        Make a shadow copy of the given file in the same directory and return the temporary path.

        This is used to avoid locking/partial-write problems when reading Excel files.

        Parameters:
        - src: source file path.

        Returns:
        - str: path to the temporary shadow copy.

        Notes:
        - The temporary file is created with prefix ".shadow_" and suffix ".xlsx".
        - The caller is responsible for removing the returned temporary file.
        """
        d = os.path.dirname(src) or "."
        fd, tmp = tempfile.mkstemp(prefix=".shadow_", suffix=".xlsx", dir=d)
        os.close(fd)
        shutil.copy2(src, tmp)
        return tmp

    def _safe_read_xl_dict(self, excel_path: str):
        """
        Safely read an Excel file and return a dict of sheet_name -> DataFrame.

        Strategy:
        - Wait for the file to be stable and check it's a valid zipped .xlsx.
        - Create a shadow copy and attempt to read via pandas.read_excel with openpyxl engine.
        - If pandas.read_excel fails but openpyxl is available, attempt a fallback manual read using openpyxl.

        Parameters:
        - excel_path: path to .xlsx file.

        Returns:
        - dict: mapping sheet name to pandas.DataFrame.

        Raises:
        - IOError or underlying exceptions when reading/parsing fails.
        """
        if not self._wait_stable(excel_path):
            raise IOError("file not stable")
        if not self._is_valid_zip(excel_path):
            raise IOError("not a valid .xlsx zip")
        shadow = None
        try:
            shadow = self._shadow_copy(excel_path)
            try:
                return pd.read_excel(shadow, sheet_name=None, engine="openpyxl")
            except Exception as e1:
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
        """
        Safely write a dictionary of sheets to an Excel file in a crash-safe manner.

        Strategy:
        - Write to a temporary file in the same directory, then atomically replace the target path.

        Parameters:
        - excel_path: destination .xlsx path.
        - sheets: mapping of sheet_name -> tabular data (pandas DataFrame or convertible).

        Raises:
        - Exceptions from pandas/OpenPyXL or os.replace will propagate to caller.
        """
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
        """
        Scan the given Excel workbook and mark rows matching the wall token as 'done'.

        Procedure:
        - Read the workbook via _safe_read_xl_dict (protected by self._io_lock).
        - Resolve typeselection to a specific sheet name if provided; otherwise search all sheets.
        - For each applicable sheet, normalize the "Wall Number" column and set "Status" to "done"
          for rows that match the normalized token.
        - If any sheet was changed, write back the modified workbook using _safe_write_xl_dict.

        Parameters:
        - excel_path: path to the workbook.
        - wall: wall token (stringable) to match (e.g., "1", "F").
        - typ: typeselection string that may designate a sheet to limit the search.

        Returns:
        - bool: True if at least one row was updated and the workbook was written, False otherwise.

        Side effects:
        - Writes to excel_path if modified.
        - Logs info/debug messages about matches and failures.
        """
        target = _normalize_wall_token(wall)
        with self._io_lock:  
            try:
                xl = self._safe_read_xl_dict(excel_path)
            except Exception as e:
                rospy.logerr(f"[listener] Failed to open Excel '{excel_path}': {e}")
                return False
            chosen_sheet = _resolve_sheet_name(xl, typ)
            sheets_to_search = [chosen_sheet] if chosen_sheet else list(xl.keys())
            changed = False
            out = dict(xl)  
            for sheet_name in sheets_to_search:
                df = xl.get(sheet_name)
                if df is None or not isinstance(df, pd.DataFrame):
                    continue
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
            try:
                self._safe_write_xl_dict(excel_path, out)
                rospy.loginfo(f"[listener] Marked wall {wall!r} as done in '{excel_path}' "
                              f"(sheets searched={sheets_to_search})")
                return True
            except Exception as e:
                rospy.logerr(f"[listener] Excel write failed: {e}")
                return False

    def _retry_pending(self, _evt):
        """
        Timer callback that retries processing a previously pending selection.

        Called periodically by rospy.Timer when a selection was deferred because
        an Excel path was not yet available. If processing succeeds, publishes
        ui_wall_done and clears the pending state and timer.

        Parameters:
        - _evt: rospy.TimerEvent passed by rospy.Timer (unused).
        """
        if not self.pending:
            if self.retry_timer:
                self.retry_timer.shutdown()
                self.retry_timer = None
            return
        wall, typ = self.pending
        excel = self._get_excel_path()
        if not excel:
            return
        if self._scan_and_mark(excel, wall, typ):
            self.ui_wall_done_pub.publish(String(data=str(wall)))
        self.pending = None
        if self.retry_timer:
            self.retry_timer.shutdown()
            self.retry_timer = None

    def _process_selection(self, wall: str, typ: str):
        """
        Process a selection request immediately if possible; otherwise defer.

        If no Excel path is available, the selection is stored in self.pending and
        a retry timer is created to periodically attempt processing. If processing
        succeeds, a /ui/wall_done is published.

        Parameters:
        - wall: wall token to process.
        - typ: typeselection string to resolve to sheet name when searching.
        """
        excel = self._get_excel_path()
        if not excel:
            rospy.logwarn(f"[listener] No Excel path yet; deferring selection wall={wall!r}, typ={typ!r}")
            self.pending = (wall, typ)
            if not self.retry_timer:
                self.retry_timer = rospy.Timer(rospy.Duration(0.5), self._retry_pending)
        if self._scan_and_mark(excel, wall, typ):
            self.ui_wall_done_pub.publish(String(data=str(wall)))

    def file_cb(self, msg: FileExtractionMessage):
        """
        Callback for FileExtractionMessage messages.

        Stores the incoming Excel path in self.latest_excel, mirrors it to the ROS
        parameter '/excel_path' for robustness, and attempts processing any pending selection.

        Parameters:
        - msg: FileExtractionMessage with fields 'excelfile' and 'stl_data' (stl_data unused here).
        """
        self.latest_excel = msg.excelfile
        rospy.set_param("/excel_path", self.latest_excel)  # mirror to param for robustness
        rospy.loginfo(f"[listener] Received Excel path: {self.latest_excel!r}")
        if self.pending:
            wall, typ = self.pending
            self._process_selection(wall, typ)

    def selection_cb(self, msg: SelectionWall):
        """
        Callback for SelectionWall messages.

        - Publishes /ui/wall_started immediately.
        - If excel path is missing, defer processing and start the retry timer.
        - Otherwise attempt to mark the matching wall(s) as done and publish /ui/wall_done.
        - Track completed walls and publish /ui/all_done when expected set satisfied.

        Parameters:
        - msg: SelectionWall message with at least wallselection and typeselection fields.
        """
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
    """
    Module entrypoint to start the ListenerNode and enter rospy.spin().
    """
    ListenerNode()
    rospy.spin()

if __name__ == "__main__":
    main()
