// =========================================================
// FINAL SixWallFlow.tsx (ROBUST)
// - Retry ALWAYS works (uses lastErrorWall)
// - Continue handles Wall 4 -> Placement 2, Wall 1 -> Complete
// - failureWall + lastErrorWall captured from poll()
// - No refresh needed
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
    case 2: return 1;
    case 3: return 2;
    case 4: return 3;
    case 5: return 5;
    case 6: return 6;
    case 1: return 7;
    default: return 0;
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
  const lines = (output || "").split(/\r?\n/).map(l => l.trim());
  const rax = lines.find(l => l.includes("rax_1"));
  const tgt = lines.find(l => l.includes("j0"));

  let current: any = {};
  let target: any = {};

  try {
    if (rax) current = JSON.parse(rax.replace(/'/g, '"'));
    if (tgt) target = JSON.parse(tgt.replace(/'/g, '"'));
  } catch {}

  // Map j0..j5 -> J1..J6
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
  if (line.includes("[SKIP]")) return "text-yellow-300";
  if (line.toLowerCase().includes("bringup")) return "text-blue-400";
  return "text-green-400";
};

const isMarkingStep = (s: number) => [1, 2, 3, 5, 6, 7].includes(s);

// =========================================================
// COMPONENT
// =========================================================
const SixWallFlow: React.FC<any> = ({
  wallDetails,
  maxWall,
  excelFiles,
  meshfile,
  folderdirectory,
}) => {
  const [currentStep, setCurrentStep] = useState(0);

  const [running, setRunning] = useState(false);
  const [paused, setPaused] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // 🔥 error targeting
  const [failureWall, setFailureWall] = useState<number | null>(null);
  const [lastErrorWall, setLastErrorWall] = useState<number | null>(null);

  // HomeCheck UI
  const [homeCheckRows, setHomeCheckRows] = useState<any[]>([]);
  const [homeCheckWall, setHomeCheckWall] = useState<number | null>(null);
  const [homeCheckPassed, setHomeCheckPassed] = useState<boolean | null>(null);

  // Logs UI
  const [cmdLogs, setCmdLogs] = useState<string[]>([]);
  const logEndRef = useRef<HTMLDivElement | null>(null);

  // Poll control
  const pollingRef = useRef<number | null>(null);
  const uiLockedRef = useRef(false);

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
  // AUTO SCROLL LOGS
  // --------------------------------------------------------
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [cmdLogs]);

  // --------------------------------------------------------
  // HOME CHECK
  // --------------------------------------------------------
  const triggerHomeCheck = async (wall: number) => {
    setErrorMessage(null);
    setHasError(false);

    setHomeCheckWall(wall);
    setHomeCheckRows([]);
    setHomeCheckPassed(null);

    setCurrentStep(wallToStep(wall));
    uiLockedRef.current = true;

    const res = await axios.post(`${API_BASE_URL}/marking/homecheck`, {
      target: `wall_${wall}`,
    });

    const passed = !!res.data?.passed;
    const output = res.data?.output || "";

    setHomeCheckPassed(passed);
    setHomeCheckRows(parseHomeCheck(output));

    if (!passed) {
      setHasError(true);
      setErrorMessage(res.data?.error || `Home check failed for wall ${wall}`);
      setLastErrorWall(wall);
      setFailureWall(wall);
      return;
    }

    setTimeout(() => {
      setHomeCheckRows([]);
      setHomeCheckWall(null);
      setHomeCheckPassed(null);
      uiLockedRef.current = false;
    }, 800);
  };

  // --------------------------------------------------------
  // START PHASES
  // --------------------------------------------------------
  const startPhaseOne = async () => {
    await axios.post(`${API_BASE_URL}/marking/start`, {
      walls: PHASE1_ORDER.map(w => ({
        wall: w,
        rows: getRows(w),
        excel: excelMap[w] ?? "",
      })),
      meshfile,
      folder: folderdirectory,
      max_wall: maxWall,
      phase: 1,
    });
    setCmdLogs([]);
    setHasError(false);
    setErrorMessage(null);

    await triggerHomeCheck(2);
  };

  const startPhaseTwo = async () => {
    await axios.post(`${API_BASE_URL}/marking/start`, {
      walls: PHASE2_ORDER.map(w => ({
        wall: w,
        rows: getRows(w),
        excel: excelMap[w] ?? "",
      })),
      meshfile,
      folder: folderdirectory,
      max_wall: maxWall,
      phase: 2,
    });

    setCmdLogs([]);
    setHasError(false);
    setErrorMessage(null);

    await triggerHomeCheck(5);
  };

  // --------------------------------------------------------
  // ACTIONS
  // --------------------------------------------------------
  const pauseMarking = async () => {
    await axios.post(`${API_BASE_URL}/marking/pause`);
  };

  const showFailureActions = hasError || homeCheckPassed === false;
  const [homeCheckPending, setHomeCheckPending] = useState(false);
  const retryCurrentWall = async () => {
  const wall = lastErrorWall;
  if (!wall) return;

  setCmdLogs([]);
  setHasError(false);
  setErrorMessage(null);

  // 1) Tell backend: retry same wall (sets homecheck gate)
  await axios.post(`${API_BASE_URL}/marking/retry`);

  // 2) Run homecheck for SAME wall
  await triggerHomeCheck(wall);
};

  const continueNextWall = async () => {
  const res = await axios.post(`${API_BASE_URL}/marking/continue`);

  setHasError(false);
  setErrorMessage(null);
  setCmdLogs([]);
  uiLockedRef.current = false;

  // phase jump rules
  if (!hasError && running === false && failureWall === null && currentStep === 3) {
    setCurrentStep(4);
  }
  if (!hasError && running === false && failureWall === null && currentStep === 7) {
  setCurrentStep(8);  
  }

  if (res.data?.homeCheckRequired && res.data?.next_wall) {
    await triggerHomeCheck(res.data.next_wall); // ✅ THIS is the key
  }
};

  // --------------------------------------------------------
  // POLLING
  // --------------------------------------------------------
  const poll = async () => {
  try {
    const { data } = await axios.get<MarkingStatusResponse>(
      `${API_BASE_URL}/marking/status`
    );

    setRunning(data.running);
    setPaused(data.paused);
    setHasError(!!data.hasError);
    setErrorMessage(data.errorSummary || null);
    setHomeCheckPending(!!data.homeCheckPending);
    setHomeCheckWall(data.homeCheckWall ?? null);
    // ✅ Re-hydrate failure wall after page refresh
    if (data.lastFailedWall !== undefined && data.lastFailedWall !== null) {
      setLastErrorWall(data.lastFailedWall);
      setFailureWall(data.lastFailedWall);
    }

    // 🔥 UNLOCK UI WHEN WAITING FOR HOME CHECK
    if (data.homeCheckPending) {
      uiLockedRef.current = false;
    }

    // ==================================================
    // 1️⃣ HOME CHECK PENDING → MOVE TO NEXT WALL
    // ==================================================
    if (data.homeCheckPending && data.homeCheckWall !== null) {
      setCurrentStep(wallToStep(data.homeCheckWall));

      const logRes = await axios.get(
        `${API_BASE_URL}/marking/errorlog/${data.homeCheckWall}`
      );
      if (logRes.data?.error) {
        setCmdLogs(logRes.data.error.slice(-50));
      }

      pollingRef.current = window.setTimeout(poll, 1500);
      return;
    }
    
    // ==================================================
    // 2️⃣ ERROR STATE → STAY ON FAILED WALL
    // ==================================================
    if (data.hasError) {
      const failed = data.startedWall ?? data.doneWall ?? null;
      if (failed !== null) {
        setFailureWall(failed);
        setLastErrorWall(failed);
        setCurrentStep(wallToStep(failed));

        const logRes = await axios.get(
          `${API_BASE_URL}/marking/errorlog/${failed}`
        );
        if (logRes.data?.error) {
          setCmdLogs(logRes.data.error.slice(-50));
        }
      }

      pollingRef.current = window.setTimeout(poll, 1500);
      return;
    }

    // ==================================================
    // 3️⃣ ACTIVE MARKING
    // ==================================================
    if (
      data.running &&
      data.startedWall !== null &&
      !uiLockedRef.current
    ) {
      setCurrentStep(wallToStep(data.startedWall));

      const logRes = await axios.get(
        `${API_BASE_URL}/marking/errorlog/${data.startedWall}`
      );
      if (logRes.data?.error) {
        setCmdLogs(logRes.data.error.slice(-50));
      }

      pollingRef.current = window.setTimeout(poll, 1500);
      return;
    }

    // ==================================================
    // 4️⃣ PHASE TRANSITIONS
    // ==================================================
    if (data.doneWall === 4 && data.phase === 1) {
      setCurrentStep(4);
    }

    if (data.doneWall === 1 && data.phase === 2) {
      setCurrentStep(8);
    }

  } catch (e) {
    // optional console.error(e)
  }

  pollingRef.current = window.setTimeout(poll, 1500);
};


  useEffect(() => {
    poll();
    return () => pollingRef.current && clearTimeout(pollingRef.current);
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
          <li key={l} className={i === currentStep ? "step step-primary" : "step"}>
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
          {/*
          <div className="menu bg-base-200 rounded-box p-4 shadow">
            <p className="text-2xl font-semibold">{STEP_LABELS[currentStep]}</p>
          </div>
          */}

          <div className="menu bg-base-200 rounded-box p-4 shadow">
            <p className="text-lg font-semibold">Instruction</p>
            <p className="mt-1 text-sm">
              {homeCheckPending && homeCheckWall !== null && (
                <>Home position check required for Wall {homeCheckWall}.</>
              )}

              {!homeCheckPending && currentStep === 1 && "Marking Wall 2 in progress."}
              {!homeCheckPending && currentStep === 2 && "Marking Wall 3 in progress."}
              {!homeCheckPending && currentStep === 3 && "Marking Wall 4 in progress."}

              {!homeCheckPending && currentStep >= 5 && currentStep <= 7 && (
                "Marking wall in progress."
              )}
              {currentStep === 8 && "Marking complete."}
            </p>

            <p className="mt-1 text-sm">
              {"Ensure that the laser leveller is turned on and is facing the wall that is to be marked."}
            </p>
          </div>
	{/*
          <div className="bg-black font-mono text-xs rounded p-3 max-h-[220px] overflow-y-auto shadow">
            <div className="text-green-300 mb-1">Backend Output</div>
            {cmdLogs.length === 0 ? (
              <div className="opacity-60 text-green-400">Waiting for backend output…</div>
            ) : (
              cmdLogs.map((l, i) => (
                <div key={i} className={getLogClass(l)}>{l}</div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
		
          {errorMessage && (
            <div className="p-3 bg-red-100 text-red-700 rounded">{errorMessage}</div>
          )}
	*/}
          {homeCheckRows.length > 0 && (
            <div className="bg-white shadow rounded overflow-hidden">
              <div className={`text-center font-bold py-1 ${homeCheckPassed === false ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"}`}>
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
              <button className="btn btn-primary" onClick={startPhaseOne}>Next</button>
            )}

            {currentStep === 4 && (
              <button className="btn btn-primary" onClick={startPhaseTwo}>Next</button>
            )}

            {running && isMarkingStep(currentStep) && !hasError && (
              <button className="btn btn-warning" onClick={pauseMarking}>Pause</button>
            )}

            {showFailureActions && (
              <div className="flex gap-2">
                <button className="btn btn-error flex-1" onClick={retryCurrentWall}>Retry</button>
                <button className="btn btn-warning flex-1" onClick={continueNextWall}>Continue →</button>
              </div>
            )}

            {currentStep === 8 && (
              <button className="btn btn-success" onClick={() => window.close()}>Exit</button>
            )}
          </div>

          <div className="text-xs opacity-60">
            running={String(running)} paused={String(paused)} hasError={String(hasError)}
          </div>
        </div>
      </div>
    </>
  );
};

export default SixWallFlow;
