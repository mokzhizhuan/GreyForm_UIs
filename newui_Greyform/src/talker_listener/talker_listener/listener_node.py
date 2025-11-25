#!/usr/bin/env python3
import os
import re
import threading
from typing import Dict, Optional

import pandas as pd
import rospy
from pathlib import Path
from std_msgs.msg import String, Bool
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall

FILE_TOPIC = "/file_extraction_topic"
SEL_TOPIC = "/selection_wall_topic"
UI_STARTED = "/ui/wall_started"
UI_DONE = "/ui/wall_done"
UI_ALLDONE = "/ui/all_done"


def _normalize(v):
    s = str(v).strip().upper()
    m = re.search(r"(\d+)", s)
    if m:
        return m.group(1)
    if s in {"F", "FLOOR", "FL"}:
        return "F"
    return s


def _resolve_sheet(xl_sheets: Dict[str, pd.DataFrame], typ: str):
    if not typ:
        return ""
    t = typ.lower().strip()
    mapping = {name.lower(): name for name in xl_sheets.keys()}
    return mapping.get(t, "")


class ListenerNode:
    def __init__(self):
        rospy.init_node("listener_node", anonymous=True)

        self.excel_path: Optional[str] = None

        self._io = threading.Lock()

        self.pending_list = []   # many stored until Excel arrives

        self.ui_start_pub = rospy.Publisher(UI_STARTED, String, queue_size=10)
        self.ui_done_pub = rospy.Publisher(UI_DONE, String, queue_size=10)
        self.ui_all_pub = rospy.Publisher(UI_ALLDONE, Bool, queue_size=10)

        rospy.Subscriber(FILE_TOPIC, FileExtractionMessage, self.file_cb, queue_size=5)
        rospy.Subscriber(SEL_TOPIC, SelectionWall, self.selection_cb, queue_size=50)

        rospy.loginfo("[listener] Started clean listener_node.")

    # ----------------------------------------------------------------------
    # Excel read/write
    # ----------------------------------------------------------------------
    def _read(self):
        return pd.read_excel(self.excel_path, sheet_name=None, engine="openpyxl")

    def _write(self, sheets):
        with pd.ExcelWriter(self.excel_path, engine="openpyxl") as w:
            for name, df in sheets.items():
                pd.DataFrame(df).to_excel(w, sheet_name=name, index=False)

    # ----------------------------------------------------------------------
    # Mark Excel row(s)
    # ----------------------------------------------------------------------
    def _mark(self, wall, typ):
        if not self.excel_path:
            return False

        target = _normalize(wall)

        with self._io:
            try:
                xl = self._read()
            except Exception as e:
                rospy.logerr(f"[listener] XLS read failed: {e}")
                return False

            changed = False
            out = dict(xl)

            sheet_name = _resolve_sheet(xl, typ)
            search_list = [sheet_name] if sheet_name else list(xl.keys())

            for name in search_list:
                df = xl.get(name)
                if df is None:
                    continue
                df = df.copy()
                df.columns = [str(c).strip() for c in df.columns]

                if "Wall Number" not in df.columns:
                    continue

                if "Status" not in df.columns:
                    df["Status"] = ""

                mask = df["Wall Number"].apply(_normalize) == target

                if mask.any():
                    df.loc[mask, "Status"] = "done"
                    out[name] = df
                    changed = True

            if not changed:
                rospy.loginfo(f"[listener] No rows updated for wall={wall}")
                return False

            try:
                self._write(out)
                return True
            except Exception as e:
                rospy.logerr(f"[listener] XLS write failed: {e}")
                return False

    # ----------------------------------------------------------------------
    # ROS Callbacks
    # ----------------------------------------------------------------------
    def file_cb(self, msg: FileExtractionMessage):
        path = msg.excelfile.strip()
        if not os.path.exists(path):
            rospy.logerr(f"[listener] Excel file missing: {path}")
            return

        self.excel_path = path
        rospy.loginfo(f"[listener] Using Excel: {path}")

        # Process all pending
        for wall, typ in list(self.pending_list):
            self._process(wall, typ)
        self.pending_list.clear()

    def _process(self, wall, typ):
        if not self.excel_path:
            rospy.logwarn(f"[listener] No Excel yet; queueing wall={wall} typ={typ}")
            self.pending_list.append((wall, typ))
            return

        ok = self._mark(wall, typ)
        if ok:
            self.ui_done_pub.publish(String(data=str(wall)))

    def selection_cb(self, msg: SelectionWall):
        wall = str(msg.wallselection)
        typ = str(msg.typeselection or "")

        rospy.loginfo(f"[listener] selection_cb: wall={wall}, typ={typ}")

        self.ui_start_pub.publish(String(data=wall))
        self._process(wall, typ)
        rospy.set_param("/ui_last_started_wall", wall)
        rospy.set_param("/ui_last_done_wall", wall)


def main():
    ListenerNode()
    rospy.spin()


if __name__ == "__main__":
    main()
