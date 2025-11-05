# backend/placementcoord.py
import json, re
from typing import List, Dict, Any, Optional

_CP_NAME_RE = re.compile(r"^WallCP(\d+)$")

def placementcoord_from_json(json_path: str) -> Optional[List[List[float]]]:
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    cps = []
    for r in items if isinstance(items, list) else []:
        if str(r.get("Marking Type", "")) != "CenterWallPoint":
            continue
        m = _CP_NAME_RE.match(str(r.get("Name", "")))
        if not m:
            continue
        idx = int(m.group(1))
        cps.append((idx, r))

    if not cps:
        return None

    cps.sort(key=lambda t: t[0])
    first, last = cps[0][1], cps[-1][1]
    start = [float(first.get("X", 0)), float(first.get("Y", 0)), float(first.get("Z", 0))]
    end   = [float(last.get("X", 0)),  float(last.get("Y", 0)),  float(last.get("Z", 0))]
    return [start, end]

def strict_index_loop_1_2(runner, placementcoord, dwell_s=0.5):
    """
    Send calibration points in strict order: index 1 then index 2.
    placementcoord must be [[x1,y1,z1], [x2,y2,z2]] (at least 2 points).
    """
    import time

    if not isinstance(placementcoord, (list, tuple)) or len(placementcoord) < 2:
        raise ValueError("placementcoord must contain at least two points: [[x1,y1,z1],[x2,y2,z2]]")

    # Helper to coerce to ints for publish_selection_message fallback
    def _to_int3(pt):
        return [int(round(float(pt[0]))), int(round(float(pt[1]))), int(round(float(pt[2])))]

    # Strict 1-based index loop
    for public_idx in (1, 2):
        zero_based = public_idx - 1
        xyz = placementcoord[zero_based]
        runner._emit(f"Calibrating placement index {public_idx}: {xyz}")

        # Prefer a dedicated publisher if available
        if hasattr(runner.talker_node, "publish_calibration_point"):
            # Some listeners might expect 1-based index; we pass public_idx.
            runner.talker_node.publish_calibration_point(index=public_idx, point=xyz)
        else:
            # Fallback using your existing selection API as a signal
            px, py, pz = _to_int3(xyz)
            runner.talker_node.publish_selection_message(
                wn=None,
                picked_position=[px, py, pz],
                markingtype=f"Calibrate:{public_idx}"
            )

        time.sleep(dwell_s)  # small dwell between 1 and 2

    runner._emit("✅ Strict index loop (1 → 2) complete.")