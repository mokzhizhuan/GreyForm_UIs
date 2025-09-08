import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";

// Background hero image (inline SVG -> data URI)
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
  waiting: {
    title: "Please insert a USB drive to continue",
    message: "Click Start to detect a USB drive (e.g. /mnt/usb).",
    variant: "primary",
    primaryText: "Start",
    showSpinner: false,
  },
  reading: {
    title: "Reading USB drive...",
    message: "Please wait while we read the contents of the USB drive.",
    variant: "info",
    primaryText: "Cancel",
    showSpinner: true,
  },
  success: {
    title: "USB drive detected",
    message: "Press Continue to launch the UI.",
    variant: "success",
    primaryText: "Continue",
    showSpinner: false,
  },
  error: {
    title: "Error reading USB drive",
    message: "We could not find a usable USB or matching files.",
    variant: "error",
    primaryText: "Try Again",
    showSpinner: false,
  },
  launching: {
    title: "Launching UI…",
    message: "Sending request to the backend.",
    variant: "info",
    primaryText: "Launching…",
    showSpinner: true,
  },
  shutdown: {
    title: "Please power off the machine",
    message: "The operation has completed successfully. You may now shut down the system.",
    variant: "neutral",
    primaryText: "",
    showSpinner: false,
  },
} as const satisfies Record<
  UsbState,
  {
    title: string;
    message: string;
    variant:
      | "primary"
      | "secondary"
      | "accent"
      | "info"
      | "success"
      | "warning"
      | "error"
      | "neutral";
    primaryText: string;
    showSpinner?: boolean;
  }
>;

export default function Status() {
  const [state, setState] = useState<UsbState>("waiting");
  const v = views[state];

  const API = useMemo(
    () => import.meta.env.VITE_API_URL ?? "http://localhost:8000",
    []
  );

  const [usbPath, setUsbPath] = useState<string>("");
  const [uiPid, setUiPid] = useState<number | null>(null);
  const [responseMessage, setResponseMessage] = useState("Ready");
  const [closedMessage, setClosedMessage] = useState("");
  const [errorDetails, setErrorDetails] = useState("");

  const pollMs = 2000;

  const detectUsb = async () => {
    setState("reading");
    try {
      const res = await axios.get(`${API}/api/detect_usb`, {
        params: { path: "/mnt/usb", scan_media: false },
      });

      if (res.data?.found && res.data?.preferred) {
        setUsbPath(res.data.preferred as string);
        setErrorDetails("");
        setState("success");
      } else {
        setUsbPath("");
        setErrorDetails(JSON.stringify(res.data?.checked ?? [], null, 2));
        setState("error");
      }
    } catch (e) {
      console.error("USB detect failed:", e);
      setUsbPath("");
      setErrorDetails(String(e));
      setState("error");
    }
  };

  const launchUI = async () => {
    if (!usbPath) {
      setState("error");
      return;
    }
    setState("launching");
    try {
      const formData = new FormData();
      formData.append("usb_path", usbPath);

      const res = await axios.post(`${API}/api/launch_ui`, formData);
      const pid = Number(res.data?.pid ?? 0);
      if (pid > 0) setUiPid(pid);


      setResponseMessage(
        `✅ Automated PBU Robot UI: ${res.data.message ?? "started"}\nPath: ${usbPath}`
      );
      setClosedMessage(""); // not closed yet—we’ll detect it
      setState("success");  // remain here until process ends
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || "unknown error";
      console.error("Launch failed:", detail);
      setResponseMessage(`❌ Failed to launch: ${detail}`);
      setState("error");
    }
  };

  // Poll the backend to know when the UI process exits
    useEffect(() => {
    if (!uiPid) return;
    let cancelled = false;
    const interval = setInterval(async () => {
      try {
        const r = await axios.get(`${API}/api/ui_status`, { params: { pid: uiPid } });
        const running = !!r.data?.running;
        if (!running && !cancelled) {
          setClosedMessage("");
          setResponseMessage("Please power off the machine.");
          setState("shutdown");
          clearInterval(interval);
        }
      } catch (e) {
        console.warn("ui_status poll failed:", e);
      }
    }, 2000);
    return () => { cancelled = true; clearInterval(interval); };
  }, [uiPid, API]);
  
  const handlePrimary = () => {
    switch (state) {
      case "waiting":
        detectUsb();
        break;
      case "reading":
        setState("waiting");
        break;
      case "success":
        launchUI();
        break;
      case "error":
        detectUsb();
        break;
      case "launching":
      case "shutdown":
        // no-op
        break;
    }
  };

  return (
    <>
      <div
        className="hero min-h-screen relative bg-cover bg-center"
        style={{ backgroundImage: `url("${bgDataUri}")` }}
      >
        <div
          className={`hero-overlay ${
            state === "reading" || state === "launching"
              ? "bg-neutral/60"
              : "bg-neutral/40"
          }`}
        />
        <div className="hero-content text-neutral-content text-center relative">
          <div className="max-w-md space-y-5">
            <h1 className="text-4xl md:text-5xl font-bold">{v.title}</h1>
            <p>{v.message}</p>

            {v.showSpinner ? (
              <span className="loading loading-spinner loading-md" aria-label="Loading" />
            ) : null}

            {/* Show which path was detected, if any */}
            {usbPath && state !== "waiting" && (
              <div className="badge badge-outline font-mono">{usbPath}</div>
            )}

            {/* Primary button (hidden in shutdown state) */}
            {state !== "shutdown" && (
              <div>
                <button
                  className={`btn btn-${v.variant} md:btn-md lg:btn-lg`}
                  onClick={handlePrimary}
                  disabled={state === "launching"}
                >
                  {v.primaryText}
                </button>
              </div>
            )}

            {/* Error details (helpful for debugging) */}
            {state === "error" && errorDetails && (
              <pre className="text-left text-xs bg-base-200 p-3 rounded overflow-auto max-h-64">
                {errorDetails}
              </pre>
            )}
          </div>
        </div>
      </div>

      {/* Status messages below the hero */}
      <div className="p-6 space-y-3">
        <div className="alert alert-info whitespace-pre-line">
          {responseMessage}
        </div>
        {closedMessage && (
          <div className="alert alert-warning whitespace-pre-line">
            {closedMessage}
          </div>
        )}
      </div>
    </>
  );
}
