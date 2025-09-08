import pandas as pd
import numpy as np

def exceldataextractor(df_combined_all: pd.DataFrame):
    req = ["Wall Number", "Name", "Position X", "Position Y", "Position Z", "Shape Type", "Width", "Height", "Status"]

    # Remove Basic Wall / CP rows (you can extend this mask as needed)
    mask_keep = ~df_combined_all["Name"].astype(str).str.startswith(("Basic Wall", "CP"))
    df = df_combined_all.loc[mask_keep].copy()

    # Ensure required columns exist
    for c in req:
        if c not in df.columns:
            df[c] = "blank" if c == "Status" else np.nan

    # Normalize Wall Number (keep 'F', convert digit-like to int, else leave as-is)
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
        placement_bins = {"placement1": {1, 5, 6}, "placement2": {2, 3, 4}}
    else:
        allowed_walls = {1, 2, 3, 4}
        placement_bins = {"placement1": {1, 4}, "placement2": {2, 3}}

    # Keep only allowed walls + Floor ('F') to avoid later reindex warnings
    is_floor_all = df["Wall Number"].astype(str).str.strip().str.upper().eq("F")
    df = df[df["Wall Number"].isin(allowed_walls) | is_floor_all].copy()

    wall_numbers_by_placement = {}
    unique_width_height_dict = {}

    # Helper: normalize Status and dedupe while preserving order
    def _unique_status_list(series: pd.Series):
        out, seen = [], set()
        for v in series:
            s = "blank" if pd.isna(v) or str(v).strip() == "" else str(v)
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    for pname, walls in placement_bins.items():
        # Recompute floor mask on the already filtered df to avoid misalignment
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

        # Collect unique width/height per wall (no mixed-type compare issues expected here)
        for wall_num, w, h in zip(part["Wall Number"], part["Width"], part["Height"]):
            bucket = unique_width_height_dict.setdefault(wall_num, {"width": set(), "height": set()})
            bucket["width"].add(w)
            bucket["height"].add(h)

        # If you still need per-wall unique statuses without sorting:
        _ = (
            part.groupby("Wall Number", as_index=False)
                .agg({"Status": _unique_status_list})
        )
        # (Not returned, but left here if you hook it up later.)

    # You compute unique_width_height_df but don’t use it in the return; keeping as-is
    _ = pd.DataFrame([
        {
            "Wall Number": wall_num,
            "width": sorted(list(data["width"]), key=lambda v: (pd.isna(v), v)),
            "height": sorted(list(data["height"]), key=lambda v: (pd.isna(v), v)),
        }
        for wall_num, data in unique_width_height_dict.items()
    ])

    return wall_numbers_by_placement
