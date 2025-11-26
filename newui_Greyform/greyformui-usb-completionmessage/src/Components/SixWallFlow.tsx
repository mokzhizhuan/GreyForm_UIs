import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

import placementOne from "../assets/six_wall_flow/6_wall_flow_placement1.jpg";
import placementTwo from "../assets/six_wall_flow/6_wall_flow_placement2.jpg";
import wallMarking1 from "../assets/six_wall_flow/wall_marking_6_walls1.jpg";
import wallMarking2 from "../assets/six_wall_flow/wall_marking_6_walls2.jpg";
import { API_BASE_URL } from "./config";

type StepStatus = "idle" | "pending" | "error";

interface MarkingStatusResponse {
  currentWall?: number | null;
  progressPercent?: number | null;
  done?: boolean;
  paused?: boolean;
  message?: string;
}

interface WallRow {
  [key: string]: any;
}

interface WallInfo {
  wall: string; // "1", "2", "3", ...
  count: number;
  rows: WallRow[];
}

interface SixWallFlowProps {
  walls: WallInfo[];
  maxWall: number;
}

/**
 * Step indexes (6-wall flow):
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
const steps = [
  "Placement",
  "Wall 2",
  "Wall 3",
  "Wall 4",
  "Placement 2",
  "Wall 5",
  "Wall 6",
  "Wall 1",
  "Marking Complete",
];

const images = [
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

const SixWallFlow: React.FC<SixWallFlowProps> = ({ walls, maxWall, excelfile }) => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [status, setStatus] = useState<StepStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);

  // 0 = idle, 1 = phase1 (walls 2–4), 2 = phase2 (walls 5–6–1)
  const [autoModePhase, setAutoModePhase] = useState<0 | 1 | 2>(0);
  const steps = ["Placement 1", "Wall 2", "Wall 3", "Wall 4", "Placement 2", "Wall 5", "Wall 6", "Wall 1", "Marking Complete"];
  const [paused, setPaused] = useState<boolean>(false);
  const [pausedAfterWall, setPausedAfterWall] = useState<number | null>(null);
  const [loadingPause, setLoadingPause] = useState(false);
  const [loadingContinue, setLoadingContinue] = useState(false);

  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef<boolean>(false);
  const retryCountRef = useRef<number>(0);
  const phase: 1 | 2 =
  currentStep <= 3   // Placement + Wall2 + Wall3 + Wall4
    ? 1              // Phase 1
    : 2;    
  const isFinalStep = currentStep === steps.length - 1;

  // ------------------------------------
  // Auto-start ROS core + listener
  // ------------------------------------
  useEffect(() => {
    mountedRef.current = true;

    (async () => {
      try {
        await axios.post(`${API_BASE_URL}/roscore/start`);
        console.log("ROS core + listener started");
      } catch (e) {
        console.error("Failed to start ROS:", e);
      }
    })();

    return () => {
      mountedRef.current = false;
      if (pollingRef.current) clearTimeout(pollingRef.current);
    };
  }, []);

  // ------------------------------------
  // Wall -> step index mapping
  // ------------------------------------
  const wallNumberToStepIndex = (wall: number): number => {
    if (phase === 1) {
    if (wall === 2) return 1;
    if (wall === 3) return 2;
    if (wall === 4) return 3;
  }

  // Phase 2 sequence
  if (phase === 2) {
    if (wall === 5) return 4;
    if (wall === 6) return 5;
    if (wall === 1) return 6;
  }

  return 0;
  };
  // ------------------------------------
  // Phase 1: mark walls 2, 3, 4
  // ------------------------------------
  const startPhaseOne = async () => {
    setStatus("pending");
    setErrorMessage(null);
    setProgress(null);
    setPaused(false);
    setPausedAfterWall(null);

    try {
      await axios.post(`${API_BASE_URL}/marking/start`, {
        max_wall: maxWall,
        phase: 1,
        walls,
        excelfile
      });

      await axios.post(`${API_BASE_URL}/marking/run`);

      setAutoModePhase(1);
      setCurrentStep(1); // wall 2
      retryCountRef.current = 0;
      scheduleNextPoll(1000);
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          err?.message ||
          "Failed to start phase 1 marking."
      );
      setAutoModePhase(0);
    }
  };

  // ------------------------------------
  // Pause / Continue
  // ------------------------------------
  const handlePauseClick = async () => {
    try {
      setLoadingPause(true);
      setErrorMessage(null);

      // Tell backend: pause after this wall
      const res = await axios.post(`${API_BASE_URL}/marking/pause`);
      if (res.data?.paused) {
        // We don't stop immediately; backend will finish current wall.
        // UI will react when /status shows paused = true and currentWall stops changing.
        setPaused(true);
      }
    } catch (err: any) {
      setErrorMessage("Failed to request pause.");
    } finally {
      setLoadingPause(false);
    }
  };

  const handleContinueClick = async () => {
    try {
      setLoadingContinue(true);
      setErrorMessage(null);
      setPaused(false);
      setPausedAfterWall(null);

      // Backend resumes next wall; UI will see that via polling
      await axios.post(`${API_BASE_URL}/marking/continue`);

      // We DO NOT change step immediately (Option D).
      // We wait for /marking/status to report the new currentWall.
      retryCountRef.current = 0;
      scheduleNextPoll(1000);
    } catch (err: any) {
      setErrorMessage("Failed to continue marking.");
    } finally {
      setLoadingContinue(false);
    }
  };

  // ------------------------------------
  // Polling
  // ------------------------------------
  const scheduleNextPoll = (delayMs: number = 2000) => {
    if (!mountedRef.current) return;
    if (pollingRef.current) clearTimeout(pollingRef.current);
    pollingRef.current = window.setTimeout(fetchMarkingStatus, delayMs);
  };

  const fetchMarkingStatus = async () => {
  const res = await axios.get(`${API_BASE_URL}/marking/status`);
  const data = res.data;

  // ----------------------------------------
  // ⭐ 1. WALL STARTED  → update UI to correct wall step
  // ----------------------------------------
  if (data.startedWall) {
    const w = Number(data.startedWall);

    let stepIndex = null;

    if (w === 2) stepIndex = 1;
    if (w === 3) stepIndex = 2;
    if (w === 4) stepIndex = 3;
    if (w === 5) stepIndex = 5;
    if (w === 6) stepIndex = 6;
    if (w === 1) stepIndex = 7;

    if (stepIndex !== null) {
      setCurrentStep(stepIndex);
    }
  }

  // ----------------------------------------
  // ⭐ 2. WALL COMPLETED  → detect transitions
  // ----------------------------------------
  if (data.doneWall) {
    const completed = Number(data.doneWall);
    console.log("Wall completed:", completed);

    // ⭐ After finishing wall 4 → jump to Placement 2 (step 4)
    if (completed === 4) {
      setCurrentStep(4);   // Placement 2
      setPaused(true);     // pause until user presses Start again
      return;              // stop status polling
    }

    // ⭐ After finishing wall 1 → go to Marking Complete (step 8)
    if (completed === 1) {
      setCurrentStep(8);   // Marking Complete
      setPaused(true);
      return;
    }
  }

  // Continue polling
  scheduleNextPoll();
};
  // ------------------------------------
  // Phase 2: mark walls 5, 6, 1
  // ------------------------------------
  const startPhaseTwo = async () => {
    setStatus("pending");
    setErrorMessage(null);
    setProgress(null);
    setPaused(false);
    setPausedAfterWall(null);

    try {
      await axios.post(`${API_BASE_URL}/marking/start`, {
        max_wall: maxWall,
        phase: 2,
        walls,
        excelfile
      });

      await axios.post(`${API_BASE_URL}/marking/run`);

      setAutoModePhase(2);
      setCurrentStep(5); // wall 5
      retryCountRef.current = 0;
      scheduleNextPoll(1000);
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          err?.message ||
          "Failed to start phase 2 marking."
      );
    }
  };
  // ------------------------------------
  // Placement "Next" button
  // ------------------------------------
  const handlePlacementNext = () => {
    if (currentStep === 0) {
      // Placement 1 → start phase 1 (walls 2, 3, 4)
      startPhaseOne();
    } else if (currentStep === 4) {
      // Placement 2 → start phase 2 (walls 5, 6, 1)
      startPhaseTwo();
    }
  };

  // ------------------------------------
  // Instruction text
  // ------------------------------------
  const getInstructionContent = (): React.ReactNode => {
    if (isFinalStep) {
      return <>Marking complete! You may now proceed to turn off the robot.</>;
    }

    if (currentStep === 0) {
      return (
        <>
          Position the robot facing <strong>wall two</strong> and{" "}
          <strong>1m away</strong> from the wall. Press{" "}
          <strong>Next</strong> to start marking walls 2, 3 and 4.
        </>
      );
    }

    if (currentStep === 4) {
      return (
        <>
          Reposition the robot for <strong>second placement</strong> facing{" "}
          <strong>wall one</strong> and <strong>1m away</strong> from the wall.
          Press <strong>Next</strong> to continue marking walls 5, 6 and 1.
        </>
      );
    }

    if (paused && pausedAfterWall != null) {
      return (
        <>
          Marking is <strong>paused</strong> after finishing{" "}
          <strong>wall {pausedAfterWall}</strong>. Press{" "}
          <strong>Continue</strong> to start the next wall.
        </>
      );
    }

    if (currentStep >= 1 && currentStep <= 3) {
      return (
        <>
          Currently marking <strong>wall {currentStep + 1}</strong>. Please
          wait.
        </>
      );
    }

    if (currentStep >= 5 && currentStep <= 7) {
      const wallDisplay = currentStep === 7 ? 1 : currentStep === 5 ? 5 : 6;
      return (
        <>
          Currently marking <strong>wall {wallDisplay}</strong>. Please wait.
        </>
      );
    }

    return <>Starting marking process...</>;
  };

  // ------------------------------------
  // Status line text
  // ------------------------------------
  const getStatusLine = (): React.ReactNode => {
    if (isFinalStep) return null;

    // Placement steps: only show error
    if (currentStep === 0 || currentStep === 4) {
      if (status === "error") {
        return (
          <p className="text-red-600 mt-2">
            Error: {errorMessage || "Unknown error. Please retry."}
          </p>
        );
      }
      return null;
    }

    if (paused && pausedAfterWall != null) {
      return (
        <p className="mt-2">
          Paused after <strong>wall {pausedAfterWall}</strong>. Waiting for
          user to press Continue.
        </p>
      );
    }

    if (status === "error") {
      return (
        <p className="text-red-600 mt-2">
          Error: {errorMessage || "Polling error. Retrying..."}
        </p>
      );
    }

    if (status === "pending") {
      if (progress != null) {
        return (
          <p className="mt-2">
            Progress: <strong>{progress}%</strong>
          </p>
        );
      }
      return <p className="mt-2">Progress: In progress...</p>;
    }

    return null;
  };

  const handleExit = () => {
    try {
      window.close();
      setTimeout(() => {
        // If still open, alert the user to close manually
        alert("If the window did not close automatically, please close the window manually.");
      }, 300);
    } catch (e) {
        alert("Please close the window manually.");
    }
  };

  // ------------------------------------
  // Render
  // ------------------------------------
  return (
    <>
      {/* Header & Steps */}
      <div className="flex flex-col items-center justify-center mb-8">
        <h2 className="text-4xl md:text-5xl font-bold mb-6">
          Marking of PBU (6-Wall Flow)
        </h2>

        <ul className="steps w-full max-w-5xl mb-4">
          {steps.map((label, i) => (
            <li
              key={label}
              className={i === currentStep ? "step step-primary" : "step"}
            >
              {label}
            </li>
          ))}
        </ul>
      </div>

      {/* Main Body */}
      <div className="flex flex-row gap-6 w-full justify-center">
        {/* Left: layout image */}
        <div className="card bg-base-100 shadow-md max-w-2xl">
          <img
            src={images[currentStep]}
            alt={`6 Wall Flow ${steps[currentStep]}`}
            className="w-full h-auto max-h-[70vh] object-contain"
          />
        </div>

        {/* Right: instructions + buttons */}
        <div className="flex flex-col justify-between w-[420px]">
          <div className="menu bg-base-200 rounded-box p-5 text-black shadow-md">
            <p className="text-2xl font-semibold mb-2">Instructions:</p>
            <p className="text-xl leading-relaxed">
              {getInstructionContent()}
            </p>
            <div className="mt-3">{getStatusLine()}</div>
          </div>

          <div className="flex flex-col items-center mt-4 gap-4">
            {/* Placement buttons (0 and 4) */}
            {(currentStep === 0 || currentStep === 4) && !isFinalStep && (
              <button
                className="btn btn-primary md:btn-md lg:btn-lg py-2 px-4 border-b-4
                           border-gray-500 hover:border-gray-700 rounded"
                onClick={handlePlacementNext}
              >
                {status === "error"
                  ? "Retry"
                  : status === "pending"
                  ? "Starting..."
                  : "Next"}
              </button>
            )}

            {/* Pause / Continue only during marking steps */}
            {currentStep !== 0 &&
              currentStep !== 4 &&
              !isFinalStep && (
                <div className="flex gap-4">
                  <button
                    className="btn btn-warning md:btn-md lg:btn-lg py-2 px-4 border-b-4
                           border-gray-500 hover:border-gray-700 text-black rounded ? disabled:opacity-0"
                    onClick={handlePauseClick}
                    disabled={loadingPause || paused}
                  >
                    {loadingPause ? "Pausing..." : "Pause after this wall"}
                  </button>
                  <button
                    className="btn btn-success md:btn-md lg:btn-lg py-2 px-4 border-b-4
                           border-gray-500 hover:border-gray-700 text-black ? disabled:opacity-0"
                    onClick={handleContinueClick}
                    disabled={loadingContinue || !paused}
                  >
                    {loadingContinue ? "Continuing..." : "Continue next wall"}
                  </button>
                </div>
              )}

            {/* Exit on final step */}
            {isFinalStep && (
              <button
                className="btn btn-error md:btn-md lg:btn-lg py-2 px-4 border-b-4
                         border-gray-500 hover:border-gray-700 rounded
                         text-white"
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
