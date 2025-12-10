// =============================
// FourWallFlow.tsx
// 4-Wall Flow with Placement + HomeCheck
// Uses same backend/status model as SixWallFlow
// =============================

import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

import wallImg from "../assets/four_wall_flow/wall_marking_4_walls.jpg";
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
  queue: string[]; // e.g. ["wall_3", "wall_4", "wall_1"]
  phase?: number | null;
  maxWalls?: number;
  folder?: string;
  meshFile?: string;
  excelMap?: Record<string, string>;
  lineCount?: number; // points done
  totalPoints?: number; // optional from backend
  rowTotals?: Record<number, number>;
  hasError?: boolean;
  errorSummary?: string | null;
}

interface WallRow {
  [key: string]: any;
}

interface FourWallFlowProps {
  wallDetails: Record<string, WallRow[]>; // e.g. { wall_1: [...], wall_2: [...] }
  maxWall: number;                        // should be 4 for 4-wall flow
  excelFiles: string[];                   // full paths for each wall_* excel
  meshfile: string;
  folderdirectory: string;
}

// --------------------------------------------------------
// UI STEPS
// Placement + 4 walls + complete
// --------------------------------------------------------
const STEPS = [
  "Placement",      // 0
  "Wall 2",         // 1
  "Wall 3",         // 2
  "Wall 4",         // 3
  "Wall 1",         // 4
  "Marking Complete", // 5
];

const STEP_IMAGES = [
  wallImg, // placement (no dedicated image yet)
  wallImg,
  wallImg,
  wallImg,
  wallImg,
  wallImg,
];

// wall → step
const STEP_SEQUENCE: Record<number | string, number> = {
  2: 1,
  3: 2,
  4: 3,
  1: 4,
  DONE: 5,
};

// next wall in the sequence
const NEXT_KEY_FOR_WALL: Record<number, number | "DONE"> = {
  2: 3,
  3: 4,
  4: 1,
  1: "DONE",
};

// helper: resolve wall from step
const wallFromStep = (step: number): number | null => {
  if (step === 1) return 2;
  if (step === 2) return 3;
  if (step === 3) return 4;
  if (step === 4) return 1;
  return null;
};

// --------------------------------------------------------
// COMPONENT
// --------------------------------------------------------
const FourWallFlow: React.FC<FourWallFlowProps> = ({
  wallDetails,
  maxWall,
  excelFiles,
  meshfile,
  folderdirectory,
}) => {
  const [currentStep, setCurrentStep] = useState(0); // start at Placement
  const [status, setStatus] = useState<StepStatus>("idle");
  const [paused, setPaused] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);
  const [homeCheckTriggered, setHomeCheckTriggered] = useState(false);
  const [errorWall, setErrorWall] = useState<number | null>(null);

  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef(false);
  const currentStepRef = useRef(0);

  const isFinalStep = currentStep === 5;
  const isMarkingStep = (s: number) => [1, 2, 3, 4].includes(s);

  useEffect(() => {
    currentStepRef.current = currentStep;
  }, [currentStep]);

  // --------------------------------------------------------
  // NORMALIZE wallDetails KEYS → "wall_X"
  // --------------------------------------------------------
  const normalized: Record<string, WallRow[]> = {};
  for (const [key, rows] of Object.entries(wallDetails)) {
    const match = key.match(/\d+/);
    const label = match ? `wall_${match[0]}` : key;
    normalized[label] = rows ?? [];
  }

  const getRowsForWallLabel = (label: string) => normalized[label] ?? [];

  const getRowCountForWallNumber = (num: number) =>
    normalized[`wall_${num}`]?.length ?? 0;

  // --------------------------------------------------------
  // PAUSE / RESUME
  // --------------------------------------------------------
  const pauseMarking = async () => {
    try {
      await axios.post(`${API_BASE_URL}/marking/pause`);
      setPaused(true);
    } catch (e) {
      console.error("Pause failed:", e);
      setErrorMessage("Failed to pause marking.");
    }
  };

  const resumeMarking = async () => {
    try {
      await axios.post(`${API_BASE_URL}/marking/continue`);
      setPaused(false);
    } catch (e) {
      console.error("Resume failed:", e);
      setErrorMessage("Failed to continue marking.");
    }
  };

  // --------------------------------------------------------
  // RETRY CURRENT WALL
  // --------------------------------------------------------
  const retryCurrentWall = async () => {
    const wallNum = wallFromStep(currentStepRef.current);
    if (!wallNum) return;

    try {
      await axios.post(`${API_BASE_URL}/marking/retry`, null, {
        params: { wall: wallNum },
      });
      console.log(`🔁 Retry requested for wall ${wallNum}`);
      setHasError(false);
      setErrorMessage(null);
      schedulePoll(1000);
    } catch (e) {
      console.error("Retry failed:", e);
      setErrorMessage("Retry failed. Please check logs.");
    }
  };

  // --------------------------------------------------------
  // HOME CHECK (Placement step → wall_2)
  // --------------------------------------------------------
  const [homeCurrentRax, setHomeCurrentRax] =
    useState<Record<string, number> | null>(null);
  const [homeTargetJoints, setHomeTargetJoints] =
    useState<Record<string, number> | null>(null);

  const requestHomeCheckForWall = async (
    targetLabel: string
  ): Promise<boolean> => {
    setHomeCheckTriggered(true);

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

  const homeCheckRows =
    homeCurrentRax && homeTargetJoints
      ? Object.entries(homeTargetJoints).map(([key, targetVal], idx) => ({
          axis: key.toUpperCase(),
          current: homeCurrentRax[`rax_${idx + 1}`],
          target: targetVal,
        }))
      : [];

  // --------------------------------------------------------
  // START MARKING (single phase → walls 2,3,4,1)
  // --------------------------------------------------------
  const startMarking = async () => {
    const orderedLabels = ["wall_2", "wall_3", "wall_4", "wall_1"];

    const wallsPayload = orderedLabels.map((label) => ({
      wall: label,
      rows: getRowsForWallLabel(label),
    }));

    console.log("▶ FourWallFlow startMarking walls payload:", wallsPayload);
    console.log("▶ FourWallFlow excelFiles payload:", excelFiles);

    try {
      setStatus("pending");
      setErrorMessage(null);

      // Pass excelFiles array as excelfile → backend builds excel_map
      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls: wallsPayload,
        excelfile: excelFiles, // array
        meshfile,
        folder: folderdirectory,
        max_wall: maxWall,
        phase: 1, // informational only
      });

      setCurrentStep(1); // Wall 2
      schedulePoll(500);
    } catch (e: any) {
      console.error("Failed to start marking:", e);
      setStatus("error");
      setErrorMessage(e?.message ?? "Failed to start marking.");
    }
  };

  // --------------------------------------------------------
  // POLLING STATUS
  // --------------------------------------------------------
  const clearPolling = () => {
    if (pollingRef.current !== null) {
      clearTimeout(pollingRef.current);
      pollingRef.current = null;
    }
  };

  const schedulePoll = (ms = 2000) => {
    if (!mountedRef.current) return;
    clearPolling();
    pollingRef.current = window.setTimeout(fetchStatus, ms);
  };

  const fetchStatus = async () => {
    try {
      const res = await axios.get<MarkingStatusResponse>(
        `${API_BASE_URL}/marking/status`
      );
      const data = res.data;

      console.log("📡 /marking/status (4-wall):", data);

      setPaused(Boolean(data.paused));
      setStatus(data.running ? "pending" : "idle");
      setHasError(Boolean(data.hasError));
      if (data.errorSummary) {
        setErrorMessage(data.errorSummary);
      }
      if (data.hasError && data.startedWall) {
          setErrorWall(data.startedWall);
        } else if (!data.hasError) {
          setErrorWall(null);
        }
      const stepNow = currentStepRef.current;

      // ACTIVE MARKING
      if (data.running && data.startedWall) {
        const wall = data.startedWall;
        const lineCount = data.lineCount ?? 0;

        const totalLocal = getRowCountForWallNumber(wall);
        const totalServer = data.totalPoints ?? totalLocal;
        const total = totalServer || totalLocal;

        // Hidden console log counter
        console.log(
          `🔢 [4-wall] Wall ${wall} → ${lineCount} / ${total} points done`
        );

        // Map wall → UI step
        const stepIdx = STEP_SEQUENCE[wall];
        if (stepIdx !== undefined && stepIdx !== stepNow) {
          setCurrentStep(stepIdx);
        }

        // AUTO-ADVANCE WHEN COMPLETED AND NO ERROR
        if (!data.hasError && total > 0 && lineCount >= total) {
          console.log(`🌟 [4-wall] Auto-advance from wall ${wall}`);
          const nextKey = NEXT_KEY_FOR_WALL[wall];
          const nextStep =
            typeof nextKey === "number"
              ? STEP_SEQUENCE[nextKey]
              : STEP_SEQUENCE["DONE"];

          if (nextStep !== undefined) {
            setCurrentStep(nextStep);
          }
        }

        schedulePoll(4000);
        return;
      }

      // ERROR STATE — do not auto-advance; wait for Retry
      if (!data.running && data.hasError && data.startedWall !== null) {
        const wall = data.startedWall;
        const lineCount = data.lineCount ?? 0;
        const totalLocal = getRowCountForWallNumber(wall);
        const totalServer = data.totalPoints ?? totalLocal;
        const total = totalServer || totalLocal;

        console.log(
          `❌ [4-wall] Wall ${wall} error: points ${lineCount}/${total} — waiting for Retry`
        );

        schedulePoll(3000);
        return;
      }

      // IDLE + DONE (no error) — fallback UI progress
      if (!data.running && data.doneWall !== null && !data.hasError) {
        const wallDone = data.doneWall;
        const nextKey = NEXT_KEY_FOR_WALL[wallDone];
        const nextStep =
          typeof nextKey === "number"
            ? STEP_SEQUENCE[nextKey]
            : STEP_SEQUENCE["DONE"];

        if (nextStep !== undefined) {
          setCurrentStep(nextStep);
        }

        schedulePoll(3000);
        return;
      }

      schedulePoll(4000);
    } catch (err) {
      console.error("Polling error (4-wall):", err);
      schedulePoll(5000);
    }
  };

  // --------------------------------------------------------
  // Placement "Next" button → HomeCheck + startMarking
  // --------------------------------------------------------
  const handlePlacementNext = async () => {
    if (currentStep !== 0) return;

    const ok = await requestHomeCheckForWall("wall_2");
    if (!ok) return;

    await startMarking();
  };

  // --------------------------------------------------------
  // Instructions
  // --------------------------------------------------------
  const getInstruction = () => {
    if (currentStep === 0)
      return (
        <>
          Position robot for <b>Wall 2</b>. Press Next (HOME check will run).
        </>
      );

    if (currentStep >= 1 && currentStep <= 3) {
      // step 1 → wall 2, 2 → 3, 3 → 4
      return (
        <>
          Currently marking <b>Wall {currentStep + 1}</b>.
        </>
      );
    }

    if (currentStep === 4) {
      return (
        <>
          Currently marking <b>Wall 1</b>.
        </>
      );
    }

    if (currentStep === 5) return <>Marking complete!</>;

    return <>...</>;
  };

  const handleExit = () => window.close();

  // --------------------------------------------------------
  // MOUNT / UNMOUNT
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
        <h2 className="text-4xl font-bold">Marking of PBU (4-Wall Flow)</h2>

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

          {/* HOME CHECK TABLE (Placement step only, when triggered and data exists) */}
          {currentStep === 0 &&
            homeCheckTriggered &&
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

          {/* BUTTONS */}
          <div className="flex flex-col items-center mt-6 gap-4">
            {/* Placement → Next (HOME check + start) */}
            {currentStep === 0 && (
              <button
                className="btn btn-primary px-6 py-3"
                onClick={handlePlacementNext}
              >
                Next
              </button>
            )}

            {/* Pause / Continue (only marking steps, no error) */}
            {isMarkingStep(currentStep) && !paused && !hasError && (
              <button
                className="btn btn-warning px-6 py-3"
                onClick={pauseMarking}
              >
                Pause
              </button>
            )}

            {isMarkingStep(currentStep) && paused && !hasError && (
              <button
                className="btn btn-success px-6 py-3"
                onClick={resumeMarking}
              >
                Continue
              </button>
            )}

            {/* Retry on error */}
            {isMarkingStep(currentStep) && hasError && (
                <button className="btn btn-error" onClick={retryCurrentWall}>
                  {errorWall
                    ? `Retry Current Wall ${errorWall}`
                    : "Retry Current Wall"}
                </button>
              )}


            {/* Exit at end */}
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

export default FourWallFlow;
