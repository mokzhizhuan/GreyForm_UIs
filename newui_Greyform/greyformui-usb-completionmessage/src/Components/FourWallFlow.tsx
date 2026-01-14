// =========================================================
// FourWallFlow.tsx (UI-STABLE / FRONTEND-ONLY FIX)
// Mirrors SixWallFlow behavior exactly (simplified to 4 walls)
// =========================================================

import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

import placementImg from "../assets/four_wall_flow/wall_marking_4_walls.jpg";
import wallImg from "../assets/four_wall_flow/wall_marking_4_walls.jpg";

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
const WALL_ORDER = ["wall_2", "wall_3", "wall_4", "wall_1"];

const STEP_LABELS = [
  "Placement",
  "Wall 2",
  "Wall 3",
  "Wall 4",
  "Wall 1",
  "Marking Complete",
];

const STEP_IMAGES = [
  placementImg,
  wallImg,
  wallImg,
  wallImg,
  wallImg,
  wallImg,
];

// wall → step
const wallToStep = (wall: number) => {
  switch (wall) {
    case 2:
      return 1;
    case 3:
      return 2;
    case 4:
      return 3;
    case 1:
      return 4;
    default:
      return 0;
  }
};

const isMarkingStep = (s: number) => [1, 2, 3, 4].includes(s);

// --------------------------------------------------------
// HOME CHECK PARSER (same as SixWallFlow)
// --------------------------------------------------------
const parseHomeCheck = (output: string) => {
  const lines = (output || "").split(/\r?\n/).map((l) => l.trim());
  const rax = lines.find((l) => l.includes("rax_1"));
  const tgt = lines.find((l) => l.includes("j0"));

  let current: any = {};
  let target: any = {};

  try {
    if (rax) current = JSON.parse(rax.replace(/'/g, '"'));
    if (tgt) target = JSON.parse(tgt.replace(/'/g, '"'));
  } catch {}

  return Object.entries(target).map(([k, v], i) => ({
    axis: `J${i + 1}`,
    target: v,
    current: current[`rax_${i + 1}`],
  }));
};

// --------------------------------------------------------
// COMPONENT
// --------------------------------------------------------
const FourWallFlow: React.FC<any> = ({
  wallDetails,
  maxWall,
  excelFiles,
  meshfile,
  folderdirectory,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [status, setStatus] = useState<MarkingStatusResponse | null>(null);

  const running = !!status?.running;
  const paused = !!status?.paused;
  const hasError = !!status?.hasError;

  const homeCheckPending = !!status?.homeCheckPending;
  const homeCheckWall = status?.homeCheckWall ?? null;
  const homeCheckOutput = status?.homeCheckOutput ?? "";

  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // --------------------------------------------------------
  // ACTION LOCK
  // --------------------------------------------------------
  const actionLockRef = useRef(false);
  const [actionBusy, setActionBusy] = useState(false);

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
  // NORMALIZE WALL DATA
  // --------------------------------------------------------
  const normalized = useMemo(() => {
    const out: Record<string, WallRow[]> = {};
    for (const [k, v] of Object.entries(wallDetails || {})) {
      const m = k.match(/\d+/);
      out[`wall_${m ? m[0] : k}`] = v as any;
    }
    return out;
  }, [wallDetails]);

  const buildExcelMap = (files: string[]) => {
    const map: Record<string, string> = {};
    for (const f of files) {
      const m = f.match(/_wall_(\d+)\.xlsx$/);
      if (m) map[`wall_${m[1]}`] = f;
    }
    return map;
  };

  const excelMap = useMemo(() => buildExcelMap(excelFiles || []), [excelFiles]);

  // --------------------------------------------------------
  // HOME CHECK TABLE
  // --------------------------------------------------------
  const homeCheckRows = useMemo(() => {
    if (!homeCheckPending || !homeCheckOutput) return [];
    return parseHomeCheck(homeCheckOutput);
  }, [homeCheckPending, homeCheckOutput]);

  const homeCheckPassed = useMemo(() => {
    if (!homeCheckPending) return null;
    return homeCheckOutput
      .split(/\r?\n/)
      .some((l) => l.trim() === "True");
  }, [homeCheckPending, homeCheckOutput]);

  // --------------------------------------------------------
  // START MARKING
  // --------------------------------------------------------
  const startMarking = async () =>
    withActionLock(async () => {
      setErrorMessage(null);

      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls: WALL_ORDER.map((w) => ({
          wall: w,
          rows: normalized[w] ?? [],
          excel: excelMap[w] ?? "",
        })),
        meshfile,
        folder: folderdirectory,
        max_wall: maxWall,
        phase: 1,
      });

      await axios.post(`${API_BASE_URL}/marking/homecheck`, {
        target: "wall_2",
      });
    });

  // --------------------------------------------------------
  // ACTIONS
  // --------------------------------------------------------
  const pauseMarking = async () =>
    withActionLock(async () => {
      await axios.post(`${API_BASE_URL}/marking/pause`);
    });

  const retryWall = async () =>
    withActionLock(async () => {
      setErrorMessage(null);
      await axios.post(`${API_BASE_URL}/marking/retry`);
    });

  const continueNext = async () =>
    withActionLock(async () => {
      // terminal
      if (
        status?.doneWall === 1 &&
        !status?.running &&
        !status?.homeCheckPending
      ) {
        setCurrentStep(5);
        return;
      }

      const res = await axios.post(`${API_BASE_URL}/marking/continue`);
      if (res.data?.homeCheckRequired && res.data?.next_wall) {
        await axios.post(`${API_BASE_URL}/marking/homecheck`, {
          target: `wall_${res.data.next_wall}`,
        });
      }
    });

  // --------------------------------------------------------
  // POLLING (IDENTICAL MODEL TO SixWallFlow)
// --------------------------------------------------------
  const pollTimerRef = useRef<number | null>(null);
  const pollInFlightRef = useRef(false);
  const aliveRef = useRef(true);

  const poll = async () => {
    if (!aliveRef.current) return;
    if (pollInFlightRef.current) {
      pollTimerRef.current = window.setTimeout(poll, 1200);
      return;
    }

    pollInFlightRef.current = true;
    try {
      const { data } = await axios.get<MarkingStatusResponse>(
        `${API_BASE_URL}/marking/status`
      );

      if (!aliveRef.current) return;
      setStatus(data);

      if (data.hasError) {
        setErrorMessage(data.errorSummary || "Marking error detected");
      } else {
        setErrorMessage(null);
      }

      let nextStep = currentStep;

      if (
        data.doneWall === 1 &&
        !data.running &&
        !data.homeCheckPending
      ) {
        nextStep = 5;
      } else if (data.homeCheckPending && data.homeCheckWall) {
        nextStep = wallToStep(data.homeCheckWall);
      } else if (data.running && data.startedWall) {
        nextStep = wallToStep(data.startedWall);
      } else if (!data.running && data.doneWall) {
        nextStep = wallToStep(data.doneWall);
      }

      if (nextStep !== currentStep) {
        setCurrentStep(nextStep);
      }
    } catch {
      // ignore
    } finally {
      pollInFlightRef.current = false;
      pollTimerRef.current = window.setTimeout(poll, 1500);
    }
  };

  useEffect(() => {
    aliveRef.current = true;
    poll();
    return () => {
      aliveRef.current = false;
      if (pollTimerRef.current) clearTimeout(pollTimerRef.current);
    };
    // eslint-disable-next-line
  }, []);

  // --------------------------------------------------------
  // RENDER
  // --------------------------------------------------------
  return (
    <>
      <h2 className="text-4xl font-bold text-center mb-6">
        Marking of PBU (4-Wall Flow)
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
        />

        <div className="flex flex-col w-[480px] gap-4">
          <div className="menu bg-base-200 rounded-box p-4 shadow">
            <p className="text-lg font-semibold">Instruction</p>
            <p className="mt-1 text-sm">
              {homeCheckPending && homeCheckWall
                ? `Home position check required for Wall ${homeCheckWall}.`
                : currentStep === 0
                ? "Position robot for Wall 2."
                : currentStep === 5
                ? "Marking complete."
                : "Marking wall in progress."}
            </p>
          </div>

          {errorMessage && (
            <div className="p-3 bg-red-100 text-red-700 rounded">
              {errorMessage}
            </div>
          )}

          {homeCheckPending && homeCheckRows.length > 0 && (
            <div className="bg-white shadow rounded overflow-hidden">
              <div
                className={`text-center font-bold py-1 ${
                  homeCheckPassed ? "bg-green-100" : "bg-red-100"
                }`}
              >
                {homeCheckPassed
                  ? "✔ Home position verified"
                  : "✖ Home check failed"}
              </div>

              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="p-2">Axis</th>
                    <th className="p-2">Current</th>
                    <th className="p-2">Target</th>
                  </tr>
                </thead>
                <tbody>
                  {homeCheckRows.map((r, i) => (
                    <tr key={i}>
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
              <button
                className="btn btn-primary"
                onClick={startMarking}
                disabled={actionBusy}
              >
                Next
              </button>
            )}

            {running && isMarkingStep(currentStep) && !hasError && (
              <button
                className="btn btn-warning"
                onClick={pauseMarking}
                disabled={actionBusy}
              >
                Pause
              </button>
            )}

            {(hasError || homeCheckPassed === false) && (
              <div className="flex gap-2">
                <button
                  className="btn btn-error flex-1"
                  onClick={retryWall}
                  disabled={actionBusy}
                >
                  Retry
                </button>
                <button
                  className="btn btn-warning flex-1"
                  onClick={continueNext}
                  disabled={actionBusy}
                >
                  Continue →
                </button>
              </div>
            )}

            {currentStep === 5 && (
              <button className="btn btn-success" onClick={() => window.close()}>
                Exit
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default FourWallFlow;
