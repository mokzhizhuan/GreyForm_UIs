import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";

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
type UsbState = "waiting" | "reading" | "success" | "error" | "launching" | "shutdown";
const views = {
  waiting: { title: "Please insert a USB drive to continue", message: "Click Start to detect a USB drive.", variant: "primary", primaryText: "Start", showSpinner: false },
  reading: { title: "Reading USB drive...", message: "Please wait while we read the contents of the USB drive.", variant: "info", primaryText: "Cancel", showSpinner: true },
  success: { title: "USB drive detected", message: "Press Continue to launch the UI.", variant: "success", primaryText: "Continue", showSpinner: false },
  error:   { title: "Error reading USB drive", message: "Please plug in your drive", variant: "error", primaryText: "Try Again", showSpinner: false },
  launching:{ title: "Launching UI…", message: "Sending request to the backend.", variant: "info", primaryText: "Launching…", showSpinner: true },
  shutdown:{ title: "Please power off the machine", message: "The operation is completed successfully", variant: "neutral", primaryText: "", showSpinner: false },
} as const;
export default function Status() {
  const [state, setState] = useState<UsbState>("waiting");
  const v = views[state] ?? views.shutdown;
  const [shouldPoll, setShouldPoll] = useState(false);
  const API = useMemo(() => {
    const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
    return base.replace(/\/+$/, "");
  }, []);
  const [usbPath, setUsbPath] = useState<string>("");
  const [uiPid, setUiPid] = useState<number | null>(null);
  const [responseMessage, setResponseMessage] = useState("Ready");
  const [closedMessage, setClosedMessage] = useState("");
  const [errorDetails, setErrorDetails] = useState("");
  const [lastPollAt, setLastPollAt] = useState<string>("");
  const [lastRunning, setLastRunning] = useState<string>("");
  const [lastError, setLastError] = useState<string>("");
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
  const launchUI = async () => {
    if (!usbPath) {
      const msg = "❌ No USB path selected.";
      setResponseMessage(msg);
      setErrorDetails(msg);
      setState("error");
      return;
    }
    setState("launching");
    let ifcPath: string | undefined;
    try {
      const q = await axios.get(`${API}/api/find_ifc_quick`, {
        params: { root: usbPath },
        timeout: 1500,
      }).catch(() => null);
      ifcPath = q?.data?.ok ? q?.data?.match : undefined;
      if (!ifcPath) {
        const f1 = await axios.get(`${API}/api/find_ifc_fast`, {
          params: { root: usbPath, max_depth: 3, timeout_ms: 1200 },
          timeout: 3000,
        }).catch(() => null);
        ifcPath = f1?.data?.ok ? f1?.data?.match : undefined;
      }
      if (!ifcPath) {
        const f2 = await axios.get(`${API}/api/find_ifc_fast`, {
          params: { root: usbPath, max_depth: 8, timeout_ms: 2500 },
          timeout: 4000,
        }).catch(() => null);
        ifcPath = f2?.data?.ok ? f2?.data?.match : undefined;
      }
      if (!ifcPath) {
        const msg = "❌ No IFC found. Put an IFC at USB root or inside IFC/, models/, export/.";
        setResponseMessage(msg);
        setErrorDetails(msg);
        setState("error");
        return;
      }
      const probe = await axios.get(`${API}/api/ifc_probe`, {
        params: { path: ifcPath },
        timeout: 2000,
      }).catch(() => null);
      if (!probe?.data?.ok) {
        const msg = `❌ Probe failed for ${ifcPath}: ${probe?.data?.reason || "unreadable file"}`;
        setResponseMessage(msg);
        setErrorDetails(JSON.stringify(probe?.data ?? {}, null, 2));
        setState("error");
        return;
      }
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
      setClosedMessage("");
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "unknown error";
      if (status === 409 && /relaunch is locked/i.test(detail)) {
        try {
          await axios.post(`${API}/api/reset_lock`);
          const fd = new FormData();
          fd.append("usb_path", usbPath);
          fd.append("ifc_path", ifcPath!);
          const res = await axios.post(`${API}/api/launch_ui`, fd, { timeout: 20000 });
          const pid = Number(res.data?.pid ?? 0);
          if (pid > 0) setUiPid(pid);
          sessionStorage.setItem("uiPoll", "1");
          setShouldPoll(true);
          setResponseMessage(`✅ Automated PBU Robot UI: ${res.data.message ?? "started"}`);
          setErrorDetails("");
          return;
        } catch {
        }
      }
      setResponseMessage(`❌ Failed to launch: ${detail}`);
      setErrorDetails(JSON.stringify(err?.response?.data ?? { message: detail }, null, 2));
      setState("error");
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
  const handlePrimary = () => {
    switch (state) {
      case "waiting":  detectUsb(); break;
      case "reading":  setState("waiting"); break;
      case "success":  launchUI(); break;
      case "error":    detectUsb(); break;
      case "launching":
      case "shutdown": break;
    }
  };
  return (
    <>
      <div className="hero min-h-screen relative bg-cover bg-center" style={{ backgroundImage: `url("${bgDataUri}")` }}>
        <div className={`hero-overlay ${state === "reading" || state === "launching" ? "bg-neutral/60" : "bg-neutral/40"}`} />
        <div className="hero-content text-neutral-content text-center relative">
          <div className="max-w-md space-y-5">
            <h1 className="text-4xl md:text-5xl font-bold">{v.title}</h1>
            <p>{v.message}</p>
            {v.showSpinner ? <span className="loading loading-spinner loading-md" aria-label="Loading" /> : null}
            {state !== "shutdown" && (
              <div>
                <button className={`btn btn-${v.variant} md:btn-md lg:btn-lg`} onClick={handlePrimary} disabled={state === "launching"}>
                  {v.primaryText}
                </button>
              </div>
            )}
            {/*{state === "error" && responseMessage && <p className="text-sm opacity-80">{responseMessage}</p>}
            {state === "error" && errorDetails && (
              <pre className="text-left text-xs bg-base-200 p-3 rounded overflow-auto max-h-64">
                {errorDetails}
              </pre>
            )}*/}
          </div>
        </div>
      </div>
    </>
  );
}
