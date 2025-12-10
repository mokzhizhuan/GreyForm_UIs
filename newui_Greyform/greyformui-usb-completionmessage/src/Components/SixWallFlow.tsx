import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

import placementOne from "../assets/six_wall_flow/6_wall_flow_placement1.jpg";
import placementTwo from "../assets/six_wall_flow/6_wall_flow_placement2.jpg";
import wallMarking1 from "../assets/six_wall_flow/wall_marking_6_walls1.jpg";
import wallMarking2 from "../assets/six_wall_flow/wall_marking_6_walls2.jpg";

import { API_BASE_URL } from "./config";

// --------------------------------------------------------
// TYPES
// --------------------------------------------------------
type StepStatus = "idle" | "pending" | "error";

interface MarkingStatusResponse {
  running: boolean;
  paused: boolean;
  startedWall: number | null;
  doneWall: number | null;
  queue: string[];
  maxWalls: number;
  phase: number | null;
  excelFile?: string;
  meshFile?: string;
  folder?: string;
  lineCount?: number;      // interpreted as "points done"
  totalPoints?: number;    // from backend
  hasError?: boolean;
  errorSummary?: string | null;
}

interface WallRow {
  [key: string]: any;
}

interface SixWallFlowProps {
  wallDetails: Record<string, WallRow[]>;
  maxWall: number;
  excelfile: string;
  meshfile: string;
  folderdirectory: string;
}

// --------------------------------------------------------
// UI STEPS
// --------------------------------------------------------
const STEPS = [
  "Placement 1", // 0
  "Wall 2",      // 1
  "Wall 3",      // 2
  "Wall 4",      // 3
  "Placement 2", // 4
  "Wall 5",      // 5
  "Wall 6",      // 6
  "Wall 1",      // 7
  "Marking Complete", // 8
];

const STEP_IMAGES = [
  placementOne,
  wallMarking1,
  wallMarking1,
  wallMarking1,
  placementTwo,
  wallMarking2,
  wallMarking2,
  wallMarking2,
  wallMarking2,
];

// wallId → step index
const STEP_SEQUENCE: Record<number | string, number> = {
  2: 1,
  3: 2,
  4: 3,
  P2: 4,
  5: 5,
  6: 6,
  1: 7,
  DONE: 8,
};

// wallId → what comes next (wall or special key)
const NEXT_KEY_FOR_WALL: Record<number, number | "P2" | "DONE"> = {
  2: 3,
  3: 4,
  4: "P2",
  5: 6,
  6: 1,
  1: "DONE",
};

// helper: which wall number corresponds to which step
const wallFromStep = (step: number): number | null => {
  if (step === 1) return 2;
  if (step === 2) return 3;
  if (step === 3) return 4;
  if (step === 5) return 5;
  if (step === 6) return 6;
  if (step === 7) return 1;
  return null;
};

// --------------------------------------------------------
// COMPONENT
// --------------------------------------------------------
const SixWallFlow: React.FC<SixWallFlowProps> = ({
  wallDetails,
  maxWall,
  excelfile,
  meshfile,
  folderdirectory,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [status, setStatus] = useState<StepStatus>("idle");
  const [paused, setPaused] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);
  const [autoCompletedWall, setAutoCompletedWall] = useState<number | null>(
    null
  );

  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef(false);
  const currentStepRef = useRef(0);

  const isFinalStep = currentStep === 8;

  useEffect(() => {
    currentStepRef.current = currentStep;
  }, [currentStep]);

  const isMarkingStep = (step: number) => [1, 2, 3, 5, 6, 7].includes(step);

  const clearPolling = () => {
    if (pollingRef.current) clearTimeout(pollingRef.current);
    pollingRef.current = null;
  };

  const schedulePoll = (ms = 1500) => {
    if (!mountedRef.current) return;
    clearPolling();
    pollingRef.current = window.setTimeout(fetchStatus, ms);
  };

  // --------------------------------------------------------
  // NORMALIZE wallDetails KEYS → always "wall_X"
  // --------------------------------------------------------
  const normalizedDetails: Record<string, WallRow[]> = {};
  for (const [key, rows] of Object.entries(wallDetails)) {
    const match = key.match(/\d+/);
    const label = match ? `wall_${match[0]}` : key;
    normalizedDetails[label] = rows ?? [];
  }

  const getRowCountForWall = (wallNum: number) =>
    normalizedDetails[`wall_${wallNum}`]?.length ?? 0;

  // --------------------------------------------------------
  // API: PAUSE / RESUME
  // --------------------------------------------------------
  const pauseMarking = async () => {
    try {
      await axios.post(`${API_BASE_URL}/marking/pause`);
      setPaused(true);
      schedulePoll(500); // refresh quickly
    } catch (err) {
      console.error("Pause failed:", err);
      setErrorMessage("Failed to pause marking.");
    }
  };

  const resumeMarking = async () => {
    try {
      await axios.post(`${API_BASE_URL}/marking/continue`);
      setPaused(false);
      schedulePoll(500);
    } catch (err) {
      console.error("Resume failed:", err);
      setErrorMessage("Failed to resume marking.");
    }
  };

  // --------------------------------------------------------
  // RETRY API
  // --------------------------------------------------------
  const retryCurrentWall = async () => {
    const wallNum = wallFromStep(currentStepRef.current);
    if (!wallNum) return;

    try {
      await axios.post(`${API_BASE_URL}/marking/retry`, null, {
        params: { wall: wallNum },
      });
      console.log(`🔁 Retry requested for wall ${wallNum}`);
      setErrorMessage(null);
      setHasError(false);
      schedulePoll(1000);
    } catch (err) {
      console.error("Retry failed:", err);
      setErrorMessage("Retry failed. Please check logs.");
    }
  };

  // --------------------------------------------------------
  // HOME CHECK (per-wall, no phase)
  // --------------------------------------------------------
  const [homeCurrentRax, setHomeCurrentRax] =
    useState<Record<string, number> | null>(null);
  const [homeTargetJoints, setHomeTargetJoints] =
    useState<Record<string, number> | null>(null);

  const requestHomeCheckForWall = async (
    targetLabel: string
  ): Promise<boolean> => {
    try {
      const res = await axios.post(`${API_BASE_URL}/marking/homecheck`, {
        target: targetLabel,
      });

      console.log("JOINTTARGET RAW RESPONSE:", res.data);

      const output: string = res.data.output ?? "";
      const arr = output
        .split(/\r?\n/)
        .map((s) => s.trim())
        .filter(Boolean);

      console.log("PARSED LINES:", arr);

      // ---- Extract RAX JSON block ----
      const raxLine = arr.find((line) => line.includes("rax_1"));
      if (raxLine) {
        try {
          const cleaned = raxLine
            .trim()
            .replace(/^"+|"+$/g, "")
            .replace(/^'+|'+$/g, "")
            .replace(/'/g, '"');
          console.log("CLEANED RAX:", cleaned);
          setHomeCurrentRax(JSON.parse(cleaned));
        } catch (e) {
          console.warn("Failed to parse RAX JSON:", raxLine, e);
        }
      }

      // ---- Extract poses.json JSON block ----
      const targetLine = arr.find((line) => line.includes("j0"));
      if (targetLine) {
        try {
          const cleaned = targetLine
            .trim()
            .replace(/^"+|"+$/g, "")
            .replace(/^'+|'+$/g, "")
            .replace(/'/g, '"');
          console.log("CLEANED TARGET:", cleaned);
          setHomeTargetJoints(JSON.parse(cleaned));
        } catch (e) {
          console.warn("Failed to parse poses.json:", targetLine, e);
        }
      }

      const last = arr[arr.length - 1]?.trim();
      const inHome = last === "True";

      if (!inHome) {
        setErrorMessage(
          "Robot is NOT in HOME position. Please move robot to HOME and try again."
        );
      } else {
        setErrorMessage(null);
      }

      return inHome;
    } catch (err) {
      console.error("Home check failed:", err);
      setErrorMessage("Home check failed. Please try again.");
      return false;
    }
  };

  // --------------------------------------------------------
  // HOME CHECK TABLE ROWS
  // --------------------------------------------------------
  const homeCheckRows =
    homeCurrentRax && homeTargetJoints
      ? Object.entries(homeTargetJoints).map(([key, targetVal], idx) => ({
          axis: key.toUpperCase(),
          current: homeCurrentRax[`rax_${idx + 1}`],
          target: targetVal,
        }))
      : [];

  // --------------------------------------------------------
  // START PHASE 1 (walls 2, 3, 4)
  // --------------------------------------------------------
  const startPhaseOne = async () => {
    // const ok = await requestHomeCheckForWall("wall_2");
    // if (!ok) return;

    const walls = ["wall_2", "wall_3", "wall_4"].map((label) => ({
      wall: label,
      rows: normalizedDetails[label] ?? [],
    }));
    console.log("▶ startPhaseOne() walls payload:", walls);

    const res = await axios.post(`${API_BASE_URL}/marking/start`, {
      walls,
      excelfile,
      meshfile,
      folder: folderdirectory,
      phase: 1,
      max_wall: maxWall,
    });

    console.log("✅ /marking/start Phase 1 response:", res.data);

    setCurrentStep(1);
    schedulePoll(500);
  };

  // --------------------------------------------------------
  // START PHASE 2 (walls 5, 6, 1)
  // --------------------------------------------------------
  const startPhaseTwo = async () => {
    // const ok = await requestHomeCheckForWall("wall_5");
    // if (!ok) return;

    const walls = ["wall_5", "wall_6", "wall_1"].map((label) => ({
      wall: label,
      rows: normalizedDetails[label] ?? [],
    }));
    console.log("▶ startPhaseTwo() walls payload:", walls);

    const res = await axios.post(`${API_BASE_URL}/marking/start`, {
      walls,
      excelfile,
      meshfile,
      folder: folderdirectory,
      phase: 2,
      max_wall: maxWall,
    });

    console.log("✅ /marking/start Phase 2 response:", res.data);

    setCurrentStep(5);
    schedulePoll(500);
  };

  // --------------------------------------------------------
  // POLLING — event-based, uses backend's lineCount as point counter
  // --------------------------------------------------------
  const fetchStatus = async () => {
    try {
      const res = await axios.get<MarkingStatusResponse>(
        `${API_BASE_URL}/marking/status`
      );
      const data = res.data;

      // log whole payload once per poll
      console.log("📡 /marking/status:", data);

      setPaused(Boolean(data.paused));
      setStatus(data.running ? "pending" : "idle");
      setHasError(Boolean(data.hasError));
      if (data.errorSummary) {
        setErrorMessage(data.errorSummary);
      }

      const stepNow = currentStepRef.current;

      // ACTIVE MARKING
      if (data.running && data.startedWall) {
        const wall = data.startedWall;
        const lineCount = data.lineCount ?? 0;
        const totalLocal = getRowCountForWall(wall);
        const totalServer = data.totalPoints ?? totalLocal;
        const total = totalServer || totalLocal;

        // Non-visible "point counter" log
        console.log(
          `🔢 Wall ${wall} → ${lineCount} / ${total} points done (backend)`
        );

        const stepIdx = STEP_SEQUENCE[wall];
        if (stepIdx !== undefined && stepIdx !== stepNow) {
          setCurrentStep(stepIdx);
        }

        // AUTO-ADVANCE WHEN COMPLETED and NO ERROR
        if (!data.hasError && total > 0 && lineCount >= total) {
          console.log(`🌟 Auto-advance from wall ${wall}`);
          setAutoCompletedWall(wall);
          const nextKey = NEXT_KEY_FOR_WALL[wall];
          const nextStep = STEP_SEQUENCE[nextKey];
          if (nextStep !== undefined) {
            setCurrentStep(nextStep);
          }
        }

        // Poll while marking
        schedulePoll(4000);
        return;
      }

      // ERROR STATE — do NOT auto-advance, wait for Retry
      if (!data.running && data.hasError && data.startedWall !== null) {
        const wall = data.startedWall;
        const lineCount = data.lineCount ?? 0;
        const totalLocal = getRowCountForWall(wall);
        const totalServer = data.totalPoints ?? totalLocal;
        const total = totalServer || totalLocal;

        console.log(
          `❌ Wall ${wall} error: points ${lineCount}/${total} — waiting for Retry`
        );
        // stay on same step
        schedulePoll(3000);
        return;
      }

      // IDLE & DONE WALL (no error): fallback to queue-based UI progress
      if (!data.running && data.doneWall !== null && !data.hasError) {
        const wallDone = data.doneWall;
        console.log(
          `✅ doneWall reported: ${wallDone} | remaining queue=${(
            data.queue || []
          ).join(", ")}`
        );

        const nextKey = NEXT_KEY_FOR_WALL[wallDone];
        const nextStep = STEP_SEQUENCE[nextKey];
        if (nextStep !== undefined) {
          setCurrentStep(nextStep);
        }
        schedulePoll(1500);
        return;
      }

      schedulePoll(3000);
    } catch (err) {
      console.error("Polling error:", err);
      schedulePoll(4000);
    }
  };

  // --------------------------------------------------------
  // NEXT BUTTON
  // --------------------------------------------------------
  const handlePlacementNext = () => {
    if (currentStep === 0) startPhaseOne();
    if (currentStep === 4) startPhaseTwo();
  };

  // --------------------------------------------------------
  // INSTRUCTION TEXT
  // --------------------------------------------------------
  const getInstruction = () => {
    if (currentStep === 0)
      return (
        <>
          Position robot for <b>Wall 2</b>. Press Next (HOME check will run).
        </>
      );
    if (currentStep === 4)
      return (
        <>
          Reposition robot for <b>Wall 1</b>. Press Next (HOME check will run).
        </>
      );

    if (currentStep >= 1 && currentStep <= 3)
      return (
        <>
          Currently marking <b>Wall {currentStep + 1}</b>.
        </>
      );

    if (currentStep >= 5 && currentStep <= 7) {
      const w = currentStep === 5 ? 5 : currentStep === 6 ? 6 : 1;
      return (
        <>
          Currently marking <b>Wall {w}</b>.
        </>
      );
    }

    if (currentStep === 8) return <>Marking complete!</>;
    return <>...</>;
  };

  const handleExit = () => window.close();

  // --------------------------------------------------------
  // CLEAN UP ON UNMOUNT
  // --------------------------------------------------------
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      clearPolling();
    };
  }, []);

  // --------------------------------------------------------
  // UI RENDER
  // --------------------------------------------------------
  return (
    <>
      <div className="flex flex-col items-center mb-8">
        <h2 className="text-4xl font-bold">Marking of PBU (6-Wall Flow)</h2>

        <ul className="steps w-full max-w-4xl mt-4">
          {STEPS.map((label, i) => (
            <li
              key={label}
              className={i === currentStep ? "step step-primary" : "step"}
            >
              {label}
            </li>
          ))}
        </ul>
      </div>

      <div className="flex flex-row gap-6 justify-center">
        {/* MAIN IMAGE */}
        <div className="card bg-base-100 shadow-md max-w-2xl">
          <img
            src={STEP_IMAGES[currentStep]}
            className="w-full h-auto max-h-[70vh] object-contain"
          />
        </div>

        {/* RIGHT PANEL */}
        <div className="flex flex-col justify-between w-[420px]">
          <div className="menu bg-base-200 rounded-box p-5 shadow-md">
            <p className="text-2xl font-semibold">Instructions:</p>
            <p className="text-xl mt-2">{getInstruction()}</p>

            {errorMessage && (
              <p className="text-red-500 text-sm mt-2 whitespace-pre-line">
                {errorMessage}
              </p>
            )}
          </div>

          {/* HOME CHECK TABLE (only at placement steps) */}
          {(currentStep === 0 || currentStep === 4) &&
            homeCheckRows.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg mt-4 overflow-hidden">
                <table className="w-full text-sm text-black">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-2 text-left">Axis</th>
                      <th className="px-4 py-2 text-right">Current</th>
                      <th className="px-4 py-2 text-right">Target</th>
                    </tr>
                  </thead>
                  <tbody>
                    {homeCheckRows.map((row) => (
                      <tr key={row.axis} className="border-t border-gray-200">
                        <td className="px-4 py-2 font-semibold">{row.axis}</td>
                        <td className="px-4 py-2 text-right">
                          {row.current !== undefined
                            ? Number(row.current).toFixed(3) + "°"
                            : "-"}
                        </td>
                        <td className="px-4 py-2 text-right">
                          {Number(row.target).toFixed(3) + "°"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

          <div className="flex flex-col items-center mt-6 gap-4">
            {(currentStep === 0 || currentStep === 4) && (
              <button
                className="btn btn-primary px-6 py-3"
                onClick={handlePlacementNext}
              >
                Next
              </button>
            )}

            {isMarkingStep(currentStep) && !paused && (
              <button
                className="btn btn-warning px-6 py-3"
                onClick={pauseMarking}
              >
                Pause
              </button>
            )}

            {isMarkingStep(currentStep) && paused && (
              <button
                className="btn btn-success px-6 py-3"
                onClick={resumeMarking}
              >
                Continue
              </button>
            )}

            {/* Retry shows ONLY when there is backend error */}
            {isMarkingStep(currentStep) && hasError && (
              <button
                className="btn btn-error px-6 py-3 text-white"
                onClick={retryCurrentWall}
              >
                Retry Current Wall
              </button>
            )}

            {isFinalStep && (
              <button
                className="btn btn-error px-6 py-3 text-white"
                onClick={handleExit}
              >
                Exit
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default SixWallFlow;
