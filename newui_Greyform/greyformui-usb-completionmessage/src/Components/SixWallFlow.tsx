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
  queue: number[];
  maxWalls: number;
  phase: number | null;
  excelFile?: string;
  meshFile?: string;
}

interface WallRow {
  [key: string]: any;
}

interface SixWallFlowProps {
  wallDetails: Record<number, WallRow[]>;
  maxWall: number;
  excelfile: string;
  meshfile: string;
}

// --------------------------------------------------------
// STEPS
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
  placementOne,   // 0
  wallMarking1,   // 1 (Wall 2)
  wallMarking1,   // 2 (Wall 3)
  wallMarking1,   // 3 (Wall 4)
  placementTwo,   // 4
  wallMarking2,   // 5 (Wall 5)
  wallMarking2,   // 6 (Wall 6)
  wallMarking2,   // 7 (Wall 1)
  wallMarking2,   // 8 (Complete)
];

// --------------------------------------------------------
// COMPONENT
// --------------------------------------------------------
const SixWallFlow: React.FC<SixWallFlowProps> = ({
  wallDetails,
  maxWall,
  excelfile,
  meshfile,
}) => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [status, setStatus] = useState<StepStatus>("idle");
  const [paused, setPaused] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef(false);
  const currentStepRef = useRef<number>(0);

  const phase1BreakPendingRef = useRef(false);
  const phase2CompletePendingRef = useRef(false);
  const lastHandledDoneWall = useRef<number | null>(null);

  const isFinalStep = currentStep === STEPS.length - 1;

  // --------------------------------------------------------
  // HELPERS
  // --------------------------------------------------------
  const wallToStep = (wall: number): number | null => {
    switch (wall) {
      case 2: return 1;
      case 3: return 2;
      case 4: return 3;
      case 5: return 5;
      case 6: return 6;
      case 1: return 7;
      default: return null;
    }
  };

  const isMarkingStep = (step: number) => [1, 2, 3, 5, 6, 7].includes(step);

  const clearPolling = () => {
    if (pollingRef.current) clearTimeout(pollingRef.current);
    pollingRef.current = null;
  };

  const schedulePoll = (ms = 2000) => {
    if (!mountedRef.current) return;
    clearPolling();
    pollingRef.current = window.setTimeout(fetchStatus, ms);
  };

  useEffect(() => {
    currentStepRef.current = currentStep;
  }, [currentStep]);

  // --------------------------------------------------------
  // API CALLS: PAUSE & RESUME
  // --------------------------------------------------------
  const pauseMarking = async () => {
    try {
      await axios.post(`${API_BASE_URL}/marking/pause`);
      setPaused(true);
      // Robot will finish current wall → running stays true until done.
      schedulePoll(500);
    } catch (e: any) {
      setErrorMessage(e.response?.data?.detail || "Failed to pause marking.");
    }
  };

  const resumeMarking = async () => {
    try {
      await axios.post(`${API_BASE_URL}/marking/continue`);
      setPaused(false);
      schedulePoll(500);
    } catch (e: any) {
      setErrorMessage(e.response?.data?.detail || "Failed to resume marking.");
    }
  };

  // --------------------------------------------------------
  // API: START PHASE ONE (Walls 2, 3, 4)
  // --------------------------------------------------------
  const startPhaseOne = async () => {
    try {
      const walls = [2, 3, 4].map(w => ({ wall: w, rows: wallDetails[w] ?? [] }));

      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls,
        excelfile,
        meshfile,
        phase: 1,
        max_wall: 6,
      });

      lastHandledDoneWall.current = null;
      setCurrentStep(1);
      schedulePoll(500);

    } catch (e: any) {
      setErrorMessage(e.response?.data?.detail || "Failed to start phase 1.");
    }
  };

  // --------------------------------------------------------
  // API: START PHASE TWO (Walls 5, 6, 1)
  // --------------------------------------------------------
  const startPhaseTwo = async () => {
    try {
      const walls = [5, 6, 1].map(w => ({ wall: w, rows: wallDetails[w] ?? [] }));

      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls,
        excelfile,
        meshfile,
        phase: 2,
        max_wall: 6,
      });

      lastHandledDoneWall.current = null;
      setCurrentStep(5);
      schedulePoll(500);

    } catch (e: any) {
      setErrorMessage(e.response?.data?.detail || "Failed to start phase 2.");
    }
  };

  // --------------------------------------------------------
  // POLLING LOGIC
  // --------------------------------------------------------
  const fetchStatus = async () => {
    try {
      const res = await axios.get<MarkingStatusResponse>(
        `${API_BASE_URL}/marking/status`
      );
      const data = res.data;

      setPaused(Boolean(data.paused));
      setStatus(data.running ? "pending" : "idle");

      // 1) Robot started wall → move UI
      if (data.startedWall) {
        const si = wallToStep(data.startedWall);
        if (si !== null) {
          setCurrentStep(si);
        }
      }

      // 2) After finishing a wall → handle stage transitions
      if (data.doneWall) {
        const completed = data.doneWall;

        if (completed === 4 && data.phase === 1) {
          phase1BreakPendingRef.current = true;
        }

        if (completed === 1 && data.phase === 2) {
          phase2CompletePendingRef.current = true;
        }
      }

      const stepNow = currentStepRef.current;

      // 🌟 PAUSE LOGIC: If paused but robot still running → WAIT
      if (paused && data.running) {
        schedulePoll(1000);
        return;
      }

      // 🌟 PAUSE LOGIC: Paused AND robot finished → show Continue button
      if (paused && !data.running) {
        schedulePoll(1500);
        return;
      }

      // PHASE BREAK: Wall 4 → Placement 2
      if (phase1BreakPendingRef.current) {
        const wall4Step = wallToStep(4);
        if (stepNow === wall4Step && !data.running) {
          setCurrentStep(4);
          setPaused(true);
          phase1BreakPendingRef.current = false;
          clearPolling();
          return;
        }
      }

      // PHASE COMPLETE: Wall 1 → Marking Complete
      if (phase2CompletePendingRef.current) {
        const wall1Step = wallToStep(1);
        if (stepNow === wall1Step && !data.running) {
          setCurrentStep(8);
          setPaused(true);
          phase2CompletePendingRef.current = false;
          clearPolling();
          return;
        }
      }

      // Continue polling if not done
      if (!isFinalStep) {
        schedulePoll(2000);
      } else {
        clearPolling();
      }

    } catch (err) {
      console.error("Polling error:", err);
      setStatus("error");
      schedulePoll(3000);
    }
  };

  // --------------------------------------------------------
  // USER ACTION (Next)
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
      return <>Position robot for <b>Wall 2</b>. Press Next.</>;
    if (currentStep === 4)
      return <>Reposition robot for <b>Wall 1</b>. Press Next.</>;
    if (currentStep >= 1 && currentStep <= 3)
      return <>Currently marking <b>Wall {currentStep + 1}</b>.</>;
    if (currentStep >= 5 && currentStep <= 7) {
      const w = currentStep === 5 ? 5 : currentStep === 6 ? 6 : 1;
      return <>Currently marking <b>Wall {w}</b>.</>;
    }
    if (currentStep === 8)
      return <>Marking complete! You may turn off the robot.</>;
    return <>...</>;
  };

  // --------------------------------------------------------
  // EXIT
  // --------------------------------------------------------
  const handleExit = () => {
    try {
      window.close();
      setTimeout(() => {
        alert("If the window did not close automatically, please close manually.");
      }, 300);
    } catch {
      alert("Please close the window manually.");
    }
  };

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
            <li key={label} className={i === currentStep ? "step step-primary" : "step"}>
              {label}
            </li>
          ))}
        </ul>
      </div>

      <div className="flex flex-row gap-6 justify-center">
        {/* IMG */}
        <div className="card bg-base-100 shadow-md max-w-2xl">
          <img
            src={STEP_IMAGES[currentStep]}
            className="w-full h-auto max-h-[70vh] object-contain"
          />
        </div>

        {/* SIDE PANEL */}
        <div className="flex flex-col justify-between w-[420px]">
          <div className="menu bg-base-200 rounded-box p-5 shadow-md">
            <p className="text-2xl font-semibold">Instructions:</p>
            <p className="text-xl mt-2">{getInstruction()}</p>
            <p className="text-xl mt-2 text-red-500">{errorMessage}</p>
          </div>

          <div className="flex flex-col items-center mt-4 gap-4">
            
            {/* Placement steps */}
            {(currentStep === 0 || currentStep === 4) && !isFinalStep && (
              <button className="btn btn-primary px-6 py-3" onClick={handlePlacementNext}>
                Next
              </button>
            )}

            {/* PAUSE BUTTON */}
            {isMarkingStep(currentStep) && !paused && (
              <button className="btn btn-warning px-6 py-3" onClick={pauseMarking}>
                Pause
              </button>
            )}

            {/* CONTINUE BUTTON */}
            {isMarkingStep(currentStep) && paused && (
              <button className="btn btn-success px-6 py-3" onClick={resumeMarking}>
                Continue
              </button>
            )}

            {/* FINAL EXIT */}
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
