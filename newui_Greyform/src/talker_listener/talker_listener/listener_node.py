#!/usr/bin/env python3
# add at top of file
import io, os, traceback, time, zipfile, tempfile, contextlib, re
from pathlib import Path
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall
from my_robot_wallinterfaces.srv import SetLed
import pandas as pd
import numpy as np
import rospy
from contextlib import contextmanager
from collections import deque

MAGIC_XLSX = b"PK\x03\x04"  # zip header
MAGIC_OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # legacy .xls (OLE)
ONE_ROW_PER_SELECTION = True  # ← choose exactly one row across workbook
TOL_STRICT = 2.0  # mm
TOL_RELAX = 15.0  # mm
ALWAYS_FORCE_ASSIGN = True  # force if still no match
ONLY_FORCE_ON_SAME_WALL = True  # prefer/require same wall when forcing
PREFER_BLANK = True  # prefer Status != "done"
WRITE_AUDIT = False
AUDIT_COL = None
KEEP_FIRST_UNNAMED = True  # keep "Unnamed: 0" only


def _distance_l1(a, b):
    return float(np.abs(a - b).sum())


def _choose_best_idx(df, idxs, target, prefer_blank=True):
    sub = df.loc[idxs, ["Position X", "Position Y", "Position Z"]].to_numpy(dtype=float)
    d = np.abs(sub - target).sum(axis=1)
    if prefer_blank and "Status" in df.columns:
        blanks = df.loc[idxs, "Status"].astype(str).str.lower() != "done"
        d = d + (~blanks).to_numpy(dtype=float) * 1e-6
    return idxs[int(np.argmin(d))]


def _read_first_bytes(path, n=8):
    try:
        with open(path, "rb") as f:
            return f.read(n)
    except Exception:
        return b""


def _wait_for_valid_xlsx(path, timeout=10.0, interval=0.25):
    end = time.time() + timeout
    last = None
    ok_count = 0
    while time.time() < end:
        try:
            st = os.stat(path)
        except FileNotFoundError:
            time.sleep(interval)
            continue
        sig = (st.st_size, getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
        if sig == last and zipfile.is_zipfile(path):
            ok_count += 1
            if ok_count >= 2:
                return True
        else:
            ok_count = 0
        last = sig
        time.sleep(interval)
    return False


@contextmanager
def _file_lock(path, timeout=3.0, poll=0.02, stale=2.0):
    lock = f"{path}.lock"
    start = time.time()
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            os.close(fd)
            break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock) > stale:
                    os.unlink(lock)
                    rospy.logwarn(f"[listener] Stale lock removed: {lock}")
                    continue
            except FileNotFoundError:
                continue
            if time.time() - start > timeout:
                raise
            time.sleep(poll)
    try:
        yield
    finally:
        try:
            os.unlink(lock)
        except FileNotFoundError:
            pass


def _atomic_write_excel(path, sheets_dict, retries=3, backoff=0.05):
    for attempt in range(retries):
        try:
            with _file_lock(path):
                dname = os.path.dirname(path) or "."
                with tempfile.NamedTemporaryFile(
                    dir=dname, suffix=".xlsx", delete=False
                ) as tmp:
                    tmp_path = tmp.name
                try:
                    with pd.ExcelWriter(tmp_path, engine="openpyxl") as xw:
                        for name, df in sheets_dict.items():
                            df.to_excel(xw, sheet_name=name, index=False)
                    os.replace(tmp_path, path)  # atomic on same filesystem
                finally:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
            return
        except FileExistsError as e:
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (2**attempt))


def _looks_like_csv(path):
    try:
        with open(path, "rb") as f:
            head = f.read(2048)
        if b"\x00" in head:
            return False
        text = head.decode("utf-8", errors="ignore")
        return ("," in text or "\t" in text) and ("\n" in text or "\r" in text)
    except Exception:
        return False


def _load_spreadsheet_dict(path: str):
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    size = p.stat().st_size
    magic = _read_first_bytes(p, 8)
    suffix = p.suffix.lower()
    rospy.logwarn(
        f"[listener] File probe:\n"
        f"  path: {p}\n"
        f"  size: {size} bytes\n"
        f"  suffix: {suffix}\n"
        f"  magic: {magic!r}"
    )
    is_xlsx_magic = magic.startswith(MAGIC_XLSX)
    is_ole_magic = magic.startswith(MAGIC_OLE)
    is_xlsb_ext = suffix == ".xlsb"
    is_csv_ext = suffix == ".csv"
    if is_xlsx_magic or suffix == ".xlsx":
        try:
            return pd.read_excel(p, sheet_name=None, engine="openpyxl")
        except Exception as e1:
            if "File is not a zip file" in str(e1):
                raise ValueError(
                    "The file has .xlsx extension but is not a valid XLSX (zip). "
                    "It might be an .xls, .csv, or a corrupted file."
                )
            try:
                return pd.read_excel(p, sheet_name=None)
            except Exception as e2:
                raise RuntimeError(
                    f"Failed to read XLSX with openpyxl and default engine: {e1} / {e2}"
                )
    if is_ole_magic or suffix == ".xls":
        try:
            return pd.read_excel(p, sheet_name=None, engine="xlrd")
        except Exception as e:
            raise RuntimeError(
                "Failed to read legacy .xls. Ensure xlrd<2.0 is installed:\n"
                "  pip install 'xlrd<2.0'\n"
                f"Underlying error: {type(e).__name__}: {e}"
            )
    if is_xlsb_ext:
        try:
            return pd.read_excel(p, sheet_name=None, engine="pyxlsb")
        except Exception as e:
            raise RuntimeError(
                "Failed to read .xlsb. Install pyxlsb:\n"
                "  pip install pyxlsb\n"
                f"Underlying error: {type(e).__name__}: {e}"
            )
    if is_csv_ext or _looks_like_csv(p):
        try:
            df = pd.read_csv(p)
            return {"Sheet1": df}
        except Exception as e:
            raise RuntimeError(
                f"Detected CSV but failed to read: {type(e).__name__}: {e}"
            )
    try:
        return pd.read_excel(p, sheet_name=None)
    except Exception as e:
        raise RuntimeError(
            "Could not determine spreadsheet format. "
            "If it's actually a CSV, rename to .csv. "
            "If it's .xls, install xlrd<2.0 and keep .xls extension. "
            f"Last error: {type(e).__name__}: {e}"
        )


def _wait_for_stable_file(path, timeout=8.0, interval=0.25):
    end = time.time() + timeout
    last = None
    while time.time() < end:
        try:
            st = os.stat(path)
            sig = (st.st_size, getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
        except FileNotFoundError:
            time.sleep(interval)
            continue
        if sig == last:
            return True
        last = sig
        time.sleep(interval)
    return False


class ListenerNode:
    def __init__(self):
        # state
        self._excel_path = None  # str path to the Excel
        self._excel_sheets = None  # dict of DataFrames
        self._excel_ready = False
        self._selection_ready = False
        self._in_progress = False
        self._journal = []
        self._ts_excel_loaded = 0.0
        self._ts_selection = 0.0
        self.wallselection = None  # str
        self.typeselection = None  # numeric or None
        self.picked_position = None  # [LX, LY, LZ] (floats)
        self._last_excel_sig = None
        self._recent = {}  # key -> expires_at
        self._consumed = set()
        self._recent_ttl = 3.0  # seconds
        rospy.Subscriber(
            "file_extraction_topic",
            FileExtractionMessage,
            self.file_listener_callback,
            queue_size=10,
        )
        rospy.Subscriber(
            "selection_wall_topic",
            SelectionWall,
            self.selection_listener_callback,
            queue_size=10,
        )

    def file_listener_callback(self, msg: FileExtractionMessage):
        raw = msg.excelfile or ""
        self._excel_path = str(Path(raw).expanduser().resolve())
        try:
            st = os.stat(self._excel_path)
            sig = (st.st_size, getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
        except FileNotFoundError:
            sig = None
        if sig is not None and sig == self._last_excel_sig and self._excel_ready:
            rospy.loginfo(
                "[listener] Excel unchanged; ignoring duplicate file message."
            )
            self._maybe_process()
            return
        if not _wait_for_valid_xlsx(self._excel_path):
            rospy.logwarn(
                "[listener] Excel not stable/valid yet; will read on next change."
            )
            return
        self._excel_sheets = _load_spreadsheet_dict(self._excel_path)
        self._excel_ready = True
        self._ts_excel_loaded = time.time()
        self._last_excel_sig = sig
        rospy.loginfo(
            f"[listener] Excel loaded: {self._excel_path} (sheets: {list(self._excel_sheets.keys())})"
        )
        self._maybe_process()

    def selection_listener_callback(self, msg: SelectionWall):
        self._ts_selection = time.time()
        self._journal.append(
            (
                str(msg.wallselection),
                str(msg.typeselection),
                list(msg.picked_position)[:3],
            )
        )
        self._selection_ready = True
        self.wallselection = msg.wallselection
        self.typeselection = msg.typeselection
        self.picked_position = msg.picked_position
        key = f"{self.wallselection}|{self.typeselection}|{tuple(map(float, self.picked_position[:3]))}"
        if key in self._consumed:
            rospy.loginfo("[listener] Selection already consumed; skipping.")
            return
        self._maybe_process()

    def sweep_stage2_blanks_from_recent(self, recent_positions, l1_tol):
        if self._excel_sheets is None or not recent_positions:
            return 0
        df0 = self._excel_sheets.get("Stage 2")
        df = self._numeric_cols(df0)
        if df is None or df.empty:
            return 0
        changed = 0
        for idx, row in df[df["Status"] != "done"].iterrows():
            wx = (
                str(row.get("Wall Number", "")) if "Wall Number" in df.columns else None
            )
            lx, ly, lz = float(row["Position X"]), float(row["Position Y"]), float(row["Position Z"])
            for w, _mt, (px, py, pz) in recent_positions:
                if wx and w != wx:
                    continue
                if abs(lx - px) + abs(ly - py) + abs(lz - pz) <= l1_tol:
                    df.at[idx, "Status"] = "done"
                    if WRITE_AUDIT and AUDIT_COL:  # guard everything
                        if AUDIT_COL not in df.columns:
                            df[AUDIT_COL] = ""
                        df.at[idx, AUDIT_COL] = audit_value
                    df.at[idx, AUDIT_COL] = f"{w}|{_mt}|[{px},{py},{pz}]"
                    changed += 1
                    break
        if changed:
            self._excel_sheets["Stage 2"] = df
            _atomic_write_excel(self._excel_path, self._excel_sheets)
            rospy.loginfo(f"[listener] Excel updated (Stage 2 sweep: {changed})")
        return changed

    def sweep_stage2_blanks_from_journal(self):
        if self._excel_sheets is None or not self._journal:
            return 0
        df0 = self._excel_sheets.get("Stage 2")
        df = self._numeric_cols(df0)
        if df is None or df.empty:
            return 0
        changed = 0
        for idx, row in df[df["Status"].astype(str).str.lower() != "done"].iterrows():
            wx = (
                str(row.get("Wall Number", "")) if "Wall Number" in df.columns else None
            )
            lx, ly, lz = float(row["Position X"]), float(row["Position Y"]), float(row["Position Z"])
            for w, mt, pos in self._journal:
                if wx is not None and w != wx:
                    continue
                if (
                    abs(lx - pos[0]) + abs(ly - pos[1]) + abs(lz - pos[2])
                ) <= TOL_RELAX * 3:
                    df.at[idx, "Status"] = "done"
                    if WRITE_AUDIT and AUDIT_COL:  # guard everything
                        if AUDIT_COL not in df.columns:
                            df[AUDIT_COL] = ""
                        df.at[idx, AUDIT_COL] = audit_value
                    df.at[idx, AUDIT_COL] = f"{w}|{mt}|{pos}"
                    changed += 1
                    break
        if changed:
            self._excel_sheets["Stage 2"] = df
        return changed

    def _maybe_process(self):
        if not (self._excel_ready and self._selection_ready) or self._in_progress:
            return
        self._in_progress = True
        try:
            changed_mark = self._mark_selected_row()  # bool
            changed_sweep = self._autofill_status_done() > 0  # int -> bool
            changed_strip = self._strip_admin_cols()  # bool
            if changed_mark or changed_sweep or changed_strip:
                _atomic_write_excel(self._excel_path, self._excel_sheets)
                rospy.loginfo(f"[listener] Excel updated: {self._excel_path}")
        except Exception as e:
            rospy.logerr(f"[listener] Processing error: {e}")
        finally:
            self._in_progress = False

    def _numeric_cols(self, df):
        for c in ("Position X", "Position Y", "Position Z"):
            if c not in df.columns:
                return None
        df = df.copy()
        for c in ("Position X", "Position Y", "Position Z", "Wall Number", "Marking Type", "Status"):
            if c in df.columns:
                df[c] = df[c].apply(lambda x: x.strip() if isinstance(x, str) else x)
        df["Position X"] = pd.to_numeric(df["Position X"], errors="coerce")
        df["Position Y"] = pd.to_numeric(df["Position Y"], errors="coerce")
        df["Position Z"] = pd.to_numeric(df["Position Z"], errors="coerce")
        if "Status" not in df.columns:
            df["Status"] = "blank"
        else:
            df["Status"] = df["Status"].fillna("blank").astype(str).str.lower()
            df.loc[~df["Status"].isin(["blank", "done"]), "Status"] = "blank"
        return df

    def _strip_admin_cols(self) -> bool:
        changed_any = False
        for sheet in ("Stage 2", "Stage 3"):
            if sheet not in self._excel_sheets:
                continue
            df = self._excel_sheets[sheet]
            before_cols = list(df.columns)
            audit_cols = ["LastUpdatedBy"]
            if "AUDIT_COL" in globals() and globals()["AUDIT_COL"]:
                audit_cols.append(globals()["AUDIT_COL"])
            df = df.drop(
                columns=[c for c in audit_cols if c in df.columns], errors="ignore"
            )
            df = df.drop(
                columns=[
                    c for c in list(df.columns) if (c is None) or (str(c).strip() == "")
                ],
                errors="ignore",
            )
            keep, first_unnamed = [], False
            for c in df.columns:
                if str(c).startswith("Unnamed"):
                    if KEEP_FIRST_UNNAMED and not first_unnamed and c == "Unnamed: 0":
                        keep.append(c)
                        first_unnamed = True
                else:
                    keep.append(c)
            df = df[keep]
            drop_empty = [
                c
                for c in df.columns
                if str(c).startswith("Unnamed")
                and c != "Unnamed: 0"
                and df[c].isna().all()
            ]
            if drop_empty:
                df = df.drop(columns=drop_empty, errors="ignore")
            self._excel_sheets[sheet] = df
            if list(df.columns) != before_cols:
                changed_any = True
        return changed_any

    def _sstr(self, df, col):
        if col in df.columns:
            return df[col].astype(str).str.lower()
        return pd.Series([""] * len(df), index=df.index)

    def _autofill_status_done(self, sheets=("Stage 2", "Stage 3")) -> int:
        changed_total = 0
        for sheet in sheets:
            if sheet not in self._excel_sheets:
                continue
            df = self._numeric_cols(self._excel_sheets[sheet])
            if df is None or df.empty:
                continue
            if "Status" not in df.columns:
                df["Status"] = "blank"
            status_str = df["Status"].astype(str).str.strip().str.lower()
            typ = self._sstr(df, "Type")
            name = self._sstr(df, "Name")
            is_wall = typ.str.contains(r"\bwall\b", na=False) | name.str.contains(
                r"\bbasic wall\b", na=False
            )
            is_center = typ.str.contains(
                r"center\s*point", na=False
            ) | name.str.contains(r"\bcp\d*\b", na=False)
            candidates = ~(is_wall | is_center)
            not_done = ~status_str.eq("done")
            to_fill = candidates & not_done
            n = int(to_fill.sum())
            if n:
                df.loc[to_fill, "Status"] = "done"
                changed_total += n
            self._excel_sheets[sheet] = df
        return changed_total

    def _strip_audit(self, _df):
        drop = [
            c
            for c in _df.columns
            if str(c).strip().lower() in ("lastupdatedby", "last updated by")
            or str(c).strip().lower().startswith("unnamed:")
        ]
        if drop:
            _df.drop(columns=list(set(drop)), inplace=True, errors="ignore")
        self._strip_audit(_df)
        self._strip_audit(_df)
        self._excel_sheets["Stage 2"] = _df
        self._excel_sheets["Stage 3"] = _df
        return True

    def _nearest_index(self, df, posX, posY, posZ, wall_str):
        pts = df[["Position X", "Position Y", "Position Z"]].to_numpy(dtype=float)
        target = np.array([posX, posY, posZ], dtype=float)
        d = np.abs(pts - target).sum(axis=1)  # L1 is robust for grid snaps
        cand = pd.Series(d, index=df.index)
        if "Wall Number" in df.columns and wall_str is not None:
            same_wall = df["Wall Number"].astype(str) == wall_str
            if same_wall.any():
                cand = cand[same_wall]
        if PREFER_BLANK and "Status" in df.columns:
            blanks = df.loc[cand.index, "Status"].astype(str).str.lower() != "done"
            if blanks.any():
                cand = cand[blanks]
        if cand.empty:
            return None, np.inf
        idx = cand.idxmin()
        return int(idx), float(cand.loc[idx])

    def _closest_index(self, df, idx_list, posX, posY, posZ):
        sub = df.loc[idx_list, ["Position X", "Position Y", "Position Z"]].to_numpy(dtype=float)
        target = np.array([posX, posY, posZ], float)
        d = np.abs(sub - target).sum(axis=1)

        return idx_list[np.argmin(d)]

    def _mark_selected_row(self) -> bool:
        if self._excel_sheets is None or self.picked_position is None:
            return False
        posX, posY, posZ = map(float, self.picked_position)
        pos = np.array([posX, posY, posZ], dtype=float)
        wall_str = self.wallselection
        mtype = self.typeselection
        best = None
        for sheet, df0 in self._excel_sheets.items():
            df = self._numeric_cols(df0)
            if df is None or df.empty:
                continue
            strict = self._match_mask(
                df, posX, posY, posZ, wall_str, mtype, TOL_STRICT, enforce_wall=True
            )
            if strict.any():
                cand_idx = df.index[strict]
                idx = self._closest_index(df, cand_idx, posX, posY, posZ)
                l1 = float(
                    np.abs(
                        df.loc[idx, ["Position X", "Position Y", "Position Z"]].to_numpy(dtype=float) - pos
                    ).sum()
                )
                if best is None or l1 < best[1]:
                    best = ("matched", l1, sheet, idx)
        if best is None:
            for sheet, df0 in self._excel_sheets.items():
                df = self._numeric_cols(df0)
                if df is None or df.empty:
                    continue
                relaxed = self._match_mask(
                    df, posX, posY, posZ, wall_str, mtype, TOL_RELAX, enforce_wall=False
                )
                if relaxed.any():
                    cand_idx = df.index[relaxed]
                    idx = self._closest_index(df, cand_idx, posX, posY, posZ)
                    l1 = float(
                        np.abs(
                            df.loc[idx, ["Position X", "Position Y", "Position Z"]].to_numpy(dtype=float) - pos
                        ).sum()
                    )
                    if best is None or l1 < best[1]:
                        best = ("relaxed", l1, sheet, idx)
        if best is None and ALWAYS_FORCE_ASSIGN:
            for sheet, df0 in self._excel_sheets.items():
                df = self._numeric_cols(df0)
                if df is None or df.empty:
                    continue
                pool = df.index
                if (
                    ONLY_FORCE_ON_SAME_WALL
                    and "Wall Number" in df.columns
                    and wall_str is not None
                ):
                    same_wall = df["Wall Number"].astype(str) == wall_str
                    # enforce: if no same-wall rows, skip this sheet
                    if not same_wall.any():
                        continue
                    pool = df.index[same_wall]
                if PREFER_BLANK and "Status" in df.columns:
                    blanks_mask = (
                        df.loc[pool, "Status"].astype(str).str.lower() != "done"
                    )
                    if blanks_mask.any():
                        pool = df.loc[pool[blanks_mask], :].index
                if len(pool) == 0:
                    continue
                idx = self._closest_index(df, pool, posX, posY, posZ)
                l1 = float(
                    np.abs(
                        df.loc[idx, ["Position X", "Position Y", "Position Z"]].to_numpy(dtype=float) - pos
                    ).sum()
                )
                if best is None or l1 < best[1]:
                    best = ("forced", l1, sheet, idx)
        if best is None:
            rospy.logwarn("[listener] No candidates in any sheet (unexpected).")
            return False
        tag, dist, sheet, idx = best
        df = self._excel_sheets[sheet]
        if "Status" not in df.columns:
            df["Status"] = "blank"
        changed = False
        if str(df.at[idx, "Status"]).lower() != "done":
            df.at[idx, "Status"] = "done"
            changed = True
        if WRITE_AUDIT and AUDIT_COL:  # guard everything
            if AUDIT_COL not in df.columns:
                df[AUDIT_COL] = ""
            df.at[idx, AUDIT_COL] = audit_value
        self._excel_sheets[sheet] = df
        if AUDIT_COL not in df.columns:
            df[AUDIT_COL] = ""
        audit_value = (
            f"{self.wallselection}|{self.typeselection}|{self.picked_position}"
        )
        if WRITE_AUDIT and AUDIT_COL:
            if AUDIT_COL not in df.columns:
                df[AUDIT_COL] = ""
            if (
                str(df.at[idx, "Status"]).lower() == "done"
                and str(df.at[idx, AUDIT_COL]) == audit_value
            ):
                rospy.loginfo(
                    f"[listener] Row already done by same selection → {sheet}[{str(idx)}]; no write."
                )
                return False
        df.at[idx, "Status"] = "done"
        if WRITE_AUDIT and AUDIT_COL:
            df.at[idx, AUDIT_COL] = audit_value
        changed = True
        rospy.loginfo(
            f"[listener] {tag} 1 row → {sheet}[{str(idx)}] (L1={dist:.1f} mm)"
        )
        return changed

    def _match_mask(
        self, df, posX, posY, posZ, wall_str, mtype, tol, enforce_wall=True
    ):
        mask = (
            (df["Position X"].sub(posX).abs() <= tol)
            & (df["Position Y"].sub(posY).abs() <= tol)
            & (df["Position Z"].sub(posZ).abs() <= tol)
        )
        if enforce_wall and "Wall Number" in df.columns and wall_str is not None:
            mask &= df["Wall Number"].astype(str) == wall_str
        if "Marking Type" in df.columns and self._is_number(mtype):
            mt = pd.to_numeric(df["Marking Type"], errors="coerce")
            mask &= (mt == float(mtype)) | (mt.isna())
        return mask

    def _is_number(self, x):
        try:
            float(x)
            return True
        except Exception:
            return False

    @staticmethod
    def _safe_to_number(x):
        try:
            return float(x)
        except Exception:
            return np.nan


def main():
    rospy.init_node("listener_node", anonymous=True)
    ListenerNode()
    rospy.loginfo("[listener] Node started, waiting for messages...")
    rospy.spin()


if __name__ == "__main__":
    main()
