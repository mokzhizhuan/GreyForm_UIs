import pandas as pd
import numpy as np
from typing import Union, Optional, Dict, Any

def _coerce_to_dataframe(
    src: Union[str, "pd.ExcelFile", pd.DataFrame, Dict[str, pd.DataFrame], Dict, list],
    sheet_name: Optional[Union[str, int, None]] = None,
) -> pd.DataFrame:
    """
    Accepts many input shapes and returns a single DataFrame.
    - DataFrame -> copy
    - Excel path/ExcelFile -> read one sheet (sheet_name) or first sheet if None
    - dict from read_excel(sheet_name=None) -> concat all sheets
    - dict/list of row dicts -> DataFrame
    """
    # Already a DataFrame
    if isinstance(src, pd.DataFrame):
        return src.copy()

    # ExcelFile or path -> parse
    if isinstance(src, (str, pd.ExcelFile)):
        xls = src if isinstance(src, pd.ExcelFile) else pd.ExcelFile(src)
        if sheet_name is None:
            # first sheet by default
            return xls.parse(sheet_name=xls.sheet_names[0])
        elif sheet_name == "all":
            frames = [xls.parse(sn) for sn in xls.sheet_names]
            return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        else:
            return xls.parse(sheet_name=sheet_name)

    # Dict[str, DataFrame] (typical of read_excel(..., sheet_name=None))
    if isinstance(src, dict):
        # Case 1: dict of DataFrames -> concat
        if all(isinstance(v, pd.DataFrame) for v in src.values()):
            return pd.concat(list(src.values()), ignore_index=True) if src else pd.DataFrame()
        # Case 2: dict of rows -> DataFrame
        try:
            return pd.DataFrame.from_records([src])
        except Exception:
            pass

    # List of row dicts
    if isinstance(src, list) and (len(src) == 0 or isinstance(src[0], dict)):
        return pd.DataFrame.from_records(src)

    raise TypeError(f"Unsupported input type for DataFrame: {type(src)}")


def exceldataextractor(
    output_excel: Union[str, "pd.ExcelFile", pd.DataFrame, Dict[str, pd.DataFrame], Dict, list],
    sheet_name: Optional[Union[str, int, None]] = None,  # None=first sheet, "all"=concat all
) -> Dict[str, Any]:
    # 1) Load df_combined_all robustly
    df_combined_all = _coerce_to_dataframe(output_excel, sheet_name=sheet_name)

    # 2) Your original pipeline (with tiny fixes)
    req = ["Wall Number", "Name", "Position X", "Position Y", "Position Z",
           "Shape Type", "Width", "Height", "Status"]

    if "Name" not in df_combined_all.columns:
        df_combined_all["Name"] = ""

    mask_keep = ~df_combined_all["Name"].astype(str).str.startswith(("Basic Wall", "CP"))
    df = df_combined_all.loc[mask_keep].copy()

    for c in req:
        if c not in df.columns:
            df[c] = "blank" if c == "Status" else np.nan

    def _to_int_if_digit(v):
        s = str(v).strip()
        return int(s) if s.isdigit() else s

    num = pd.to_numeric(
        df["Wall Number"].astype(str).str.strip().str.extract(r"(\d+)", expand=False),
        errors="coerce"
    )
    df["Wall Number"] = df["Wall Number"].apply(_to_int_if_digit)
    max_wall = int(num.max()) if num.notna().any() else None

    if max_wall == 6:
        allowed_walls = {1, 2, 3, 4, 5, 6}
        placement_bins = {"placement1": {1, 4, 5, 6}, "placement2": {2, 3}}
    else:
        allowed_walls = {1, 2, 3, 4}
        placement_bins = {"placement1": {1, 2, 3, 4}}  # fixed comma typo

    is_floor_all = df["Wall Number"].astype(str).str.strip().str.upper().eq("F")
    df = df[df["Wall Number"].isin(allowed_walls) | is_floor_all].copy()

    wall_numbers_by_placement: Dict[str, Any] = {}
    unique_width_height_dict: Dict[Any, Dict[str, set]] = {}

    def _unique_status_list(series: pd.Series):
        out, seen = [], set()
        for v in series:
            s = "blank" if pd.isna(v) or str(v).strip() == "" else str(v)
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    for pname, walls in placement_bins.items():
        is_floor_here = df["Wall Number"].astype(str).str.strip().str.upper().eq("F")
        part = df[df["Wall Number"].isin(walls) | is_floor_here].copy()
        if part.empty:
            continue

        wall_numbers_by_placement[pname] = {
            "markingidentifiers": part["Name"].astype(str).tolist(),
            "Wall Number": part["Wall Number"].tolist(),
            "Position X": part["Position X"].tolist(),
            "Position Y": part["Position Y"].tolist(),
            "Position Z": part["Position Z"].tolist(),
            "Shape Type": part["Shape Type"].tolist(),
            "width": part["Width"].tolist(),
            "height": part["Height"].tolist(),
            "Status": part["Status"].tolist(),
        }

        for wall_num, w, h in zip(part["Wall Number"], part["Width"], part["Height"]):
            bucket = unique_width_height_dict.setdefault(wall_num, {"width": set(), "height": set()})
            bucket["width"].add(w)
            bucket["height"].add(h)

        _ = part.groupby("Wall Number", as_index=False).agg({"Status": _unique_status_list})

    _ = pd.DataFrame([
        {
            "Wall Number": wall_num,
            "width": sorted(list(data["width"]), key=lambda v: (pd.isna(v), v)),
            "height": sorted(list(data["height"]), key=lambda v: (pd.isna(v), v)),
        }
        for wall_num, data in unique_width_height_dict.items()
    ])

    return wall_numbers_by_placement
