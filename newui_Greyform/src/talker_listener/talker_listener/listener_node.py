#!/usr/bin/env python3
import rospy, pandas as pd 
from std_msgs.msg import String, Bool
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall
import re, time
from pathlib import Path
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
    s = str(v).strip().upper()
    m = re.search(r'(\d+)', s)
    if m:
        return m.group(1)               # just the digits
    if s in {"F", "FL", "FLOOR", "FLOOR/SLAB"}:
        return "F"
    return s

def _resolve_sheet_name(xl_sheets: dict, typeselection: str) -> str:
    if not typeselection:
        return ""
    key = str(typeselection).strip().lower()
    cmap = {name.strip().lower(): name for name in xl_sheets.keys()}
    return cmap.get(key, "")

class ListenerNode:
    def __init__(self):
        rospy.init_node("listener_node", anonymous=True)
        self.latest_excel = None
        self.pending = None
        self.retry_timer = None
        self.expected_walls = set()  
        self.done_walls = set()
        self.__post_init_io()
        self.stored_info = []   
        self.main_store = Path.cwd() 
        rospy.Subscriber(FILE_TOPIC, FileExtractionMessage, self.file_cb, queue_size=10)
        rospy.Subscriber(SEL_TOPIC,  SelectionWall,        self.selection_cb, queue_size=50)
        self.ui_wall_started_pub = rospy.Publisher(UI_STARTED, String, queue_size=10)
        self.ui_wall_done_pub    = rospy.Publisher(UI_DONE,    String, queue_size=10)
        self.ui_all_done_pub     = rospy.Publisher(UI_ALLDONE, Bool,   queue_size=10)

    def _get_excel_path(self):
        if self.latest_excel:
            return self.latest_excel
        p = rospy.get_param("/excel_path", None)
        if p:
            self.latest_excel = p
            rospy.loginfo(f"[listener] Loaded Excel path from param: {p!r}")
            return p
        return None
    
    # helper: MASTER -> DESTINATION (msg.directory) with counter
    def _copy_master_to_directory_with_counter(self, master: Path, dest_dir: Path, preferred_name: str = None) -> Path:
        if not master.exists():
            raise FileNotFoundError(f"Master not found: {master}")
        dest_dir.mkdir(parents=True, exist_ok=True)

        if preferred_name:
            base = Path(preferred_name)
            stem, suffix = base.stem, (base.suffix or master.suffix)
        else:
            stem, suffix = master.stem, master.suffix

        i = 1
        while True:
            candidate = dest_dir / f"{stem}_{i}{suffix}"
            if not candidate.exists():
                shutil.copy2(master, candidate)
                return candidate
            i += 1

    
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
        d = os.path.dirname(src) or "."
        fd, tmp = tempfile.mkstemp(prefix=".shadow_", suffix=".xlsx", dir=d)
        os.close(fd)
        shutil.copy2(src, tmp)
        return tmp

    def _safe_read_xl_dict(self, excel_path: str):
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

    def _initialize_working_copy(self, working_path: str):
        """
        Open the working copy, ensure it's ready for marking:
        - If a sheet has 'Wall Number' but no 'Status', add 'Status' (blank).
        - Optionally add/update a small control sheet with timestamp (harmless).
        Then write back atomically.
        """
        xl = self._safe_read_xl_dict(working_path)
        out = dict(xl)
        changed = False

        for name, df in xl.items():
            if not isinstance(df, pd.DataFrame):
                continue
            # Normalize headers
            df.columns = [str(c).strip() for c in df.columns]
            if "Wall Number" in df.columns and "Status" not in df.columns:
                df = df.copy()
                df["Status"] = ""            # prepopulate empty status
                out[name] = df
                changed = True

        # Optional: add/update a lightweight control sheet
        ctrl_name = "_Control"
        ctrl_df = pd.DataFrame({
            "Key": ["InitializedAt", "Source"],
            "Value": [time.strftime("%Y-%m-%d %H:%M:%S"), "listener_node:file_cb:init"]
        })
        if out.get(ctrl_name) is None or not ctrl_df.equals(out.get(ctrl_name)):
            out[ctrl_name] = ctrl_df
            changed = True

        if changed:
            self._safe_write_xl_dict(working_path, out)

    def _resolve_master_by_name(self, name: str) -> Path:
        """Find master by filename within main_store (or treat absolute paths directly)."""
        p = Path(name)
        if p.is_absolute():
            return p.resolve()
        return (self.main_store / p.name).resolve()

    def _scan_and_mark(self, wall: str, typ: str) -> bool:
        excel_path = self._get_excel_path()
        if not excel_path:
            rospy.logwarn(f"[listener] No working Excel for scan_and_mark(wall={wall!r}, typ={typ!r})")
            return False

        target = _normalize_wall_token(wall)
        with self._io_lock:
            try:
                xl = self._safe_read_xl_dict(excel_path)  # read working copy
            except Exception as e:
                rospy.logerr(f"[listener] Failed to open working Excel '{excel_path}': {e}")
                return False

            chosen_sheet = _resolve_sheet_name(xl, typ)
            sheets_to_search = [chosen_sheet] if chosen_sheet else list(xl.keys())
            changed, out = False, dict(xl)

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
                # (optional) sample logging omitted for brevity
                return False

            try:
                self._write_working_xl(out)  # <- ALWAYS write to working copy
                rospy.loginfo(f"[listener] Marked wall {wall!r} as done in working copy '{excel_path}' "
                            f"(sheets searched={sheets_to_search})")
                return True
            except Exception as e:
                rospy.logerr(f"[listener] Excel write failed: {e}")
                return False

    def _safe_write_xl_dict(self, excel_path: str, sheets: dict):
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
        
    def _retry_pending(self, _evt):
        if not self.pending:
            if self.retry_timer:
                self.retry_timer.shutdown(); self.retry_timer = None
            return
        wall, typ = self.pending
        if self._scan_and_mark(wall, typ):
            self.ui_wall_done_pub.publish(String(data=str(wall)))
        self.pending = None
        if self.retry_timer:
            self.retry_timer.shutdown(); self.retry_timer = None

    def _process_selection(self, wall: str, typ: str):
        if not self._get_excel_path():
            rospy.logwarn(f"[listener] No working Excel yet; deferring wall={wall!r}, typ={typ!r}")
            self.pending = (wall, typ)
            if not self.retry_timer:
                self.retry_timer = rospy.Timer(rospy.Duration(0.5), self._retry_pending)
            return
        if self._scan_and_mark(wall, typ):
            self.ui_wall_done_pub.publish(String(data=str(wall)))

    def _copy_to_dir_with_counter(self, src: Path, dest_dir: Path) -> Path:
        """Copy src into dest_dir as <stem>_1<suffix>, <stem>_2<suffix>, … (no overwrite)."""
        if not src.exists():
            raise FileNotFoundError(f"Master not found: {src}")
        dest_dir.mkdir(parents=True, exist_ok=True)
        stem, suffix = src.stem, (src.suffix or ".xlsx")
        i = 1
        while True:
            candidate = dest_dir / f"{stem}_{i}{suffix}"
            if not candidate.exists():
                shutil.copy2(src, candidate)
                return candidate
            i += 1

    def file_cb(self, msg: FileExtractionMessage):
        dest_dir = Path(os.path.expanduser(msg.directory)).resolve()
        master   = self._resolve_master_by_name(msg.excelfile)

        self.original_excel_file = str(master)
        rospy.loginfo(f"[listener] Master: {self.original_excel_file}")
        rospy.loginfo(f"[listener] Dest dir: {str(dest_dir)!r}")

        try:
            # 1) Copy master -> working (countered) inside msg.directory
            working = self._copy_to_dir_with_counter(master, dest_dir)

            # 2) Immediately open & WRITE the working copy to prep it
            self._initialize_working_copy(str(working))

            # 3) Publish the working copy as the only source-of-truth
            self.excel_file = str(working)
            rospy.set_param("/excel_path", self.excel_file)
            rospy.loginfo(f"[listener] Working copy ready & initialized: {self.excel_file}")

        except Exception as e:
            rospy.logerr(f"[listener] Failed to prepare working copy: {e}")
            # Fallback: use master so pipeline can proceed (not ideal)
            self.excel_file = str(master)
            rospy.set_param("/excel_path", self.excel_file)
            return

        # Handle any deferred selections (they will now write to working copy)
        if self.pending:
            wall, typ = self.pending
            try:
                self._process_selection(wall, typ)
            except Exception as e:
                rospy.logerr(f"[listener] _process_selection(pending) failed: {e}")
            finally:
                self.pending = None

        for idx, item in enumerate(list(self.stored_info), start=1):
            try:
                wall, typ = item
                rospy.loginfo(f"[listener] Processing stored #{idx}: wall={wall}, typ={typ}")
                self._process_selection(wall, typ)
            except Exception as e:
                rospy.logerr(f"[listener] _process_selection(stored #{idx}) failed: {e}")
        self.stored_info.clear()

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
