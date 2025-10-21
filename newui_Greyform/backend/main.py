# backend/main.py
import os, stat , json , time , glob , shutil, traceback , subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Union, Tuple , Any
import dataanalysis as datadraft
import pwd, grp , requests
import subprocess, shlex
import pandas as pd
import re
import threading
#import httpx
from requests.auth import HTTPDigestAuth
from errno import errorcode
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Form, HTTPException, Query, Request , HTTPException , Body
from fastapi.middleware.cors import CORSMiddleware

"""class ConnectPayload(BaseModel):
    ip: IPvAnyAddress = Field(..., description="Robot IPv4/IPv6 address")
    # Optional: add creds if you want to probe ABB Web Services
    username: str | None = None
    password: str | None = None
    # Optional: which port to probe for a basic connectivity check
    port: int = 80
    timeout_sec: float = 1.5

class ConnectResponse(BaseModel):
    ip: str
    reachable: bool
    detail: str

@app.post("/api/robot/connect", response_model=ConnectResponse)
def connect_robot(payload: ConnectPayload):
    # Basic TCP reachability probe (non-privileged; no ICMP required)
    try:
        with socket.create_connection((str(payload.ip), payload.port), timeout=payload.timeout_sec):
            return ConnectResponse(ip=str(payload.ip), reachable=True, detail=f"TCP {payload.port} open")
    except OSError as e:
        raise HTTPException(status_code=502, detail=f"Cannot reach {payload.ip}:{payload.port} - {e}")"""


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
PIDFILE = Path("/tmp/greyform_ui.pid")
LOCKFILE = Path("/tmp/greyform_ui.lock")
LOGFILE = Path("/tmp/greyform_ui.log")
WANTED_EXTS = {".ifc", ".ifczip", ".step", ".stp", ".csv", ".xlsx", ".xls"}
IFC_EXTS = {".ifc", ".ifczip", ".ifcxml"}
MEDIA_ROOTS = [Path("/media"), Path("/run/media")]
CACHE_FILE = Path("/tmp/ifc_cache.json")
IFC_CACHE: Dict[str, Dict[str, float]] = {}
_CACHE = {"ts": 0.0, "preferred": None, "choices": []}
_CACHE_TTL = 5.0  # seconds
PROJECT_DIR = Path(__file__).resolve().parent.parent  
_state_lock = threading.Lock()
LAST_USB_PATH: Optional[Path] = None


def _get_usb_base(usb_path: Optional[str] = None) -> Path:
    """
    Return a valid base directory or file path.
    Accepts either a folder (/media/.../USB) or a direct file (/media/.../USB/PBU_TERRAHL2.xlsx).
    """
    if usb_path:
        p = Path(usb_path).resolve()
        if not p.exists():
            raise HTTPException(
                status_code=400,
                detail=f"usb_path not visible: {usb_path}. Check that it is mounted inside the container."
            )
        return p

    # If no usb_path provided, fall back to global (optional)
    if 'LAST_USB_PATH' in globals() and globals()['LAST_USB_PATH']:
        return globals()['LAST_USB_PATH']

    raise HTTPException(status_code=400, detail="usb_path not provided and no cached path available.")

def _excel_output_path(usb_path: Optional[str] = None, excel: Optional[str] = None) -> Path:
    # 1) Direct excel path provided
    if excel:
        f = Path(excel).resolve()
        if f.exists() and f.is_file():
            return f
        if usb_path:
            f2 = (Path(usb_path).resolve() / excel).resolve()
            if f2.exists() and f2.is_file():
                return f2
        raise HTTPException(status_code=404, detail=f"Excel file not found: {excel}")

    # 2) Only usb_path provided
    if usb_path:
        base = Path(usb_path).resolve()
        if not base.exists():
            raise HTTPException(status_code=400, detail=f"usb_path not visible: {usb_path}")
        for name in ("PBU_TERRAHL2(final).xlsx", "PBU_TERRAHL2.xlsx"):
            f = base / name
            if f.exists() and f.is_file():
                return f
        raise HTTPException(status_code=404, detail=f"No Excel file found under {usb_path}")

    # 3) Fallback to cached LAST_USB_PATH (optional)
    base = globals().get("LAST_USB_PATH")
    if base and base.exists():
        for name in ("PBU_TERRAHL2(final).xlsx", "PBU_TERRAHL2.xlsx"):
            f = base / name
            if f.exists() and f.is_file():
                return f

    raise HTTPException(status_code=400, detail="Neither excel nor usb_path provided, and nothing cached.")

def _have_gui_env() -> bool:
    return bool(os.environ.get("DISPLAY")) and os.path.exists("/tmp/.X11-unix")

def _find_viewer() -> str:
    for prog in ("soffice", "libreoffice", "xdg-open"):
        if shutil.which(prog):
            return prog
    raise HTTPException(status_code=404, detail="No office viewer found (install 'libreoffice').")

def _launch(cmd: str) -> None:
    try:
        subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to launch: {e}")

# --- NEW: open Excel in view-only mode (no edits) ---
@app.post("/api/open_excel")
def open_excel_view_only(payload: Dict[str, Any] = Body(default={})):
    """
    Open Excel in read-only mode. Accepts either 'excel' (file) or 'usb_path' (dir).
    """
    excel = payload.get("excel")
    usb_path = payload.get("usb_path")

    # 👇 THIS is the missing line in your current code
    p = _excel_output_path(usb_path=usb_path, excel=excel)

    if not _have_gui_env():
        raise HTTPException(status_code=409,
            detail="GUI not available (DISPLAY or /tmp/.X11-unix missing).")

    viewer = _find_viewer()
    if viewer in ("soffice", "libreoffice"):
        cmd = f"{viewer} --view --norestore --nolockcheck --nodefault {shlex.quote(str(p))}"
    else:
        cmd = f"xdg-open {shlex.quote(str(p))}"

    _launch(cmd)
    return {"ok": True, "viewer": viewer, "excel": str(p),
            "note": "Opened in view-only mode" if viewer in ("soffice","libreoffice")
                     else "Opened via xdg-open"}

# --- NEW: compute % completed by reading the Excel (read-only) ---
@app.get("/api/progress")
def progress(
    excel: Optional[str] = Query(None, description="Full path to .xlsx, absolute or relative to usb_path"),
    usb_path: Optional[str] = Query(None, description="USB mount root (dir) if excel not provided"),
):
    # IMPORTANT: pass the params through to the resolver
    p = _excel_output_path(usb_path=usb_path, excel=excel)

    done = 0
    total = 0
    tried = []

    # Try openpyxl first (read-only)
    try:
        import openpyxl  # type: ignore
        tried.append("openpyxl")
        wb = openpyxl.load_workbook(str(p), read_only=True, data_only=True)
        for ws in wb.worksheets:
            # header row
            header = None
            for row in ws.iter_rows(min_row=1, max_row=1, values_only=True):
                header = [str(c).strip() if c is not None else "" for c in row]
                break
            if not header:
                continue
            # Status column (case-insensitive)
            try:
                idx = next(i for i, name in enumerate(header) if name.lower() == "status")
            except StopIteration:
                continue
            for row in ws.iter_rows(min_row=2, values_only=True):
                val = row[idx] if idx < len(row) else None
                if val is None or (isinstance(val, str) and not val.strip()):
                    continue
                total += 1
                if str(val).strip().lower() in {"done", "completed", "ok", "true", "yes"}:
                    done += 1
        wb.close()
    except Exception as e1:
        err1 = str(e1)
        try:
            import pandas as pd  # type: ignore
            tried.append("pandas")
            xls = pd.ExcelFile(str(p))
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                status_col = next((c for c in df.columns if str(c).strip().lower() == "status"), None)
                if status_col is None:
                    continue
                col = df[status_col].dropna().astype(str).str.strip()
                total += int(col.shape[0])
                done  += int(col.str.lower().isin(["done", "completed", "ok", "true", "yes"]).sum())
        except Exception as e2:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read Excel with {tried}: openpyxl='{err1}', pandas='{str(e2)}'"
            )

    percent = float(done) / float(total) * 100.0 if total > 0 else 0.0
    return {"ok": True, "done": done, "total": total, "percent": round(percent, 1), "excel": str(p)}

def _is_mountpoint(p: Path) -> bool:
    try:
        if os.path.ismount(p):
            return True
        st = os.stat(p)
        pst = os.stat(p.parent)
        return st.st_dev != pst.st_dev
    except Exception:
        return False

def _has_entries(p: Path) -> bool:
    try:
        with os.scandir(p) as it:
            next(it)
            return True
    except StopIteration:
        return False
    except PermissionError:
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def _is_media_root(p: Path) -> bool:
    parts = p.resolve().parts
    return (parts == ("/","media")) or (len(parts) == 3 and parts[0]=="/" and parts[1]=="run" and parts[2]=="media")

def _is_user_media_root(p: Path) -> bool:
    parts = p.resolve().parts
    return (len(parts) == 3 and parts[0]=="/" and parts[1]=="media") or \
           (len(parts) == 4 and parts[0]=="/" and parts[1]=="run" and parts[2]=="media")

def _is_media_leaf(p: Path) -> bool:
    parts = p.resolve().parts
    return (len(parts) >= 4 and parts[0]=="/" and parts[1]=="media") or \
           (len(parts) >= 5 and parts[0]=="/" and parts[1]=="run" and parts[2]=="media")

def _cache_load():
    global IFC_CACHE
    try:
        if CACHE_FILE.exists():
            IFC_CACHE = json.loads(CACHE_FILE.read_text())
    except Exception:
        IFC_CACHE = {}
def _cache_save():
    try:
        CACHE_FILE.write_text(json.dumps(IFC_CACHE))
    except Exception:
        pass
_cache_load()

def _which_find() -> str:
    return "/usr/bin/find" if Path("/usr/bin/find").exists() else (shutil.which("find") or "find")

def _expand_roots(root: Optional[str]) -> List[Path]:
    if not root:
        return []
    if any(ch in root for ch in "*?[]"):
        return [Path(p) for p in glob.glob(root) if Path(p).is_dir()]
    return [Path(root)]

def _is_under_media(p: Path) -> bool:
    s = str(p)
    return any(s == str(r) or s.startswith(str(r) + "/") for r in MEDIA_ROOTS)

def _iter_mounts_under_media() -> List[Path]:
    out: List[Path] = []
    try:
        with open("/proc/mounts", "r") as f:
            for ln in f:
                parts = ln.split()
                if len(parts) >= 2:
                    mnt = Path(parts[1])
                    if _is_under_media(mnt):
                        out.append(mnt)
    except Exception:
        pass
    seen, uniq = set(), []
    for p in out:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp not in seen:
            uniq.append(rp)
            seen.add(rp)
    return uniq

def _cheap_list(d: Path, exts: List[str], limit: int = 200) -> List[str]:
    out: List[str] = []
    try:
        with os.scandir(d) as it:
            for i, e in enumerate(it):
                if i >= limit:
                    break
                if e.is_file():
                    nm = e.name
                    if not exts or any(nm.lower().endswith(x) for x in exts):
                        out.append(nm)
    except Exception:
        pass
    return out


def _iter_files(root: Path, max_depth: int = 3):
    base = root.resolve()
    base_depth = len(base.parts)
    for p in base.rglob("*"):
        try:
            if p.is_file():
                depth = len(p.resolve().parts) - base_depth
                if depth <= max_depth:
                    yield p
        except Exception:
            continue

def _root_ok(root: Path) -> Dict:
    if not root.exists() or not root.is_dir():
        return {"exists": False, "valid": False, "files": []}
    files = [p.name for p in _iter_files(root, max_depth=3) if p.suffix.lower() in WANTED_EXTS]
    return {"exists": True, "valid": len(files) > 0, "files": files[:50]}

def pick_ifc(root: Path, recursive: bool = True, max_depth: int = 8) -> Optional[Path]:
    if not root.exists() or not root.is_dir():
        return None
    candidates: List[Tuple[Path, float]] = []
    for p in _iter_files(root, max_depth=max_depth):
        if p.suffix.lower() in IFC_EXTS:
            try:
                candidates.append((p, p.stat().st_mtime))
            except Exception:
                pass
    if not candidates:
        return None
    candidates.sort(key=lambda t: (t[0].suffix.lower() != ".ifc", -t[1]))
    return candidates[0][0]

def _first_existing(*cands: Union[str, Path]) -> Optional[Path]:
    for c in cands:
        if not c:
            continue
        p = Path(c).expanduser().resolve()
        if p.exists():
            return p
    return None

def _require_exists(label: str, p: Path):
    if not p.exists():
        raise HTTPException(status_code=400, detail=f"{label} not found: {p}")

def _pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    proc = Path(f"/proc/{pid}")
    if not proc.exists():
        return False
    try:
        cmd = (proc / "cmdline").read_text(errors="ignore")
        return "mainwindow.py" in cmd or "greyform" in cmd.lower()
    except Exception:
        return False

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}

@app.get("/api/whoami")
def whoami():
    uid = os.geteuid()
    gid = os.getegid()
    def uname(u): 
        try: return pwd.getpwuid(u).pw_name
        except Exception: return f"uid:{u}"
    def gname(g): 
        try: return grp.getgrgid(g).gr_name
        except Exception: return f"gid:{g}"
    return {
        "uid": uid, "gid": gid,
        "user": uname(uid), "group": gname(gid),
        "cwd": os.getcwd(),
        "can_read_media": os.access("/media", os.R_OK | os.X_OK),
        "can_x_ubuntu": os.access("/media/ubuntu", os.X_OK),
    }

@app.get("/api/ifc_probe")
def ifc_probe(path: str = Query(..., description="Absolute path to IFC")):
    p = Path(path)
    if not p.exists() or not p.is_file():
        return {"ok": False, "reason": "not-found-or-not-file", "path": str(p)}
    try:
        st = p.stat()
        with p.open("rb") as f:
            head = f.read(256)
        kind = "zip" if head.startswith(b"PK\x03\x04") else "ifc-or-ifcxml"
        preview = head[:80].decode("ascii", "ignore")
        return {"ok": True, "path": str(p), "size": st.st_size, "kind": kind, "preview": preview}
    except Exception as e:
        eno = getattr(e, "errno", None)
        return {
            "ok": False,
            "reason": type(e).__name__,
            "errno": eno,
            "errno_name": errorcode.get(eno, None) if eno is not None else None,
            "trace": traceback.format_exc().splitlines()[-1],
            "path": str(p),
        }

@app.get("/api/find_ifc_quick")
def find_ifc_quick(root: str = Query(..., description="USB mount root")):
    r = Path(root)
    if not r.exists() or not r.is_dir():
        return {"ok": False, "reason": "root-not-dir", "match": None}
    got = IFC_CACHE.get(str(r))
    if got:
        p = Path(got.get("path", ""))
        try:
            if p.is_file():
                return {"ok": True, "match": str(p), "cached": True}
        except Exception:
            pass
    def scan_dir_once(d: Path) -> Optional[str]:
        try:
            with os.scandir(d) as it:
                for e in it:
                    if e.is_file():
                        n = e.name.lower()
                        if n.endswith(".ifc") or n.endswith(".ifczip") or n.endswith(".ifcxml"):
                            return str(Path(e.path))
        except Exception:
            pass
        return None
    m = scan_dir_once(r)
    if m:
        IFC_CACHE[str(r)] = {"path": m, "mtime": Path(m).stat().st_mtime}
        _cache_save()
        return {"ok": True, "match": m, "cached": False}
    lvl1: List[Path] = []
    try:
        with os.scandir(r) as it:
            for e in it:
                if e.is_dir(follow_symlinks=False):
                    lvl1.append(Path(e.path))
    except Exception:
        pass
    PREFERRED = {"ifc", "IFC", "models", "model", "bim", "BIM", "export", "exports"}
    for d in lvl1:
        if d.name in PREFERRED:
            m = scan_dir_once(d)
            if m:
                IFC_CACHE[str(r)] = {"path": m, "mtime": Path(m).stat().st_mtime}
                _cache_save()
                return {"ok": True, "match": m, "cached": False}
    for d in lvl1:
        try:
            with os.scandir(d) as it:
                for f in it:
                    if f.is_dir(follow_symlinks=False):
                        m = scan_dir_once(Path(f.path))
                        if m:
                            IFC_CACHE[str(r)] = {"path": m, "mtime": Path(m).stat().st_mtime}
                            _cache_save()
                            return {"ok": True, "match": m, "cached": False}
        except Exception:
            continue
    return {"ok": False, "reason": "no-quick-hit", "match": None}

@app.get("/api/find_ifc_fast")
def find_ifc_fast(
    root: Optional[str] = Query(None, description="Optional mount or wildcard, e.g. /media/*/*"),
    max_depth: int = Query(3, ge=0, le=20),
    timeout_ms: int = Query(1200, ge=100, le=10000),
):
    candidates: List[Path] = []
    if root:
        if any(ch in root for ch in "*?[]"):
            candidates = [Path(p) for p in glob.glob(root) if Path(p).is_dir()]
        else:
            candidates = [Path(root)]
    if not candidates:
        mounts = _iter_mounts_under_media() or MEDIA_ROOTS
        candidates = [m for m in mounts if m.exists() and m.is_dir()]
    per_root_timeout = max(200, int(timeout_ms / max(1, min(len(candidates), 4))))
    find_bin = _which_find()
    for r in candidates:
        got = IFC_CACHE.get(str(r))
        if got:
            p = Path(got.get("path", ""))
            try:
                if p.is_file():
                    return {"ok": True, "match": str(p), "cached": True}
            except Exception:
                pass
        cmd = [
            find_bin, str(r), "-maxdepth", str(max_depth),
            "-type", "f",
            "(", "-iname", "*.ifc", "-o", "-iname", "*.ifczip", "-o", "-iname", "*.ifcxml", ")",
            "-printf", "%T@ %p\n",
        ]
        try:
            cp = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=per_root_timeout / 1000.0, check=False)
            out = cp.stdout.strip()
            if out:
                lines = out.splitlines()
                lines.sort(key=lambda s: (float(s.split(" ", 1)[0]),
                                          s.split(" ", 1)[1].lower().endswith(".ifc")), reverse=True)
                ts, path = lines[0].split(" ", 1)
                IFC_CACHE[str(r)] = {"path": path, "mtime": float(ts)}
                _cache_save()
                return {"ok": True, "match": path, "cached": False}
        except Exception:
            pass
        try:
            cmd2 = [find_bin, str(r), "-maxdepth", str(max_depth), "-type", "f",
                    "(", "-iname", "*.ifc", "-o", "-iname", "*.ifczip", "-o", "-iname", "*.ifcxml", ")"]
            cp2 = subprocess.run(cmd2, capture_output=True, text=True,
                                 timeout=per_root_timeout / 1000.0, check=False)
            out2 = [p for p in cp2.stdout.strip().splitlines() if p]
            if out2:
                sel = out2[0]
                try:
                    ts = Path(sel).stat().st_mtime
                except Exception:
                    ts = 0.0
                IFC_CACHE[str(r)] = {"path": sel, "mtime": ts}
                _cache_save()
                return {"ok": True, "match": sel, "cached": False}
        except Exception:
            pass
    return {"ok": False, "reason": "no-match", "match": None}


@app.get("/api/detect_usb")
def detect_usb(
    path: Optional[str] = Query(None, description="Optional hint; wildcards like /media/*/*"),
    scan_media: bool = Query(True, description="Scan /media and /run/media"),
    need_files: bool = Query(False, description="If true, add cheap (non-recursive) file list"),
):
    now = time.monotonic()
    if (now - _CACHE["ts"]) < _CACHE_TTL and _CACHE["preferred"]:
        return {
            "found": True, "preferred": _CACHE["preferred"],
            "choices": _CACHE["choices"], "checked": [], "cached": True
        }
    checked: List[Dict] = []
    choices: List[Dict] = []
    roots = _expand_roots(path)
    if scan_media:
        roots += [Path("/media"), Path("/run/media")]
        roots += [Path(p) for p in glob.glob("/media/*")]
        roots += [Path(p) for p in glob.glob("/media/*/*")]
        roots += [Path(p) for p in glob.glob("/run/media/*")]
        roots += [Path(p) for p in glob.glob("/run/media/*/*")]
    seen = set()
    for d in roots:
        try:
            rp = d.resolve()
        except Exception:
            continue
        if rp in seen or not rp.exists() or not rp.is_dir():
            continue
        seen.add(rp)
        if _is_media_root(rp):
            checked.append({
                "path": str(rp), "exists": True, "valid": False,
                "ismount": False, "has_entries": _has_entries(rp),
                "reason": "media_root"
            })
            continue
        has_any = _has_entries(rp)
        ismnt = _is_mountpoint(rp)
        files = [] if not need_files else _cheap_list(rp, exts=[], limit=200)
        if _is_user_media_root(rp) and not has_any:
            checked.append({
                "path": str(rp), "exists": True, "valid": False,
                "ismount": ismnt, "has_entries": has_any,
                "reason": "empty_user_media_root"
            })
            continue
        under_media = str(rp).startswith("/media/") or str(rp).startswith("/run/media/")
        if under_media:
            valid = _is_media_leaf(rp) and (ismnt or has_any or bool(files))
        else:
            valid = bool(files) or ismnt or has_any
        info = {
            "path": str(rp),
            "exists": True,
            "valid": valid,
            "files": files,
            "ismount": ismnt,
            "has_entries": has_any,
        }
        checked.append(info)
        if info["valid"]:
            choices.append({"path": info["path"], "files": info["files"]})
            _CACHE.update(ts=now, preferred=info["path"], choices=choices)
            return {
                "found": True, "preferred": info["path"],
                "choices": choices, "checked": checked, "cached": False
            }
    return {"found": False, "preferred": None, "choices": choices, "checked": checked, "cached": False}

@app.post("/api/checkifc")
async def data_checker(
    usb_path: str = Form(...),
    ifc_path: str = Form(...),
    model_sides: int = Form(...),
    force: bool = Form(False),
):
    datadrafter = datadraft.data_draft(ifc_path, model_sides, usb_path)
    df_combined_data = datadrafter.analysis()
    if df_combined_data is None:
        raise HTTPException(
            status_code=400,
            detail="Wrong PBU sides file , please include the specific PBU sides with the file"
        )
    return {"ok": True, "model": model_sides , "cached": True}
        


@app.post("/api/launch_ui")
async def launch_ui(
    usb_path: str = Form(...),
    ifc_path: Optional[str] = Form(None),
    force: bool = Form(False),
):
    try:
        base = Path(usb_path).resolve()
        if not base.exists() or not base.is_dir():
            raise HTTPException(status_code=400, detail=f"usb_path not found or not a directory: {usb_path}")

        # pick or validate IFC
        if ifc_path:
            ifc = Path(ifc_path).resolve()
        else:
            ifc = pick_ifc(base, recursive=True, max_depth=8)
            if ifc is None:
                raise HTTPException(status_code=404, detail="No IFC file found on the USB drive")

        # IFC must live inside the USB
        try:
            _ = ifc.resolve().relative_to(base)
        except ValueError:
            raise HTTPException(status_code=400, detail="IFC must be inside usb_path")

        # Build Excel output path ON THE USB (optionally put in a subfolder)
        # results_dir = base / "GreyForm"  # uncomment if you want a folder
        results_dir = base
        results_dir.mkdir(parents=True, exist_ok=True)

        # filename (no spaces is safer for some environments)
        # fname = f"PBU_TERRAHL2_{datetime.now():%Y%m%d-%H%M}.xlsx"
        fname = "PBU_TERRAHL2.xlsx"
        excel_output = (results_dir / fname).resolve()

        # security: must still be under the USB root
        try:
            excel_output.relative_to(base)
        except ValueError:
            raise HTTPException(status_code=400, detail="Output path escapes usb_path")

        # basic writability check
        if not os.access(results_dir, os.W_OK):
            raise HTTPException(status_code=500, detail=f"USB path not writable: {results_dir}")

        main_py = (PROJECT_DIR / "mainwindow.py").resolve()
        ui_file = (PROJECT_DIR / "UI_Design" / "greyform_sweefeng.ui").resolve()
        excel_checklist = (PROJECT_DIR / "Greyform TERRAHL2(JMB)-T1a BOM Checklist 20231211.xlsx").resolve()

        if not main_py.exists():
            raise HTTPException(500, detail=f"mainwindow.py not found: {main_py}")
        if not ui_file.exists():
            raise HTTPException(500, detail=f"UI .ui file not found: {ui_file}")

        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        env.setdefault("QT_QPA_PLATFORM", "xcb")

        # pass the USB output path to your app
        args = [
            "python3",
            str(main_py),
            str(ui_file),
            str(ifc),
            str(excel_checklist),
            str(excel_output),
        ]
        print(excel_output)
        LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        log_f = open(LOGFILE, "ab", buffering=0)

        if LOCKFILE.exists():
            LOCKFILE.unlink(missing_ok=True)
        if PIDFILE.exists():
            try:
                saved = int(PIDFILE.read_text().strip())
                if _pid_running(saved):
                    return {"status": "running", "message": f"UI already running (pid {saved})", "pid": saved}
            except Exception:
                pass

        proc = subprocess.Popen(
            args,
            cwd=str(PROJECT_DIR),
            env=env,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        PIDFILE.write_text(str(proc.pid))
        return {
            "status": "started",
            "message": f"UI started (pid {proc.pid})",
            "pid": proc.pid,
            "ifc_path": str(ifc),
            "excel_output": str(excel_output),  # <-- returned for UI visibility if needed
            "log_file": str(LOGFILE),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception launching with usb_path={usb_path}: {e}")
    
def _load_workbook(path: Path) -> Dict[str, pd.DataFrame]:
    # Sheet dict: {sheet_name: DataFrame}
    return pd.read_excel(path, sheet_name=None)
    
def _find_excel_from_usb(usb_path: str) -> Path:
    """
    Accepts either:
      - a directory path (e.g., 'E:\\' or '/media/usb')
      - a direct file path (e.g., 'E:\\project\\master.xlsx')
    Returns a Path to an existing Excel file.
    Selection rule for directories: newest *.xlsx or *.xls by modified time.
    """
    p = Path(usb_path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"Path not found: {p}")

    if p.is_file():
        if p.suffix.lower() in (".xlsx", ".xls"):
            return p
        raise ValueError(f"Not an Excel file: {p}")

    # Directory: pick most recent Excel
    candidates = list(p.rglob("*.xlsx")) + list(p.rglob("*.xls"))
    if not candidates:
        raise FileNotFoundError(f"No Excel files found under: {p}")

    # newest by mtime
    candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return candidates[0]

def _load_workbook(path: Path) -> Dict[str, pd.DataFrame]:
    # Sheet dict: {sheet_name: DataFrame}
    return pd.read_excel(path, sheet_name=None)


def _build_cp_view(
    book: Dict[str, pd.DataFrame],
    mode: str = "columns",
    key: str = "Type",
) -> Dict[str, pd.DataFrame]:
    """
    CP filtering modes:
      - 'columns': keep only columns with header containing 'CP'
      - 'rows_by_col_equals': keep rows where df[key] == 'CP' (case-insensitive)
      - 'rows_any_cell_contains': keep rows where any cell contains 'CP'
    """
    out: Dict[str, pd.DataFrame] = {}
    for name, df in book.items():
        if df.empty:
            out[name] = df.copy()
            continue

        if mode == "columns":
            cp_cols = [c for c in df.columns if "cp" in str(c).lower()]
            out[name] = df[cp_cols].copy() if cp_cols else pd.DataFrame(columns=[])
        elif mode == "rows_by_col_equals":
            if key in df.columns:
                out[name] = df[df[key].astype(str).str.fullmatch(r"(?i)CP")].copy()
            else:
                out[name] = df.iloc[0:0].copy()
        elif mode == "rows_any_cell_contains":
            mask = df.apply(lambda col: col.astype(str).str.contains(r"\bCP\b", flags=re.I, na=False))
            out[name] = df[mask.any(axis=1)].copy()
        else:
            raise ValueError(f"Unknown CP mode: {mode}")
    return out


def _frames_to_json(book: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    return {name: df.to_dict(orient="records") for name, df in book.items()}
    

@app.post("/api/ui_initailzecamdriver")
def ui_initailzecamdriver(
    usb_path: str = Form(...),
    ifc_path: Optional[str] = Form(None),
    force: bool = Form(False),
    cp_mode: str = Form("columns"),
    cp_key: str = Form("Type"),
):
    """
    Initialize UI by loading Excel from a USB path.
    - usb_path can be a drive root (e.g., E:\\) or a full file path (e.g., E:\\data\\master.xlsx)
    - cp_mode controls how the CP-only view is created (columns | rows_by_col_equals | rows_any_cell_contains)
    - cp_key is used when cp_mode = 'rows_by_col_equals'
    - 'force' = True will reload even if already initialized
    - ifc_path accepted but optional (not used here; you can stash it in state if needed)
    """
    try:
        excel_file = _find_excel_from_usb(usb_path)

        with _state_lock:
            # If already loaded and not forcing, skip reload
            already_loaded = getattr(app.state, "excel_source", None) == str(excel_file)
            if already_loaded and not force:
                cp_json = _frames_to_json(getattr(app.state, "book_cp", {}))
                return {
                    "status": "already_initialized",
                    "excel": str(excel_file),
                    "sheets": list(getattr(app.state, "book_full", {}).keys()),
                    "cp_mode": getattr(app.state, "cp_mode", "columns"),
                    "cp_key": getattr(app.state, "cp_key", "Type"),
                    "cp_preview": {k: v[:3] for k, v in cp_json.items()},  # small preview
                }

            # Load workbook
            book_full = _load_workbook(excel_file)
            book_cp = _build_cp_view(book_full, mode=cp_mode, key=cp_key)

            # Cache in app.state for other routes
            app.state.book_full = book_full
            app.state.book_cp = book_cp
            app.state.excel_source = str(excel_file)
            app.state.cp_mode = cp_mode
            app.state.cp_key = cp_key
            app.state.ifc_path = ifc_path  # stash if you’ll use it later

            cp_json = _frames_to_json(book_cp)

        return {
            "status": "initialized",
            "excel": str(excel_file),
            "sheet_count": len(book_full),
            "sheets": list(book_full.keys()),
            "cp_mode": cp_mode,
            "cp_key": cp_key,
            # keep the JSON small here; build a dedicated endpoint to fetch all CP data
            "cp_preview": {k: v[:3] for k, v in cp_json.items()},
        }

    # Friendly error mapping
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {e}")

    

@app.post("/api/ui_closed")
def ui_closed(pid: int = Form(...)):
    try:
        saved = int(PIDFILE.read_text().strip())
        if saved == pid:
            PIDFILE.unlink(missing_ok=True)
            LOCKFILE.write_text(datetime.now().isoformat())
    except Exception:
        pass
    return {"ok": True}

@app.get("/api/ui_status")
def ui_status(pid: Optional[int] = Query(None)):
    if pid is None and PIDFILE.exists():
        try:
            pid = int(PIDFILE.read_text().strip())
        except Exception:
            pid = None
    if pid is None:
        return {"running": False, "pid": None}
    running = _pid_running(pid)
    if not running and PIDFILE.exists():
        try:
            saved = int(PIDFILE.read_text().strip())
            if saved == pid:
                PIDFILE.unlink(missing_ok=True)
                if not LOCKFILE.exists():
                    LOCKFILE.write_text(datetime.now().isoformat())
        except Exception:
            pass
    return {"running": running, "pid": pid}

@app.post("/api/reset_lock")
def reset_lock():
    try:
        LOCKFILE.unlink(missing_ok=True)
        return {"ok": True, "message": "Lock cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear lock: {e}")
