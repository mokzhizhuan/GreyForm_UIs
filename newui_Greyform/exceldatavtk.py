import pandas as pd
import numpy as np

def exceldataextractor(df_combined_all: pd.DataFrame):
    req = ["Wall Number", "Name", "LX", "LY", "LZ", "Marking Type", "Width", "Height", "Status"]
    mask_keep = ~df_combined_all["Name"].astype(str).str.startswith(("Basic Wall", "CP"))
    df = df_combined_all.loc[mask_keep].copy()
    for c in req:
        if c not in df.columns:
            df[c] = "blank" if c == "Status" else np.nan
    def _to_int_if_digit(v):
        s = str(v)
        return int(s) if s.isdigit() else s
    num = pd.to_numeric(
        df["Wall Number"].astype(str).str.strip().str.extract(r"(\d+)", expand=False),
        errors="coerce"
    )
    df["Wall Number"] = df["Wall Number"].apply(_to_int_if_digit)
    max_wall = int(num.max()) if num.notna().any() else None
    is_floor = df["Wall Number"].astype(str).str.strip().str.upper().eq("F")
    if max_wall == 6:
        allowed_walls = {1, 2, 3, 4, 5, 6}
        df = df[df["Wall Number"].isin(allowed_walls)]
        placement_bins = {
            "placement1": {1, 5, 6},
            "placement2": {2, 3, 4},
        }
    else:
        allowed_walls = {1, 2, 3, 4}
        df = df[df["Wall Number"].isin(allowed_walls)]
        placement_bins = {
            "placement1": {1, 4},
            "placement2": {2, 3},
        }
    wall_numbers_by_placement = {}
    unique_wall_numbers_by_placement = {}
    unique_width_height_dict = {}
    placement_names = []
    for pname, walls in placement_bins.items():
        part = df[df["Wall Number"].isin(walls) | is_floor].copy()
        if part.empty:
            continue
        placement_names.append(pname)
        wall_numbers_by_placement[pname] = {
            "markingidentifiers": part["Name"].astype(str).tolist(),
            "Wall Number": part["Wall Number"].tolist(),
            "Position X": part["LX"].tolist(),
            "Position Y": part["LY"].tolist(),
            "Position Z": part["LZ"].tolist(),
            "Shape Type": part["Marking Type"].tolist(),
            "width": part["Width"].tolist(),
            "height": part["Height"].tolist(),
            "Status": part["Status"].tolist(),
        }
        for wall_num, w, h in zip(part["Wall Number"], part["Width"], part["Height"]):
            bucket = unique_width_height_dict.setdefault(wall_num, {"width": set(), "height": set()})
            bucket["width"].add(w)
            bucket["height"].add(h)
        unique_data = (
            part.groupby("Wall Number", as_index=False)
                .agg({"Status": lambda x: sorted(set(x))})
        )
        unique_wall_numbers_by_placement[pname] = {
            "wall_numbers": unique_data["Wall Number"].tolist(),
            "status": unique_data["Status"].tolist(),
        }
    unique_width_height_df = pd.DataFrame([
        {
            "Wall Number": wall_num,
            "width": sorted(list(data["width"]), key=lambda v: (pd.isna(v), v)),
            "height": sorted(list(data["height"]), key=lambda v: (pd.isna(v), v)),
        }
        for wall_num, data in unique_width_height_dict.items()
    ])
    wall_list = unique_width_height_df.to_dict(orient="records")
    return wall_numbers_by_placement
