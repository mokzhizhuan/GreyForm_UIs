from typing import Optional, TypedDict, List, Literal, Dict

# ---- Types ----
class JointPose(TypedDict):
    j0: float
    j1: float
    j2: float
    j3: float
    j4: float
    j5: float

class HomeOnlyRequired(TypedDict):
    home: List[JointPose]

# title is optional; home is required
class HomeOnly(HomeOnlyRequired, total=False):
    title: str

PoseSection = Literal["floor", "wall_1", "wall_2"]
PoseHomeMap = Dict[PoseSection, HomeOnly]

POSE_KEYS = ("j0", "j1", "j2", "j3", "j4", "j5")


# ---- Loader that preserves optional 'title' and filters to j0..j5 ----
def load_home_only(path: str) -> PoseHomeMap:
    import json
    with open(path, "r") as f:
        raw = json.load(f)

    def clean_home(section_key: PoseSection) -> HomeOnly:
        section_raw = raw.get(section_key, {})
        home_list = section_raw.get("home", [])
        cleaned_home: List[JointPose] = [
            {k: float(p[k]) for k in POSE_KEYS if k in p}  # enforce j0..j5 order+types
            for p in home_list
        ]
        out: HomeOnly = {"home": cleaned_home}
        # keep title if present
        if isinstance(section_raw.get("title"), str):
            out["title"] = section_raw["title"]
        return out

    return {
        "floor":  clean_home("floor"),
        "wall_1": clean_home("wall_1"),
        "wall_2": clean_home("wall_2"),
    }


# ---- Helper: get first 'home' pose for a section ----
def get_home_pose(
    home_only: PoseHomeMap,
    section: PoseSection
) -> Optional[JointPose]:
    seq = home_only.get(section, {}).get("home", [])
    return seq[0] if seq else None


# ---- Helper: resolve a nice title (JSON 'title' or derived from key) ----
def get_section_title(section: PoseSection, section_data: HomeOnly) -> str:
    if "title" in section_data and isinstance(section_data["title"], str):
        return section_data["title"]
    return f"{section.replace('_', ' ').title()} Home Pose"


# ---- Example: loop all sections, print title + first home pose ----
def print_home_sections(home_only: PoseHomeMap) -> None:
    for section, data in home_only.items():
        title = get_section_title(section, data)
        pose = data["home"][0] if data.get("home") else None
        if pose:
            ordered = {k: pose[k] for k in POSE_KEYS if k in pose}
            print(f"{title}: {ordered}")
        else:
            print(f"{title}: <not found>")


# ===== Usage =====
# poses_path = "/mnt/data/example_poses.json"  # set your path
# home_only = load_home_only(poses_path)
# print_home_sections(home_only)

# # If you need a single pose by section:
# section_pose = get_home_pose(home_only, "wall_2")
# if section_pose:
#     print(get_section_title("wall_2", home_only["wall_2"]), section_pose)
