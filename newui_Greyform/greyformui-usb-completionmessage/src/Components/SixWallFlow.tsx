import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

import placementOne from "../assets/six_wall_flow/6_wall_flow_placement1.jpg";
import placementTwo from "../assets/six_wall_flow/6_wall_flow_placement2.jpg";
import wallMarking1 from "../assets/six_wall_flow/wall_marking_6_walls1.jpg";
import wallMarking2 from "../assets/six_wall_flow/wall_marking_6_walls2.jpg";

import { API_BASE_URL } from "./config";

type StepStatus = "idle" | "pending" | "error";

interface MarkingStatusResponse {
  running: boolean;
  paused: boolean;
  startedWall: number | null;  // backend: current running wall
  doneWall: number | null;     // backend: wall that just finished
  queue: number[];
  maxWalls: number;
  phase: number | null;        // ⭐ NEW from backend
  excelFile?: string;
  meshFile?: string;
}

interface WallRow {
  [key: string]: any;
}

interface WallInfo {
  wall: string;
  count: number;
  rows: WallRow[];
}

interface SixWallFlowProps {
  walls: WallInfo[];
  maxWall: number;
  excelfile: string;
  meshfile: string;
}

/**
 * UI Steps (index):
 * 0: Placement 1
 * 1: Wall 2
 * 2: Wall 3
 * 3: Wall 4
 * 4: Placement 2
 * 5: Wall 5
 * 6: Wall 6
 * 7: Wall 1
 * 8: Marking Complete
 */
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

const SixWallFlow: React.FC<SixWallFlowProps> = ({
  excelfile,
  meshfile,
}) => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [status, setStatus] = useState<StepStatus>("idle");
  const [paused, setPaused] = useState(false);
  const [pausedAfterWall, setPausedAfterWall] = useState<number | null>(null);
  const [loadingPause, setLoadingPause] = useState(false);
  const [loadingContinue, setLoadingContinue] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);

  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef(false);

  const isFinalStep = currentStep === STEPS.length - 1;

  // -------------------------------------------
  // Polling Helpers
  // -------------------------------------------
  const clearPolling = () => {
    if (pollingRef.current) clearTimeout(pollingRef.current);
    pollingRef.current = null;
  };

  const schedulePoll = (delayMs = 2000) => {
    if (!mountedRef.current) return;
    clearPolling();
    pollingRef.current = window.setTimeout(fetchStatus, delayMs);
  };

  // Map wall → UI step
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

  // -------------------------------------------
  // Phase 1 Start (Wall 2,3,4)
  // -------------------------------------------
  const startPhaseOne = async () => {
    try {
      setStatus("pending");
      setPaused(false);
      setErrorMessage(null);

      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls: [2, 3, 4],
        excelfile,
        meshfile,
        phase: 1,
        max_wall: 6,
      });

      setCurrentStep(1);
      schedulePoll(500);
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(err?.response?.data?.detail || "Failed to start Phase 1.");
    }
  };

  // -------------------------------------------
  // Phase 2 Start (Wall 5,6,1)
  // -------------------------------------------
  const startPhaseTwo = async () => {
    try {
      setStatus("pending");
      setPaused(false);
      setErrorMessage(null);

      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls: [5, 6, 1],
        excelfile,
        meshfile,
        phase: 2,
        max_wall: 6,
      });

      setCurrentStep(5);
      schedulePoll(500);
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(err?.response?.data?.detail || "Failed to start Phase 2.");
    }
  };

  // -------------------------------------------
  // PAUSE / CONTINUE
  // -------------------------------------------
  const handlePause = async () => {
    setLoadingPause(true);
    try {
      await axios.post(`${API_BASE_URL}/marking/pause`);
      setPaused(true);
    } finally {
      setLoadingPause(false);
    }
  };

  const handleContinue = async () => {
    setLoadingContinue(true);
    try {
      setPaused(false);
      setPausedAfterWall(null);
      await axios.post(`${API_BASE_URL}/marking/continue`);
      schedulePoll(500);
    } finally {
      setLoadingContinue(false);
    }
  };

  // -------------------------------------------
  // STATUS POLLING
  // -------------------------------------------
  const fetchStatus = async () => {
    try {
      const res = await axios.get<MarkingStatusResponse>(`${API_BASE_URL}/marking/status`);
      const data = res.data;

      setPaused(Boolean(data.paused));
      setStatus(data.running ? "pending" : "idle");

      // 1. Wall started → move UI to correct step
      if (data.startedWall) {
        const si = wallToStep(data.startedWall);
        if (si !== null) setCurrentStep(si);
      }

      // 2. Wall completed → drive core transitions
      if (data.doneWall) {
        const completed = data.doneWall;
        setPausedAfterWall(completed);

        // ⭐ IF PHASE 1 and finished WALL 4 → jump to Placement 2
        if (completed === 4 && data.phase === 1) {
          setCurrentStep(4);
          setPaused(true);
          clearPolling();
          return;
        }

        // ⭐ IF PHASE 2 and finished WALL 1 → Marking Complete
        if (completed === 1 && data.phase === 2) {
          setCurrentStep(8);
          setPaused(true);
          clearPolling();
          return;
        }
      }

      if (!isFinalStep) schedulePoll(2000);
      else clearPolling();

    } catch (err) {
      console.error("Polling error:", err);
      setStatus("error");
      schedulePoll(3000);
    }
  };

  // -------------------------------------------
  // Placement Button
  // -------------------------------------------
  const handlePlacementNext = () => {
    if (currentStep === 0) startPhaseOne();
    if (currentStep === 4) startPhaseTwo();
  };

  // -------------------------------------------
  // UI TEXT
  // -------------------------------------------
  const getInstruction = () => {
    if (currentStep === 0)
      return <>Position robot for <b>Wall 2</b> (1m away). Press Next.</>;

    if (currentStep === 4)
      return <>Reposition robot for <b>Wall 1</b>. Press Next to continue.</>;

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

  const handleExit = () => {
    try {
      window.close();
      setTimeout(() => {
        alert("If the window did not close automatically, please close the window manually.");
      }, 300);
    } catch (e) {
        alert("Please close the window manually.");
    }
  }

  // ----------------------------------------------------------------
  // Mount
  // ----------------------------------------------------------------
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      clearPolling();
    };
  }, []);

  // ----------------------------------------------------------------
  // Render
  // ----------------------------------------------------------------
  return (
    <>
      {/* Header */}
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

      {/* Main Content */}
      <div className="flex flex-row gap-6 justify-center">
        <div className="card bg-base-100 shadow-md max-w-2xl">
          <img
            src={STEP_IMAGES[currentStep]}
            alt="step"
            className="w-full h-auto max-h-[70vh] object-contain"
          />
        </div>

        <div className="flex flex-col justify-between w-[420px]">
          <div className="menu bg-base-200 rounded-box p-5 shadow-md">
            <p className="text-2xl font-semibold">Instructions:</p>
            <p className="text-xl mt-2">{getInstruction()}</p>

            {pausedAfterWall && paused && (
              <p className="mt-2">
                Paused after finishing <b>Wall {pausedAfterWall}</b>.
              </p>
            )}
          </div>

          <div className="flex flex-col items-center mt-4 gap-4">
            {/* Next button for placement */}
            {(currentStep === 0 || currentStep === 4) && !isFinalStep && (
              <button
                className="btn btn-primary px-6 py-3"
                onClick={handlePlacementNext}
              >
                Next
              </button>
            )}

            {/* Pause / Continue */}
            {currentStep !== 0 && currentStep !== 4 && !isFinalStep && (
              <div className="flex gap-4">
                <button
                  className="btn btn-warning px-6 py-3"
                  disabled={paused || loadingPause}
                  onClick={handlePause}
                >
                  {loadingPause ? "Pausing..." : "Pause after this wall"}
                </button>

                <button
                  className="btn btn-success px-6 py-3"
                  disabled={!paused || loadingContinue}
                  onClick={handleContinue}
                >
                  {loadingContinue ? "Continuing..." : "Continue next wall"}
                </button>
              </div>
            )}

            {/* Exit */}
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
