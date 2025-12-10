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
  lineCount?: number;
  rowTotals?: Record<number, number>;
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

// Map wall → step index
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

// Next wall mapping
const NEXT_KEY_FOR_WALL: Record<number, number | "P2" | "DONE"> = {
  2: 3,
  3: 4,
  4: "P2",
  5: 6,
  6: 1,
  1: "DONE",
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

  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef(false);
  const currentStepRef = useRef(0);

  const isFinalStep = currentStep === 8;

  useEffect(() => {
    currentStepRef.current = currentStep;
  }, [currentStep]);

  const isMarkingStep = (step: number) =>
    [1, 2, 3, 5, 6, 7].includes(step);

  const clearPolling = () => {
    if (pollingRef.current) clearTimeout(pollingRef.current);
  };

  const schedulePoll = (ms = 1500) => {
    if (!mountedRef.current) return;
    clearPolling();
    pollingRef.current = window.setTimeout(fetchStatus, ms);
  };

  // --------------------------------------------------------
  // NORMALIZE wallDetails KEYS
  // --------------------------------------------------------
  const normalizedDetails: Record<string, WallRow[]> = {};
  for (const [key, rows] of Object.entries(wallDetails)) {
    const m = key.match(/\d+/);
    const label = m ? `wall_${m[0]}` : key;
    normalizedDetails[label] = rows ?? [];
  }

  const getRowCountForWall = (wallNum: number) =>
    normalizedDetails[`wall_${wallNum}`]?.length ?? 0;

  // --------------------------------------------------------
  // HOME CHECK LOGIC
  // --------------------------------------------------------
  const [homeCurrentRax, setHomeCurrentRax] = useState<Record<string, number> | null>(null);
  const [homeTargetJoints, setHomeTargetJoints] = useState<Record<string, number> | null>(null);

  const requestHomeCheckForWall = async (label: string) => {
    try {
      const res = await axios.post(`${API_BASE_URL}/marking/homecheck`, {
        target: label,
      });

      const raw = res.data.output ?? "";
      const arr = raw.split(/\r?\n/).map(s => s.trim()).filter(Boolean);

      const raxLine = arr.find(l => l.includes("rax_1"));
      if (raxLine) {
        try {
          setHomeCurrentRax(JSON.parse(raxLine.replace(/'/g, '"')));
        } catch {}
      }

      const targetLine = arr.find(l => l.includes("j0"));
      if (targetLine) {
        try {
          setHomeTargetJoints(JSON.parse(targetLine.replace(/'/g, '"')));
        } catch {}
      }

      const last = arr[arr.length - 1];
      const ok = last === "True";

      if (!ok) setErrorMessage("Robot NOT in HOME position");

      return ok;
    } catch {
      setErrorMessage("Home check failed.");
      return false;
    }
  };

  const homeCheckRows =
    homeCurrentRax && homeTargetJoints
      ? Object.entries(homeTargetJoints).map(([key, target], idx) => ({
          axis: key.toUpperCase(),
          current: homeCurrentRax[`rax_${idx + 1}`],
          target,
        }))
      : [];

  // --------------------------------------------------------
  // START PHASES
  // --------------------------------------------------------
  const startPhaseOne = async () => {
    const walls = ["wall_2", "wall_3", "wall_4"].map(label => ({
      wall: label,
      rows: normalizedDetails[label] ?? [],
    }));

    await axios.post(`${API_BASE_URL}/marking/start`, {
      walls,
      excelfile,
      meshfile,
      folder: folderdirectory,
      phase: 1,
      max_wall: maxWall,
    });

    setCurrentStep(1);
    schedulePoll(500);
  };

  const startPhaseTwo = async () => {
    const walls = ["wall_5", "wall_6", "wall_1"].map(label => ({
      wall: label,
      rows: normalizedDetails[label] ?? [],
    }));

    await axios.post(`${API_BASE_URL}/marking/start`, {
      walls,
      excelfile,
      meshfile,
      folder: folderdirectory,
      phase: 2,
      max_wall: maxWall,
    });

    setCurrentStep(5);
    schedulePoll(500);
  };

  // --------------------------------------------------------
  // POLLING
  // --------------------------------------------------------
  const fetchStatus = async () => {
    try {
      const res = await axios.get<MarkingStatusResponse>(`${API_BASE_URL}/marking/status`);
      const data = res.data;

      setPaused(Boolean(data.paused));
      setStatus(data.running ? "pending" : "idle");

      const stepNow = currentStepRef.current;

      // ACTIVE marking
      if (data.running && data.startedWall) {
        const wall = data.startedWall;
        const total = data.rowTotals?.[wall] ?? getRowCountForWall(wall);
        const lineCount = data.lineCount ?? 0;

        // 🔍 NON-VISIBLE COUNTER (console only)
        console.log(`Wall ${wall} → ${lineCount} / ${total} points done`);

        const stepIdx = STEP_SEQUENCE[wall];
        if (stepIdx !== undefined && stepIdx !== stepNow) {
          setCurrentStep(stepIdx);
        }

        // AUTO MOVE
        if (lineCount >= total && total > 0) {
          console.log(`🌟 Auto-advance → wall ${wall}`);
          const nextKey = NEXT_KEY_FOR_WALL[wall];
          const nextStep = STEP_SEQUENCE[nextKey];
          if (nextStep !== undefined) setCurrentStep(nextStep);
        }

        schedulePoll(3000);
        return;
      }

      // IDLE fallback
      if (!data.running && data.doneWall !== null) {
        const w = data.doneWall;
        console.log(`✅ Backend confirms wall ${w} complete`);

        const nextKey = NEXT_KEY_FOR_WALL[w];
        const nextStep = STEP_SEQUENCE[nextKey];
        if (nextStep !== undefined) setCurrentStep(nextStep);

        schedulePoll(1500);
        return;
      }

      schedulePoll(1500);
    } catch (err) {
      console.error("Polling error:", err);
      schedulePoll(3000);
    }
  };

  // --------------------------------------------------------
  // Placement Button
  // --------------------------------------------------------
  const handlePlacementNext = () => {
    if (currentStep === 0) startPhaseOne();
    if (currentStep === 4) startPhaseTwo();
  };

  // --------------------------------------------------------
  // Instructions
  // --------------------------------------------------------
  const getInstruction = () => {
    if (currentStep === 0)
      return <>Position robot for <b>Wall 2</b>. Press Next.</>;

    if (currentStep === 4)
      return <>Reposition robot for <b>Wall 1</b>. Press Next.</>;

    if (currentStep >= 1 && currentStep <= 3)
      return <>Currently marking <b>Wall {currentStep + 1}</b>.</>;

    if (currentStep >= 5 && currentStep <= 7) {
      const w = currentStep === 5 ? 5 : currentStep === 6 ? 6 : 1;
      return <>Currently marking <b>Wall {w}</b>.</>;
    }

    if (currentStep === 8) return <>Marking complete!</>;

    return <>...</>;
  };

  const handleExit = () => window.close();

  // --------------------------------------------------------
  // MOUNT
  // --------------------------------------------------------
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      clearPolling();
    };
  }, []);

  // --------------------------------------------------------
  // RENDER UI
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
        {/* IMAGE */}
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
              <p className="text-red-500 text-sm mt-2">{errorMessage}</p>
            )}
          </div>

          {/* HOME CHECK TABLE */}
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

          {/* BUTTONS */}
          <div className="flex flex-col items-center mt-6 gap-4">
            {(currentStep === 0 || currentStep === 4) && (
              <button className="btn btn-primary px-6 py-3" onClick={handlePlacementNext}>
                Next
              </button>
            )}

            {isMarkingStep(currentStep) && !paused && (
              <button className="btn btn-warning px-6 py-3" onClick={pauseMarking}>
                Pause
              </button>
            )}

            {isMarkingStep(currentStep) && paused && (
              <button className="btn btn-success px-6 py-3" onClick={resumeMarking}>
                Continue
              </button>
            )}

            {isFinalStep && (
              <button className="btn btn-error px-6 py-3 text-white" onClick={handleExit}>
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
