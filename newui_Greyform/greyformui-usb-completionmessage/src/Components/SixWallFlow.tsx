// =========================================================
// SixWallFlow.tsx (UI-STABLE / FRONTEND-ONLY FIX)
// - HomeCheck table is backend-driven (status.homeCheckOutput)
// - Retry/Continue are stable (action lock + no UI clearing fights poll)
// - Poll never overlaps; no stale updates; no hidden table issues
// =========================================================

import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

import placementOne from "../assets/six_wall_flow/6_wall_flow_placement1.jpg";
import placementTwo from "../assets/six_wall_flow/6_wall_flow_placement2.jpg";
import wallMarking1 from "../assets/six_wall_flow/6_wall_flow_placement1_1.png";
import wallMarking2 from "../assets/six_wall_flow/6_wall_flow_placement2_1.png";
import manToAuto1 from "../assets/Manual_to_auto_1.png";
import manToAuto2 from "../assets/Manual_to_auto_2.png";
import manToAuto3 from "../assets/Manual_to_auto_3.png";
import manToAuto4 from "../assets/Manual_to_auto_4.png";
import manToAuto5 from "../assets/Manual_to_auto_5().png";
import manToAuto6 from "../assets/Manual_to_auto_6.png";
import emergencyStop from "../assets/flex_pendant_emergency_stop.png";

import { API_BASE_URL } from "./config";

// --------------------------------------------------------
// TYPES
// --------------------------------------------------------
interface WallRow {
  [key: string]: any;
}

interface MarkingStatusResponse {
  running: boolean;
  paused: boolean;
  startedWall: number | null;
  doneWall: number | null;
  phase: number | null;
  hasError: boolean;
  errorSummary?: string | null;
  lastFailedWall?: number | null;
  homeCheckPending?: boolean;
  homeCheckWall?: number | null;
  homeCheckOutput?: string | null;
}

// --------------------------------------------------------
// CONSTANTS
// --------------------------------------------------------
const PHASE1_ORDER = ["wall_2", "wall_3", "wall_4"];
const PHASE2_ORDER = ["wall_5", "wall_6", "wall_1"];

const STEP_IMAGES = [
  placementOne, // 0
  wallMarking1, // 1
  wallMarking1, // 2
  wallMarking1, // 3
  placementTwo, // 4
  wallMarking2, // 5
  wallMarking2, // 6
  wallMarking2, // 7
  wallMarking2, // 8
];

const STEP_LABELS = [
  "Placement 1",
  "Wall 2",
  "Wall 3",
  "Wall 4",
  "Placement 2",
  "Wall 5",
  "Wall 6",
  "Wall 1",
  "Marking Complete",
];

// Auto Mode Instructions steps (overlay pages)
const AUTO_STEPS = [
  {
    title: "Control panel",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>At the top right corner of the screen, select the "..." button.</li>
          <li>Next, select Control.</li>
          <li>You should now see the control panel.</li>
        </ul>
        <img src={manToAuto1} width="600" alt="Manual to Auto Mode Overview" />
      </>
    ),
  },
  {
    title: "Selection of Auto button",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Select the "Auto" button.</li>
          <li>A prompt should now be displayed. Select the "Acknowledge" button.</li>
        </ul>
        <img src={manToAuto2} width="600" alt="Press on Auto button" />
      </>
    ),
  },
  {
    title: "Motors on",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Select the "Motors on" button.</li>
          <li>The "Motors on" button should now be highlighted in blue.</li>
        </ul>
        <img src={manToAuto3} width="600" alt="Press on Motor on button" />
      </>
    ),
  },
  {
    title: "Reset program (PP to main)",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Select the "Reset program (PP to main)" button.</li>
          <li>Select "Yes" when the acknowledgement prompt appears.</li>
        </ul>
        <img src={manToAuto4} width="650" alt="Press on Reset Program button" />
      </>
    ),
  },
  {
    title: "Press the Play Button",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Select the play button (right below "Reset PP to main")"</li>
          <li>You have to press the "Play" button</li>
        </ul>
        <img src={manToAuto5} width="250" alt="Press the Play button" />
      </>
    ),
  },
  {
    title: "Complete Auto mode Setup",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>You should now be seeing the screen below.</li>
        </ul>
        <img src={manToAuto6} width="600" alt="Manual to Auto Mode Overview" />
      </>
    ),
  },
  {
    title: "Safety Instructions",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Always keep the workspace clear while the robot operates.</li>
          <li>The operator should always be ready to hit the emergency stop switch in case of emergencies.</li>
        </ul>
        <img src={emergencyStop} width="600" alt="Emergency Stop Button" />
      </>
    ),
  },
];

// --------------------------------------------------------
// HELPERS
// --------------------------------------------------------
const wallToStep = (wall: number) => {
  switch (wall) {
    case 2:
      return 1;
    case 3:
      return 2;
    case 4:
      return 3;
    case 5:
      return 5;
    case 6:
      return 6;
    case 1:
      return 7;
    default:
      return 0;
  }
};
const buildExcelMap = (files: string[]) => {
  const map: Record<string, string> = {};
  for (const f of files) {
    const m = f.match(/_wall_(\d+)\.xlsx$/);
    if (m) map[`wall_${m[1]}`] = f;
  }
  return map;
};
const parseHomeCheck = (output: string) => {
  const lines = (output || "").split(/\r?\n/).map((l) => l.trim());
  const rax = lines.find((l) => l.includes("rax_1"));
  const tgt = lines.find((l) => l.includes("j0"));
  let current: any = {};
  let target: any = {};
  try {
    if (rax) current = JSON.parse(rax.replace(/'/g, '"'));
    if (tgt) target = JSON.parse(tgt.replace(/'/g, '"'));
  } catch {
    // ignore parse errors
  }
  return Object.entries(target).map(([k, v], i) => {
    const m = k.match(/^j(\d+)$/i);
    const idx = m ? parseInt(m[1], 10) : i;
    return {
      axis: `J${idx + 1}`,
      target: v,
      current: current[`rax_${idx + 1}`],
    };
  });
};
const isMarkingStep = (s: number) => [1, 2, 3, 5, 6, 7].includes(s);
// --------------------------------------------------------
// COMPONENT
// --------------------------------------------------------
const SixWallFlow: React.FC<any> = ({
  wallDetails,
  maxWall,
  excelFiles,
  meshfile,
  folderdirectory,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  // Canonical status snapshot (single source of truth in UI)
  const [status, setStatus] = useState<MarkingStatusResponse | null>(null);
  // Derived flags
  const running = !!status?.running;
  const paused = !!status?.paused;
  const hasError = !!status?.hasError;
  const homeCheckPending = !!status?.homeCheckPending;
  const homeCheckWall = status?.homeCheckWall ?? null;
  const homeCheckOutput = status?.homeCheckOutput ?? "";
  // Error targeting
  const [lastErrorWall, setLastErrorWall] = useState<number | null>(null);
  // UI messaging/logs
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [cmdLogs, setCmdLogs] = useState<string[]>([]);
  const logEndRef = useRef<HTMLDivElement | null>(null);
  // Action locking (prevents double-click / poll fights)
  const actionLockRef = useRef(false);
  const [actionBusy, setActionBusy] = useState(false);
  // Poll control (no overlap)
  const pollingTimerRef = useRef<number | null>(null);
  const pollInFlightRef = useRef(false);
  const aliveRef = useRef(true);
    // Overlay state for auto mode instructions (multi-step)
  const [showAutoInstr, setShowAutoInstr] = useState(false);
  const [autoStep, setAutoStep] = useState(0);
  const totalAutoSteps = AUTO_STEPS.length;
  // Prevent background scroll when overlay open
  useEffect(() => {
    if (showAutoInstr) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = prev;
      };
    }
  }, [showAutoInstr]);
  // Keyboard navigation when overlay is open
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (!showAutoInstr) return;
      if (e.key === "Escape") {
        setShowAutoInstr(false);
      } else if (e.key === "ArrowRight") {
        setAutoStep((s) => Math.min(s + 1, totalAutoSteps - 1));
      } else if (e.key === "ArrowLeft") {
        setAutoStep((s) => Math.max(s - 1, 0));
      } else if (e.key.toLowerCase() === "home") {
        setAutoStep(0);
      } else if (e.key.toLowerCase() === "end") {
        setAutoStep(totalAutoSteps - 1);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [showAutoInstr, totalAutoSteps]);
  // --------------------------------------------------------
  // NORMALIZATION
  // --------------------------------------------------------
  const normalized = useMemo(() => {
    const out: Record<string, WallRow[]> = {};
    for (const [k, v] of Object.entries(wallDetails || {})) {
      const m = k.match(/\d+/);
      out[`wall_${m ? m[0] : k}`] = v as any;
    }
    return out;
  }, [wallDetails]);
  const excelMap = useMemo(() => buildExcelMap(excelFiles || []), [excelFiles]);
  const getRows = (w: string) => normalized[w] ?? [];
  // --------------------------------------------------------
  // HOME CHECK TABLE (backend-driven; never stored in state)
  // --------------------------------------------------------
  const homeCheckRows = useMemo(() => {
    if (!homeCheckPending || homeCheckWall === null) return [];
    if (!homeCheckOutput) return [];
    return parseHomeCheck(homeCheckOutput);
  }, [homeCheckPending, homeCheckWall, homeCheckOutput]);
  const homeCheckPassed = useMemo(() => {
    if (!homeCheckPending || homeCheckWall === null) return null;
    if (!homeCheckOutput) return null;
    // your homeposcheck prints "True" in output
    return homeCheckOutput.split(/\r?\n/).some((l) => l.trim() === "True");
  }, [homeCheckPending, homeCheckWall, homeCheckOutput]);
  const extractFinalSummary = (logs: string[]) => {
  if (!logs || logs.length === 0) return null;
  // Prefer final ERROR
  for (let i = logs.length - 1; i >= 0; i--) {
    if (logs[i].startsWith("[ERROR]")) {
      return logs[i];
    }
  }
  // Otherwise final SUCCESS
  for (let i = logs.length - 1; i >= 0; i--) {
    if (logs[i].startsWith("[SUCCESS]")) {
      return logs[i];
    }
  }
  return null;
};
  // --------------------------------------------------------
  // AUTO SCROLL LOGS
  // --------------------------------------------------------
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [cmdLogs]);
const [forcedPlacement2, setForcedPlacement2] = useState(false);
  // --------------------------------------------------------
  // Small helper: safely lock actions
  // --------------------------------------------------------
  const withActionLock = async (fn: () => Promise<void>) => {
    if (actionLockRef.current) return;
    actionLockRef.current = true;
    setActionBusy(true);
    try {
      await fn();
    } finally {
      actionLockRef.current = false;
      setActionBusy(false);
    }
  };
  // --------------------------------------------------------
  // API: start phases
  // --------------------------------------------------------
  const startPhaseOne = async () =>
    withActionLock(async () => {
      setErrorMessage(null);
      setCmdLogs([]);
      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls: PHASE1_ORDER.map((w) => ({
          wall: w,
          rows: getRows(w),
          excel: excelMap[w] ?? "",
        })),
        meshfile,
        folder: folderdirectory,
        max_wall: maxWall,
        phase: 1,
      });
      // Kick the first homecheck via backend homecheck endpoint:
      await axios.post(`${API_BASE_URL}/marking/homecheck`, { target: "wall_2" });
      // No local state changes; poll will reflect backend state.
    });
  const startPhaseTwo = async () =>
  withActionLock(async () => {
    setForcedPlacement2(false); // 🔓 unlock Placement 2
    setErrorMessage(null);
    setCmdLogs([]);
    await axios.post(`${API_BASE_URL}/marking/start`, {
      walls: PHASE2_ORDER.map((w) => ({
        wall: w,
        rows: getRows(w),
        excel: excelMap[w] ?? "",
      })),
      meshfile,
      folder: folderdirectory,
      max_wall: maxWall,
      phase: 2,
    });
    await axios.post(`${API_BASE_URL}/marking/homecheck`, { target: "wall_5" });
  });
  // --------------------------------------------------------
  // ACTIONS
  // --------------------------------------------------------
  const pauseMarking = async () =>
    withActionLock(async () => {
      await axios.post(`${API_BASE_URL}/marking/pause`);
    });
  const retryCurrentWall = async () =>
    withActionLock(async () => {
      setErrorMessage(null);
      setCmdLogs([]);
      try {
        await axios.post(`${API_BASE_URL}/marking/retry`);
      } catch (e: any) {
        setErrorMessage(e?.response?.data?.detail || "Retry failed (backend error)");
        return;
      }
      // IMPORTANT: Do not run homecheck directly here unless you really want it.
      // If your backend requires it, you can keep it.
      // Most stable approach: backend sets homeCheckPending + homeCheckWall.
      // Poll will show it and operator can proceed.
      // If you want auto-trigger, uncomment:
      // const w = status?.homeCheckWall ?? status?.lastFailedWall ?? lastErrorWall;
      // if (w) await axios.post(`${API_BASE_URL}/marking/homecheck`, { target: `wall_${w}` });
    });
  const continueNextWall = async () =>
  withActionLock(async () => {
    // ------------------------------------------------------
    // PHASE 1 → PLACEMENT 2 (UI-controlled transition)
    // Allow if:
    // - phase 1
    // - UI currently on Wall 4 step (step 3)
    // - idle (not running, not homecheck pending)
    // This avoids relying on doneWall===4 timing.
    // ------------------------------------------------------
    const phase1IdleOnWall4 =
      status?.phase === 1 &&
      currentStep === 3 &&
      !status?.running &&
      !status?.homeCheckPending;
    if (phase1IdleOnWall4) {
      setForcedPlacement2(true);
      setCurrentStep(4); // Placement 2
      return;
    }
    // ------------------------------------------------------
    // MARKING COMPLETE (terminal)
    // ------------------------------------------------------
    if (
      status?.phase === 2 &&
      currentStep === 7 &&
      !status?.running &&
      !status?.homeCheckPending
    ) {
      setCurrentStep(8);
      return;
    }
    // ------------------------------------------------------
    // Otherwise normal backend continue
    // ------------------------------------------------------
    setErrorMessage(null);
    setCmdLogs([]);
    const res = await axios.post(`${API_BASE_URL}/marking/continue`);
    if (res.data?.homeCheckRequired && res.data?.next_wall) {
      await axios.post(`${API_BASE_URL}/marking/homecheck`, {
        target: `wall_${res.data.next_wall}`,
      });
    }
  });
  // Show actions:
  // - Marking error => show buttons
  // - HomeCheck failed => also show buttons (operator expects Retry/Continue
const isPlacement2 = currentStep === 4;
const isPhase1Wall4 = status?.phase === 1 && currentStep === 3;
const isHomeCheckFailed = homeCheckPending && homeCheckPassed === false;
const isRealMarkingError =
  hasError &&
  !running &&
  !homeCheckPending &&
  !isPhase1Wall4 &&   // ❌ THIS EXCLUDES WALL 4
  !isPlacement2;
const isWall4MarkingError =
  !running &&
  !homeCheckPending &&
  status?.phase === 1 &&
  currentStep === 3;
const showErrorBanner =errorMessage && isMarkingStep(currentStep); 
const isTerminalStep = currentStep === 8;
  // --------------------------------------------------------
  // POLLING (single loop, no overlap, stable)
  // --------------------------------------------------------
  const poll = async () => {
  if (!aliveRef.current) return;
  // Prevent overlapping polls
  if (pollInFlightRef.current) {
    pollingTimerRef.current = window.setTimeout(poll, 1200);
    return;
  }
  pollInFlightRef.current = true;
  try {
    const { data } = await axios.get<MarkingStatusResponse>(
      `${API_BASE_URL}/marking/status`
    );
    if (!aliveRef.current) return;
    setStatus(data);
    // -------------------------------
    // 🔴 Derive last failed wall safely
    // -------------------------------
    if (data.lastFailedWall !== undefined && data.lastFailedWall !== null) {
      setLastErrorWall(data.lastFailedWall);
    } else if (data.hasError) {
      const failed = data.startedWall ?? data.doneWall ?? null;
      if (failed !== null) setLastErrorWall(failed);
    }
    // -------------------------------
    // 🔴 Error message handling
    // -------------------------------
    if (data.hasError) {
      setErrorMessage(data.errorSummary || "Marking error detected");
    } else if (data.homeCheckPending && data.homeCheckWall !== null) {
      // Homecheck table itself is the message
      setErrorMessage(null);
    } else {
      setErrorMessage(null);
    }
    // =========================================================
    // 🧠 STEP RESOLUTION (PRIORITY-ORDERED, SAFE)
    // =========================================================
    let nextStep = currentStep;
    // 🔒 ABSOLUTE TERMINAL — NEVER LEAVE
    if (currentStep === 8) {
      // Do nothing forever once completed
      pollInFlightRef.current = false;
      pollingTimerRef.current = window.setTimeout(poll, 1500);
      return;
    }
    // 🔒 MARKING COMPLETE (backend truth only)
    const isMarkingComplete =
      data.phase === 2 &&
      !data.running &&
      !data.homeCheckPending &&
      data.doneWall === 1;
    
    if (isMarkingComplete) {
      nextStep = 8;
    }
    if (
      data.phase === 1 &&
      data.doneWall === 4 &&
      !data.running &&
      !data.homeCheckPending && 
      !forcedPlacement2    
    ) {
      setForcedPlacement2(true); // 🔒 lock it
      nextStep = 4;              // Placement 2
    }
    // 🔒 PLACEMENT 2 — operator-forced, never overridden
    else if (forcedPlacement2) {
      nextStep = 4;
    }
    // 🟡 HOME CHECK PENDING
    else if (data.homeCheckPending && data.homeCheckWall !== null) {
      nextStep = wallToStep(data.homeCheckWall);
    }
    // 🟢 MARKING RUNNING
    else if (data.running && data.startedWall !== null) {
      nextStep = wallToStep(data.startedWall);
    }
    // 🟠 IDLE FALLBACK (safe now, terminal guarded)
    else if (!data.running && data.doneWall !== null) {
      nextStep = wallToStep(data.doneWall);
    }
    if (nextStep !== currentStep) {
      setCurrentStep(nextStep);
    }
    // -------------------------------
    // 🔴 Logs (single-line summary only)
    // -------------------------------
    const logWall =
      data.homeCheckPending && data.homeCheckWall !== null
        ? data.homeCheckWall
        : data.startedWall ??
          (data.hasError ? data.startedWall ?? data.doneWall : null);

    if (logWall !== null) {
      try {
        const logRes = await axios.get(
          `${API_BASE_URL}/marking/errorlog/${logWall}`
        );
        if (logRes.data?.error) {
          const logs = logRes.data.error as string[];
          const finalLine = extractFinalSummary(logs);
          setCmdLogs(finalLine ? [finalLine] : []);
        }
      } catch {
        // ignore log fetch errors
      }
    }

  } catch {
    // ignore polling errors; keep polling
  } finally {
    pollInFlightRef.current = false;
    pollingTimerRef.current = window.setTimeout(poll, 1500);
  }
};


  useEffect(() => {
    aliveRef.current = true;
    poll();
    return () => {
      aliveRef.current = false;
      if (pollingTimerRef.current) clearTimeout(pollingTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --------------------------------------------------------
  // RENDER
  // --------------------------------------------------------
  return (
    <>
      <h2 className="text-4xl font-bold text-center mb-6">
        Marking of PBU (6-Wall Flow)
      </h2>

      <ul className="steps w-full mb-6">
        {STEP_LABELS.map((l, i) => (
          <li
            key={l}
            className={i === currentStep ? "step step-primary" : "step"}
          >
            {l}
          </li>
        ))}
      </ul>

      <div className="flex gap-6">
        <img
          src={STEP_IMAGES[currentStep]}
          className="max-w-2xl max-h-[70vh] rounded-lg shadow object-contain"
          alt="step"
        />
        <div className="flex flex-col w-[520px] gap-4">
          <div className="menu bg-base-200 rounded-box p-4 shadow">
            <p className="text-lg font-semibold">Instruction</p>
            <p className="mt-1 text-sm">
              {homeCheckPending && homeCheckWall !== null && (
                <>Home position check required for Wall {homeCheckWall}.</>
              )}
              {!homeCheckPending && currentStep === 1 && "Marking Wall 2 in progress."}
              {!homeCheckPending && currentStep === 2 && "Marking Wall 3 in progress."}
              {!homeCheckPending && currentStep === 3 && "Marking Wall 4 in progress."}
              {!homeCheckPending && currentStep === 5 && "Marking wall 5 in progress."}
              {!homeCheckPending && currentStep === 6 && "Marking wall 6 in progress."}
              {!homeCheckPending && currentStep === 7 && "Marking wall 1 in progress."}
              {currentStep === 8 && "Marking complete."}
            </p>
            <p className="mt-1 text-sm">
              Ensure that the laser leveller is turned on and is facing the wall that is to be marked.
            </p>
          </div>
          {/*
          <div className="bg-black font-mono text-xs rounded p-3 max-h-[220px] overflow-y-auto shadow">
            <div className="text-green-300 mb-1">Backend Output</div>
            {cmdLogs.length === 0 ? (
              <div className="opacity-60 text-green-400">Waiting for backend output…</div>
            ) : (
              cmdLogs.map((l, i) => (
                <div key={i} className={getLogClass(l)}>
                  {l}
                </div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
          */}
          {showErrorBanner && (
            <div className="p-3 bg-red-100 text-red-700 rounded">
              <pre className="whitespace-pre-wrap text-sm">
                {errorMessage}
              </pre>
            </div>
          )}
          {/* HOME CHECK TABLE (backend-driven, stable) */}
          {homeCheckPending && homeCheckWall !== null && homeCheckRows.length > 0 && (
            <div className="bg-white shadow rounded overflow-hidden">
              <div
                className={`text-center font-bold py-1 ${
                  homeCheckPassed === false
                    ? "bg-red-100 text-red-800"
                    : "bg-green-100 text-green-800"
                }`}
              >
                {homeCheckPassed === false ? "✖ Home check failed" : "✔ Home position verified"}
              </div>

              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="p-2 text-left">Axis</th>
                    <th className="p-2 text-left">Current</th>
                    <th className="p-2 text-left">Target</th>
                  </tr>
                </thead>
                <tbody>
                  {homeCheckRows.map((r, i) => (
                    <tr key={i} className="border-t">
                      <td className="p-2">{r.axis}</td>
                      <td className="p-2">{r.current?.toFixed?.(3)}</td>
                      <td className="p-2">{r.target?.toFixed?.(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div className="flex flex-col gap-3">
            {currentStep === 0 && (
              <button className="btn btn-primary" onClick={startPhaseOne} disabled={actionBusy}>
                {actionBusy ? "Working..." : "Next"}
              </button>
            )}
            {currentStep === 4 && !isHomeCheckFailed  && (
              <button className="btn btn-primary" onClick={startPhaseTwo} disabled={actionBusy}>
                {actionBusy ? "Working..." : "Next"}
              </button>
            )}
            {running && isMarkingStep(currentStep) && !hasError && (
              <button className="btn btn-warning" onClick={pauseMarking} disabled={actionBusy}>
                {actionBusy ? "Working..." : "Pause"}
              </button>
            )}
            {isHomeCheckFailed && (
              <button
                className="btn btn-error"
                onClick={retryCurrentWall}
                disabled={actionBusy}
              >
                Retry
              </button>
            )}
            {/* WALL 4 MARKING ERROR → Retry + Continue (to Placement 2) */}
            {isWall4MarkingError && (
              <div className="flex gap-2">
                <button
                  className="btn btn-error flex-1"
                  onClick={retryCurrentWall}
                  disabled={actionBusy}
                >
                  Retry
                </button>
                <button
                  className="btn btn-warning flex-1"
                  onClick={continueNextWall}
                  disabled={actionBusy}
                >
                  Continue →
                </button>
              </div>
            )}
            {/* Error / HomeCheck failure */}
            {isRealMarkingError && !isTerminalStep && (
              <div className="flex gap-2">
                <button
                  className="btn btn-error flex-1"
                  onClick={retryCurrentWall}
                  disabled={actionBusy}
                >
                  Retry
                </button>
                <button
                  className="btn btn-warning flex-1"
                  onClick={continueNextWall}
                  disabled={actionBusy}
                >
                  Continue →
                </button>
              </div>
            )}
            {currentStep === 8 && (
              <button className="btn btn-success" onClick={() => window.location.reload()}>
                Exit
              </button>
            )}
          </div>
          <div>
            <button
              className="btn btn-neutral btn-sm"
              onClick={() => {
                setAutoStep(0);
                setShowAutoInstr(true);
              }}
              aria-haspopup="dialog"
              aria-expanded={showAutoInstr}
              aria-controls="auto-mode-instructions"
            >
              Click here to view auto mode instructions
            </button>
          </div>
        </div>
      </div>
      {/* Overlay / Modal for Auto Mode Instructions (multi-step) */}
      {showAutoInstr && (
        <div
          id="auto-mode-instructions"
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50"
        >
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setShowAutoInstr(false)}
          />
          {/* Panel */}
          <div className="absolute inset-0 flex items-center justify-center p-4">
            <div className="w-full max-w-3xl rounded-xl bg-base-100 shadow-2xl">
              {/* Header */}
              <div className="flex items-center justify-between border-b px-5 py-3">
                <div>
                  <h3 className="text-lg font-semibold">
                    Auto Mode Instructions — {AUTO_STEPS[autoStep].title}
                  </h3>
                  <div className="text-xs text-base-content/70">
                    Step {autoStep + 1} of {totalAutoSteps}
                  </div>
                </div>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setShowAutoInstr(false)}
                  aria-label="Close"
                  title="Close"
                >
                  ✕
                </button>
              </div>
              {/* Body */}
              <div className="p-5 space-y-4 text-sm leading-6">
                {AUTO_STEPS[autoStep].body}
                <div className="alert alert-info mt-2">
                  <div>
                    Ensure the laser leveller is turned on and facing the active wall. Keep
                    the area clear while the robot is moving.
                  </div>
                </div>
              </div>
              {/* Footer controls */}
              <div className="flex justify-between border-t px-5 py-3">
                <div className="flex gap-2">
                  <button
                    className="btn btn-ghost"
                    onClick={() => setShowAutoInstr(false)}
                  >
                    Close
                  </button>
                </div>
                <div className="flex gap-2">
                  <button
                    className="btn"
                    onClick={() => setAutoStep((s) => Math.max(s - 1, 0))}
                    disabled={autoStep === 0}
                  >
                    ← Back
                  </button>
                  {autoStep < totalAutoSteps - 1 ? (
                    <button
                      className="btn btn-primary"
                      onClick={() => setAutoStep((s) => Math.min(s + 1, totalAutoSteps - 1))}
                    >
                      Next →
                    </button>
                  ) : (
                    <button
                      className="btn btn-primary"
                      onClick={() => setShowAutoInstr(false)}
                    >
                      Finish
                    </button>
                  )}
                </div>
                {/*
                <div className="text-xs opacity-60">
            running={String(running)} paused={String(paused)} hasError={String(hasError)}{" "}
            homeCheckPending={String(homeCheckPending)}
          </div>
          */}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
export default SixWallFlow;                