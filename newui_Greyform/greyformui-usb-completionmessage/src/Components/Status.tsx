import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import ModelSelection from "./ModelSelection";
import RobotIPInput from "./RobotIPInput";
import ABBHOMEImage from '../assets/ABB Robot placeholder image.jpg';

const svg = `
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 800'>
  <rect fill='#020133' width='800' height='800'/>
  <g fill='none' stroke='#1C60FF' stroke-width='1'>
    <path d='M769 229L1037 260.9M927 880L731 737 520 660 309 538 40 599 295 764 126.5 879.5 40 599-197 493 102 382-31 229 126.5 79.5-69-63'/>
    <path d='M-31 229L237 261 390 382 603 493 308.5 537.5 101.5 381.5M370 905L295 764'/>
    <path d='M520 660L578 842 731 737 840 599 603 493 520 660 295 764 309 538 390 382 539 269 769 229 577.5 41.5 370 105 295 -36 126.5 79.5 237 261 102 382 40 599 -69 737 127 880'/>
    <path d='M520-140L578.5 42.5 731-63M603 493L539 269 237 261 370 105M902 382L539 269M390 382L102 382'/>
    <path d='M-222 42L126.5 79.5 370 105 539 269 577.5 41.5 927 80 769 229 902 382 603 493 731 737M295-36L577.5 41.5M578 842L295 764M40-201L127 80M102 382L-261 269'/>
  </g>
  <g fill='#8F8B8B'>
    <circle cx='769' cy='229' r='5'/><circle cx='539' cy='269' r='5'/><circle cx='603' cy='493' r='5'/>
    <circle cx='731' cy='737' r='5'/><circle cx='520' cy='660' r='5'/><circle cx='309' cy='538' r='5'/>
    <circle cx='295' cy='764' r='5'/><circle cx='40' cy='599' r='5'/><circle cx='102' cy='382' r='5'/>
    <circle cx='127' cy='80' r='5'/><circle cx='370' cy='105' r='5'/><circle cx='578' cy='42' r='5'/>
    <circle cx='237' cy='261' r='5'/><circle cx='390' cy='382' r='5'/>
  </g>
</svg>
`.trim();

const bgDataUri = `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;

type UsbState =
  | "waiting"
  | "reading"
  | "success"
  | "error"
  | "launching"
  | "shutdown"
  | "checked_ok"    // ✅ validated, can launch
  | "invalid_model"
  | "robot_connected"
  | "home_verified";

const views = {
  waiting:  { title: "Please insert a USB drive to continue", message: "Click Start to detect a USB drive.", variant: "primary", primaryText: "Start", showSpinner: false },
  reading:  { title: "Reading USB drive...", message: "Please wait while we read the contents of the USB drive.", variant: "info",    primaryText: "Cancel",       showSpinner: true },
  success:  { title: "USB drive detected",    message: "Select the correct model, then click Check selection.",   variant: "success", primaryText: "Check selection", showSpinner: false },
  invalid_model: { title: "Wrong model type", message: "Please change the model and Check selection again.",       variant: "error",   primaryText: "Check selection", showSpinner: false },
  checked_ok: { title: "Selection verified",  message: "Model matches the IFC. Please enter the Robot IP Address.",            variant: "success", primaryText: "Launch UI", showSpinner: false },
  error:    { title: "Error reading USB drive", message: "Please plug in your drive",                              variant: "error",   primaryText: "Try Again", showSpinner: false },
  launching:{ title: "Loading…", message: "", variant: "info", primaryText: "Loading…", showSpinner: true },
  shutdown: { title: "Please power off the machine", message: "The operation is completed successfully",           variant: "neutral", primaryText: "", showSpinner: false },
  robot_connected: { title: "Robot Connected", message: "Robot is successfully connected.", variant: "success", primaryText: "Verify HOME position", showSpinner: false },
  home_verified: { title: "Robot in HOME position", message: "You can now launch the UI.", variant: "success", primaryText: "Start UI", showSpinner: false },
} as const;

export default function Status() {
  const [state, setState] = useState<UsbState>("waiting");
  const v = views[state] ?? views.shutdown;

  const API = useMemo(() => {
    const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
    return base.replace(/\/+$/, "");
  }, []);

  const [usbPath, setUsbPath] = useState<string>("");
  const [uiPid, setUiPid] = useState<number | null>(null);
  const [shouldPoll, setShouldPoll] = useState(false);

  const [responseMessage, setResponseMessage] = useState("Ready");
  const [errorDetails, setErrorDetails] = useState("");
  const prevUsbRef = useRef<string>("");
  const [closedMessage, setClosedMessage] = useState("");
  const [lastPollAt, setLastPollAt] = useState<string>("");

  const [lastRunning, setLastRunning] = useState<string>("");
  const [lastError, setLastError] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<number | null>(null);
  const [isValidated, setIsValidated] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [ifcPath, setIfcPath] = useState<string | null>(null);

  const [robotIP, setRobotIP] = useState<string | null>(null);

  const http = useMemo(() => {
  const base = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/+$/,"");
  return axios.create({
    baseURL: base,
    timeout: 0,        // no client-side timeout by default
  });
}, [])

function handleRobotConnect(ip: string) {
    setRobotIP(ip);       // Save the IP for future use
    setState("robot_connected");  // Main state updated
    setResponseMessage(`✅ Connected to robot at ${ip}`);
    setErrorDetails("");  // Clear errors
  }


  // Debug log
  useEffect(() => {
    console.log("[Status]", { state, usbPath, ifcPath, selectedModel, isValidated });
  }, [state, usbPath, ifcPath, selectedModel, isValidated]);

  // Only reset validation when the USB actually changes
  useEffect(() => {
    if (usbPath && usbPath !== prevUsbRef.current) {
      setIsValidated(false);
      setIfcPath(null);
      if (state !== "checked_ok") setState("success");
      prevUsbRef.current = usbPath;
    }
    if (!usbPath && prevUsbRef.current) {
      setIsValidated(false);
      setIfcPath(null);
      setState("waiting");
      prevUsbRef.current = "";
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usbPath]);

  const pollMs = 500;

  const detectUsb = async () => {
    setState("reading");
    try {
      const res = await axios.get(`${API}/api/detect_usb`, {
        params: { path: "/media/*/*", scan_media: true, need_files: false },
        timeout: 6000,
      });
      if (res.data?.found && res.data?.preferred) {
        setUsbPath(res.data.preferred);
        setErrorDetails("");
        setState("success");
      } else {
        setUsbPath("");
        setErrorDetails(JSON.stringify(res.data?.checked ?? [], null, 2));
        setState("error");
      }
    } catch (e: any) {
      setUsbPath("");
      setErrorDetails(String(e?.message || e));
      setState("error");
    }
  };

  const findAndProbeIfc = async (root: string): Promise<string> => {
    const q = await axios.get(`${API}/api/find_ifc_quick`, { params: { root }, timeout: 1500 }).catch(() => null);
    let path = q?.data?.ok ? q?.data?.match : undefined;

    if (!path) {
      const f1 = await axios.get(`${API}/api/find_ifc_fast`, { params: { root, max_depth: 3, timeout_ms: 1200 }, timeout: 3000 }).catch(() => null);
      path = f1?.data?.ok ? f1?.data?.match : undefined;
    }
    if (!path) {
      const f2 = await axios.get(`${API}/api/find_ifc_fast`, { params: { root, max_depth: 8, timeout_ms: 2500 }, timeout: 4000 }).catch(() => null);
      path = f2?.data?.ok ? f2?.data?.match : undefined;
    }
    if (!path) throw new Error("No IFC found. Put an IFC at USB root or inside IFC/, models/, export/.");

    const probe = await axios.get(`${API}/api/ifc_probe`, { params: { path }, timeout: 2000 }).catch(() => null);
    if (!probe?.data?.ok) throw new Error(`Probe failed for ${path}: ${probe?.data?.reason || "unreadable file"}`);

    return path;
  };

  const validateSelection = async () => {
    try {
      if (!usbPath) throw new Error("No USB path selected.");
      if (!selectedModel) throw new Error("Please choose a model (4 or 6 walls).");

      setIsChecking(true);
      setResponseMessage("🔎 Checking selection against IFC…");
      setErrorDetails("");

      const path = ifcPath ?? (await findAndProbeIfc(usbPath));
      setIfcPath(path);

      const fd = new FormData();
      fd.append("usb_path", usbPath);
      fd.append("ifc_path", path);
      fd.append("model_sides", String(selectedModel));

      const res = await axios.post(`${API}/api/checkifc`, fd, { timeout: 0 });

      if (res.data?.ok) {
        setIsValidated(true);
        setState("checked_ok");
        setResponseMessage(`✅ Selection is valid${res.data.model ? ` (model: ${res.data.model})` : ""}. You can now Launch UI.`);
        setErrorDetails("");
      } else {
        throw new Error("Backend did not confirm selection");
      }
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "unknown error";

      setIsValidated(false);
      setResponseMessage(`❌ ${detail}`);
      setErrorDetails(
        typeof err?.response?.data === "object" ? JSON.stringify(err.response.data, null, 2) : String(detail)
      );

      if (status === 400) setState("invalid_model");
      else setState("success");
    } finally {
      setIsChecking(false);
    }
  };
 
  
  const launchUI = async () => {
    if (!(isValidated && state === "checked_ok") || !ifcPath || !usbPath) {
      setResponseMessage("❌ Please validate the selection first.");
      setErrorDetails("Missing validation or paths");
      return;
    }
    try {
      setState("launching");
      const fd = new FormData();
      fd.append("usb_path", usbPath);
      fd.append("ifc_path", ifcPath);
      const res = await axios.post(`${API}/api/launch_ui`, fd, { timeout: 20000 });

      const pid = Number(res.data?.pid ?? 0);
      if (pid > 0) setUiPid(pid);
      sessionStorage.setItem("uiPoll", "1");
      setShouldPoll(true);
      setResponseMessage(`✅ Automated PBU Robot UI: ${res.data.message ?? "started"}`);
      setErrorDetails("");
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || "unknown error";
      setState("error");
      setResponseMessage(`❌ Failed to launch: ${detail}`);
      setErrorDetails(JSON.stringify(err?.response?.data ?? { message: detail }, null, 2));
    }
  };
  useEffect(() => {
    if (!shouldPoll) return;
    let cancelled = false;
    const check = async () => {
      try {
        const params = uiPid ? { params: { pid: uiPid } } : undefined;
        const r = await axios.get(`${API}/api/ui_status`, params as any);
        const running = !!r.data?.running;
        setLastPollAt(new Date().toLocaleTimeString());
        setLastRunning(String(running));
        setLastError("");
        if (!running && !cancelled) {
          sessionStorage.removeItem("uiPoll");
          setShouldPoll(false);
          setUiPid(null);
          setClosedMessage("");
          setResponseMessage("");
          setState("shutdown");
        }
      } catch (e: any) {
        setLastPollAt(new Date().toLocaleTimeString());
        setLastRunning("n/a");
        setLastError(e?.message ?? String(e));
        console.warn("ui_status poll failed:", e);
      }
    };
    check();
    const id = setInterval(check, pollMs);
    return () => { cancelled = true; clearInterval(id); };
  }, [shouldPoll, uiPid, API]);
  const canShowPicker = state === "success" || state === "invalid_model" || state === "checked_ok";
  const canLaunch = isValidated && !!usbPath && !!ifcPath && state === "checked_ok";
  const [progressPct, setProgressPct] = useState<number | null>(null);

// --- add this effect to run when we enter 'shutdown' ---
// show % on shutdown
useEffect(() => {
  if (state !== "shutdown" || !usbPath) return;
  (async () => {
    const r = await axios.get(`${API}/api/progress`, { params: { usb_path: usbPath } });
    if (r.data?.ok) setProgressPct(r.data.percent);
  })();
}, [state, usbPath, API]);

// open Excel (view-only, no PDF)
const openExcelViewOnly = async () => {
  await axios.post(`${API}/api/open_excel`, { usb_path: usbPath });
};


  // UI (balanced braces/parens)
  return (
    <div className="hero min-h-screen relative bg-cover bg-center" style={{ backgroundImage: `url("${bgDataUri}")` }}>
      <div className={`hero-overlay ${state === "reading" || state === "launching" ? "bg-neutral/60" : "bg-neutral/40"}`} />
      <div className="hero-content text-neutral-content text-center relative">
        <div className="max-w-2xl space-y-5">
          <h1 className="text-4xl md:text-5xl font-bold">{v.title}</h1>
          {state === "shutdown" ? (
            <p className="opacity-90">
              The operation is completed successfully.<br />
              {progressPct !== null ? <>Completed: <span className="font-semibold">{progressPct}%</span></> : "Checking completion…"}
            </p>
          ) : (
            <p className="opacity-90">{v.message}</p>
          )}


          {(responseMessage || errorDetails) && (
            <div className="mt-2">
              <p className="text-sm opacity-90" aria-live="polite">
                {responseMessage}
              </p>
              {errorDetails && (
                <pre className="text-left text-xs bg-base-200/60 p-3 rounded overflow-auto max-h-40 mt-2">
                  {errorDetails}
                </pre>
              )}
            </div>
          )}

          {canShowPicker && (
            <>
              <ModelSelection value={selectedModel} onChange={setSelectedModel} />

              {state === "invalid_model" && (
                <p className="text-sm text-red-300">
                  Wrong model type detected for this IFC. Adjust your selection and try again.
                </p>
              )}

              <div className="flex gap-3 justify-center mt-2">
                <button
                  className="btn btn-outline"
                  onClick={validateSelection}
                  disabled={isChecking || !usbPath || !selectedModel}
                >
                  {isChecking ? (
                    <>
                      <span className="loading loading-spinner loading-xs mr-2" />
                      Checking…
                    </>
                  ) : (
                    "Check selection"
                  )}
                </button>

                <button className="btn btn-primary" onClick={launchUI} disabled={isChecking || !canLaunch}>
                  Launch UI
                </button>
              </div>

              {!isChecking && !canLaunch && (
                <p className="text-xs opacity-80 mt-1">
                  Select a model and click <span className="font-semibold">Check selection</span> to enable Launch UI.
                </p>
              )}
            </>
          )}
          {/* NEW: shutdown actions */}
          {state === "shutdown" && (
            <div className="flex gap-3 justify-center mt-3">
              <button className="btn btn-outline" onClick={openExcelViewOnly}>
                Open Excel (view-only)
              </button>
            </div>
          )}
          {/*{state === "checked_ok" && (
            <RobotIPInput onConnect={handleRobotConnect} />
          )}*/}
          {state === "robot_connected" && (
            <div>
              <div className="card bg-base-100 w-96 shadow-sm">
                <div className="card-body">
                  <h2 className="card-title text-black">Is the ABB Robot in HOME position?</h2>
                  <p className="text-black">Please verify that the ABB robot is in the HOME position as illustrated in the photo below.</p>
                </div>
                <figure>
                  <img
                    src={ABBHOMEImage}
                    alt="ABB Robot HOME position" />
                </figure>
              </div>
              <div className="divider" />
              <button
                className={`btn btn-${v.variant} md:btn-md lg:btn-lg`}
                onClick={verifyHomePosition}
              >
                {v.primaryText}
              </button>
            </div>
          )}
          {!canShowPicker && state !== "shutdown" && state !== "robot_connected" && (
            <div>
              <button
                className={`btn btn-${v.variant} md:btn-md lg:btn-lg`}
                onClick={detectUsb}
                disabled={state === "launching"}
              >
                {v.primaryText}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
