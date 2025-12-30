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
import wallMarking1 from "../assets/six_wall_flow/wall_marking_6_walls1.jpg";
import wallMarking2 from "../assets/six_wall_flow/wall_marking_6_walls2.jpg";

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

const getLogClass = (line: string) => {
  if (line.includes("[ERROR]")) return "text-red-400 font-bold";
  if (line.includes("[SKIP]") || line.includes("[SKIPPED]")) return "text-yellow-300";
  if (line.toLowerCase().includes("bringup")) return "text-blue-400";
  return "text-green-400";
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
  const phase1Ended =
  status?.phase === 1 &&
  status?.doneWall === 4 &&
  !status?.running &&
  !status?.homeCheckPending &&
  !status?.hasError;

const phase2Ended =
  status?.phase === 2 &&
  status?.doneWall === 1 &&
  !status?.running &&
  !status?.homeCheckPending;
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

const isMarkingComplete =
  status?.phase === 2 &&
  !status?.running &&
  !status?.homeCheckPending &&
  currentStep === 7;

const isPlacement2 =
  currentStep === 4;

const isPhase1Wall4 =
  status?.phase === 1 && currentStep === 3;

const isHomeCheckFailed =
  homeCheckPending && homeCheckPassed === false;

const isRealMarkingError =
  hasError &&
  !running &&
  !homeCheckPending &&
  !isPhase1Wall4 &&   // ❌ THIS EXCLUDES WALL 4
  !isPlacement2;

const isWall4MarkingError =
  (!hasError || hasError) &&
   !running &&
  !homeCheckPending &&
  status?.phase === 1 &&
  currentStep === 3;

const showErrorBanner =
  errorMessage &&
  isMarkingStep(currentStep); 

const isTerminalStep = currentStep === 8;
  // --------------------------------------------------------
  // POLLING (single loop, no overlap, stable)
  // --------------------------------------------------------
  const poll = async () => {
    if (!aliveRef.current) return;
    if (pollInFlightRef.current) {
      // prevent overlap
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

      // derive lastErrorWall reliably
      if (data.lastFailedWall !== undefined && data.lastFailedWall !== null) {
        setLastErrorWall(data.lastFailedWall);
      } else if (data.hasError) {
        const failed = data.startedWall ?? data.doneWall ?? null;
        if (failed !== null) setLastErrorWall(failed);
      }

      // instruction/error message
      if (data.hasError) {
        setErrorMessage(data.errorSummary || "Marking error detected");
      } else if (data.homeCheckPending && data.homeCheckWall !== null) {
        // On homecheck failure, backend should still provide output.
        // If it doesn't, keep message minimal.
        if (homeCheckOutput) {
          const passed = homeCheckOutput.split(/\r?\n/).some((l) => l.trim() === "True");
          if (!passed) setErrorMessage(null); // table itself is the message
        }
      } else {
        setErrorMessage(null);
      }

      // Step control:
      // 1) HomeCheck pending -> step to that wall
    let nextStep = currentStep;

    // 🔒 MARKING COMPLETE — ABSOLUTE TERMINAL
    if (isMarkingComplete) {
      nextStep = 8;
    }

    // 🔒 Placement 2 forced by operator
    else if (forcedPlacement2) {
      nextStep = 4;
    }

    // 🟡 Home check pending
    else if (data.homeCheckPending && data.homeCheckWall !== null) {
      nextStep = wallToStep(data.homeCheckWall);
    }

    // 🟢 Marking running
    else if (data.running && data.startedWall !== null) {
      nextStep = wallToStep(data.startedWall);
    }

    // 🟣 Phase 1 idle on Wall 4 (wait for Continue)
    else if (
      data.phase === 1 &&
      !data.running &&
      !data.homeCheckPending &&
      currentStep === 3
    ) {
      nextStep = 3;
    }

    // 🟠 Idle fallback
    else if (!data.running && data.doneWall !== null) {
      nextStep = wallToStep(data.doneWall);
    }

    if (nextStep !== currentStep) {
      setCurrentStep(nextStep);
    }
      // logs (only for a relevant wall)
      const logWall =
        data.homeCheckPending && data.homeCheckWall !== null
          ? data.homeCheckWall
          : data.startedWall ?? (data.hasError ? (data.startedWall ?? data.doneWall) : null);

      if (logWall !== null) {
        try {
          const logRes = await axios.get(`${API_BASE_URL}/marking/errorlog/${logWall}`);
          if (logRes.data?.error) {
            const logs = logRes.data.error as string[];

            const finalLine = extractFinalSummary(logs);

            if (finalLine) {
              setCmdLogs([finalLine]); // 🔥 ONLY ONE LINE
            } else {
              setCmdLogs([]); // or keep previous
            }
          }

        } catch {
          // ignore log fetch errors
        }
      }

    } catch {
      // ignore poll errors; keep polling
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

              {!homeCheckPending && currentStep >= 5 && currentStep <= 7 && "Marking wall in progress."}
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
              {errorMessage}
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
                <button
                  className="btn btn-success"
                  onClick={() => window.close()}
                >
                  Exit
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
    </>
  );
};

export default SixWallFlow;
