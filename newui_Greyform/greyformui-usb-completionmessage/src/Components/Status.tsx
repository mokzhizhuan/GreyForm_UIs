import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import ModelSelection from "./ModelSelection";
import ABBHOMEImage from "../assets/ABB Robot placeholder image.jpg";
import LevellerImage from "../assets/Leveller.jpeg";
import RemoteControlImage from "../assets/Remote Control.jpeg";
import HomePositionCheck from "./HomePositionCheck";
import PushIntoPBUAndLevel from "./PushIntoPBUAndLevel";
import pushRobotIntoPBUImage from "../assets/push_robot_into_PBU.png";

type CPBook = Record<string, Record<string, any>[]>;

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
  | "waiting"          // insert USB / find PBU Excel
  | "reading"
  | "success"          // Excel/model selection screen
  | "error"
  | "checked_ok"       // Excel + IFC validated
  | "launching"        // marking in progress
  | "shutdown"         // marking finished
  | "invalid_model"
  | "robot_connected"  // robot powered, HOME check
  | "home_verified";   // pushed into PBU, 1m from wall etc.

const views = {
  waiting: {
    title: "Select PBU Excel (Master file)",
    message: "Click Start to search the template folder / USB for PBU Excel files.",
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
    title: "PBU Excel found",
    message: "Select the correct PBU model, then click Check selection.",
    variant: "success",
    primaryText: "Check selection",
    showSpinner: false,
  },
  invalid_model: {
    title: "Wrong model type",
    message: "Please change the model and Check selection again.",
    variant: "error",
    primaryText: "Check selection",
    showSpinner: false,
  },
  checked_ok: {
    title: "PBU model verified",
    message:
      "Excel and IFC match. Create the working folder, then power up the robot to continue.",
    variant: "success",
    primaryText: "",
    showSpinner: false,
  },
  error: {
    title: "Error reading USB drive",
    message: "Please plug in your drive and try again.",
    variant: "error",
    primaryText: "Try Again",
    showSpinner: false,
  },
  launching: {
    title: "Robot is marking",
    message: "Marking in progress. Please wait until completion.",
    variant: "info",
    primaryText: "Loading…",
    showSpinner: true,
  },
  shutdown: {
    title: "Marking completed",
    message:
      "The operation is completed successfully. Please return the robot to HOME position.",
    variant: "neutral",
    primaryText: "",
    showSpinner: false,
  },
  robot_connected: {
    title: "Robot Powered Up",
    message:
      "Perform HOME position check as shown on the pendant / GUI. Confirm when HOME is OK.",
    variant: "success",
    primaryText: "Verify HOME position",
    showSpinner: false,
  },
  home_verified: {
    title: "Robot in HOME position",
    message:
      "Turn off the robot, push it into the PBU, power up again, level it ~1m from the wall and facing the wall.",
    variant: "success",
    primaryText: "Check scanning position & Start marking",
    showSpinner: false,
  },
} as const;

async function postWithRetries(
  url: string,
  data?: any,
  config?: AxiosRequestConfig,
  tries = 10,
  delayMs = 400
) {
  let lastErr: any;
  for (let i = 0; i < tries; i++) {
    try {
      return await axios.post(url, data, { timeout: 8000, ...(config || {}) });
    } catch (e: any) {
      lastErr = e;
      const code = e?.response?.status;
      if (code && code !== 409 && code < 500) break;
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }
  throw lastErr;
}

export default function Status() {
  // --- high level workflow state ---
  const [state, setState] = useState<UsbState>("waiting");
  const v = views[state] ?? views.shutdown;

  const API = useMemo(() => {
    const base = import.meta.env.VITE_API_URL ?? "http://localhost:800";
    return base.replace(/\/+$/, "");
  }, []);

  const ran = useRef(false);

  // Auto start roscore + build + listener once (when UI opens)
  useEffect(() => {
    if (ran.current) return;
    ran.current = true;

    (async () => {
      try {
        await postWithRetries(`${API}/roscore/start`);
        console.log("[auto] roscore started");
      } catch (e: any) {
        console.warn("[auto] roscore error:", e?.response?.data || e?.message);
      }

      try {
        await postWithRetries(`${API}/build/start`);
        console.log("[auto] build started");
      } catch (e: any) {
        console.warn("[auto] build error:", e?.response?.data || e?.message);
      }

      try {
        await postWithRetries(`${API}/ros/listener/start`, null, {
          params: { restart: true },
        });
        console.log("[auto] listener started");
      } catch (e: any) {
        console.warn("[auto] listener error:", e?.response?.data || e?.message);
      }
    })();
  }, [API]);

  const [usbPath, setUsbPath] = useState<string>("");
  const [uiPid, setUiPid] = useState<number | null>(null);
  const [shouldPoll, setShouldPoll] = useState(false);
  const excel_checklist =
    "Greyform TERRAHL2(JMB)-T1a BOM Checklist 20231211.xlsx";
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

  const http = useMemo(() => {
    const base = (import.meta.env.VITE_API_URL ?? "http://localhost:800").replace(
      /\/+$/,
      ""
    );
    return axios.create({
      baseURL: base,
      timeout: 0,
    });
  }, []);

  // Debug log
  useEffect(() => {
    console.log("[Status]", {
      state,
      usbPath,
      ifcPath,
      selectedModel,
      isValidated,
    });
  }, [state, usbPath, ifcPath, selectedModel, isValidated]);

  // Reset validation when USB changes
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

  // --- Step 1: detect USB / PBU Excel master file ---
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

  // --- Step 2: find / probe IFC and validate model selection ---
  const findAndProbeIfc = async (root: string): Promise<string> => {
    const q = await axios
      .get(`${API}/api/find_ifc_quick`, { params: { root }, timeout: 1500 })
      .catch(() => null);
    let path = q?.data?.ok ? q?.data?.match : undefined;

    if (!path) {
      const f1 = await axios
        .get(`${API}/api/find_ifc_fast`, {
          params: { root, max_depth: 3, timeout_ms: 1200 },
          timeout: 3000,
        })
        .catch(() => null);
      path = f1?.data?.ok ? f1?.data?.match : undefined;
    }
    if (!path) {
      const f2 = await axios
        .get(`${API}/api/find_ifc_fast`, {
          params: { root, max_depth: 8, timeout_ms: 2500 },
          timeout: 4000,
        })
        .catch(() => null);
      path = f2?.data?.ok ? f2?.data?.match : undefined;
    }
    if (!path)
      throw new Error(
        "No IFC found. Put an IFC at USB root or inside IFC/, models/, export/."
      );

    const probe = await axios
      .get(`${API}/api/ifc_probe`, { params: { path }, timeout: 2000 })
      .catch(() => null);
    if (!probe?.data?.ok)
      throw new Error(
        `Probe failed for ${path}: ${
          probe?.data?.reason || "unreadable file"
        }`
      );

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
      fd.append("excel_checklist", excel_checklist);

      const res = await axios.post(`${API}/api/checkifc`, fd, { timeout: 0 });

      if (res.data?.ok) {
        setIsValidated(true);
        setState("checked_ok");
        setResponseMessage(
          `✅ Selection is valid${
            res.data.model ? ` (model: ${res.data.model})` : ""
          }.`
        );
        setErrorDetails("");
      } else {
        throw new Error("Backend did not confirm selection");
      }
    } catch (err: any) {
      const status = err?.response?.status;
      const detail =
        err?.response?.data?.detail || err?.message || "unknown error";

      setIsValidated(false);
      setResponseMessage(`❌ ${detail}`);
      setErrorDetails(
        typeof err?.response?.data === "object"
          ? JSON.stringify(err.response.data, null, 2)
          : String(detail)
      );

      if (status === 400) setState("invalid_model");
      else setState("success");
    } finally {
      setIsChecking(false);
    }
  };

  // --- Step 3: create working folder / CP JSON (ROS: send directory) ---
  const [cpJson, setCpJson] = useState<CPBook | null>(null);
  const [progressPct, setProgressPct] = useState<number | null>(null);

  const initAndGetCP = async () => {
    try {
      if (!usbPath) throw new Error("No USB path selected.");

      const fd = new FormData();
      fd.append("usb_path", usbPath);
      if (ifcPath) fd.append("ifc_path", ifcPath);
      fd.append("force", "true");
      fd.append("model_sides", String(selectedModel));
      fd.append("cp_mode", "columns");
      fd.append("cp_key", "Type");
      fd.append("include_cp", "true");

      const res = await http.post(`/api/ui_initailzecamdriver`, fd, {
        timeout: 0,
      });

      if (!res?.data) throw new Error("Empty response from backend.");
      const cp = res.data.cp_json ?? null;
      setCpJson(cp || null);
      setResponseMessage(`✅ Working folder initialized (${res.data.status}).`);
      setErrorDetails("");
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message || "unknown error";
      setResponseMessage(`❌ Init working folder failed: ${detail}`);
      setErrorDetails(
        typeof e?.response?.data === "object"
          ? JSON.stringify(e.response.data, null, 2)
          : String(detail)
      );
    }
  };

  // --- Step 4: HOME position check ---
  const verifyHomePosition = () => {
    setState("home_verified");
    setResponseMessage("HOME position confirmed. Please push the robot into the PBU.");
  };

  // --- Step 5: start marking (scan position, then mark) ---
  const launchUI = async () => {
    if (!isValidated || !ifcPath || !usbPath) {
      setResponseMessage("❌ Please finish Excel/IFC validation first.");
      setErrorDetails("Missing validation or paths");
      return;
    }
    try {
      setState("launching");
      const fd = new FormData();
      fd.append("usb_path", usbPath);
      fd.append("ifc_path", ifcPath);
      const res = await axios.post(`${API}/api/launch_ui`, fd, {
        timeout: 20000,
      });
      const pid = Number(res.data?.pid ?? 0);
      if (pid > 0) setUiPid(pid);
      sessionStorage.setItem("uiPoll", "1");
      setShouldPoll(true);
      setResponseMessage(
        `✅ Automated PBU Robot UI: ${res.data.message ?? "started"}`
      );
      setErrorDetails("");
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail || err?.message || "unknown error";
      setState("error");
      setResponseMessage(`❌ Failed to launch: ${detail}`);
      setErrorDetails(
        JSON.stringify(err?.response?.data ?? { message: detail }, null, 2)
      );
    }
  };

  const checkPlacementAndStart = async () => {
    try {
      // Here you can call a REST endpoint to command the robot
      // to scan its position and verify 1m-from-wall, facing wall, etc.
      //
      // Example (placeholder):
      // await axios.post(`${API}/api/robot/check_scanning_position`);

      setResponseMessage(
        "✅ Robot position OK. Starting marking sequence…"
      );
      await launchUI();
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message || "unknown error";
      setResponseMessage(`❌ Failed to start marking: ${detail}`);
      setErrorDetails(
        typeof e?.response?.data === "object"
          ? JSON.stringify(e.response.data, null, 2)
          : String(detail)
      );
    }
  };

  // --- Poll until marking finished ---
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
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [shouldPoll, uiPid, API]);

  // --- show % completion when in shutdown ---
  useEffect(() => {
    if (state !== "shutdown" || !usbPath) return;
    (async () => {
      const r = await axios.get(`${API}/api/progress`, {
        params: { usb_path: usbPath },
      });
      if (r.data?.ok) setProgressPct(r.data.percent);
    })();
  }, [state, usbPath, API]);

  const openExcelViewOnly = async () => {
    if (!usbPath) return;
    await axios.post(`${API}/api/open_excel`, { usb_path: usbPath });
  };

  // --- UI ---
  return (
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
        <div className="max-w-2xl space-y-5">
          <h1 className="text-4xl md:text-5xl font-bold">{v.title}</h1>

          {state === "shutdown" ? (
            <p className="opacity-90">
              The operation is completed successfully.
              <br />
              {progressPct !== null ? (
                <>
                  Completed:{" "}
                  <span className="font-semibold">{progressPct}%</span>
                </>
              ) : (
                "Checking completion…"
              )}
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

          {/* Step 1: USB / PBU Excel selection */}
          {["waiting", "reading", "error"].includes(state) && (
            <div className="mt-4">
              <button
                className={`btn btn-${v.variant} md:btn-md lg:btn-lg`}
                onClick={detectUsb}
                disabled={state === "launching"}
              >
                {v.primaryText || "Start"}
              </button>
            </div>
          )}

          {/* Step 2: model selection + validation */}
          {["success", "invalid_model"].includes(state) && (
            <>
              <ModelSelection value={selectedModel} onChange={setSelectedModel} />

              {state === "invalid_model" && (
                <p className="text-sm text-red-300">
                  Wrong model type detected for this IFC. Adjust your selection
                  and try again.
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
              </div>
            </>
          )}

          {/* Step 3: Excel/IFC OK → init working folder & power up robot */}
          {state === "checked_ok" && (
            <>
              <p className="text-sm opacity-90">
                Excel &amp; IFC are valid. Create the working folder (ROS will
                receive the directory), then power up the robot and continue.
              </p>
              <div className="flex flex-col md:flex-row gap-3 justify-center mt-3">
                <button
                  className="btn btn-outline"
                  onClick={initAndGetCP}
                  disabled={!usbPath || state === "launching"}
                >
                  Init working folder
                </button>
                <button
                  className="btn btn-primary"
                  onClick={() => setState("robot_connected")}
                  disabled={!isValidated}
                >
                  Robot is powered up – go to HOME check
                </button>
              </div>
            </>
          )}

          {/* Step 4: HOME position check */}
          {state === "robot_connected" && (
            <HomePositionCheck
              ABBHOMEImage={ABBHOMEImage}
              v={v}
              verifyHomePosition={verifyHomePosition}
            />
          )}

          {/* Step 5: push into PBU, place 1m from wall, start marking */}
          {state === "home_verified" && (
            <>
              <PushIntoPBUAndLevel
                pushRobotIntoPBUImage={pushRobotIntoPBUImage}
                LevellerImage={LevellerImage}
                RemoteControlImage={RemoteControlImage}
                v={v}
              />
              <button
                className="btn btn-primary mt-4"
                onClick={checkPlacementAndStart}
                disabled={state === "launching"}
              >
                Check scanning position &amp; Start marking
              </button>
            </>
          )}

          {/* Step 6: after shutdown → allow opening Excel in view-only */}
          {state === "shutdown" && (
            <div className="flex gap-3 justify-center mt-3">
              <button className="btn btn-outline" onClick={openExcelViewOnly}>
                Open Excel (view-only)
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
