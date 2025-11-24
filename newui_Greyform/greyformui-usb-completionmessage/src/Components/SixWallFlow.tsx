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
  phase?: number | null; // 1 or 2 (optional)
  message?: string;
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

// Reuse same illustrative image; replace with more specific ones if available.
const images = [
  placementOne,
  wallMarking1,
  wallMarking1,
  wallMarking1,
  placementTwo, // second placement illustration (can create a new asset)
  wallMarking2,
  wallMarking2,
  wallMarking2,
  wallMarking2,
];

const SixWallFlow: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [status, setStatus] = useState<StepStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);

  const [autoModePhase, setAutoModePhase] = useState<0 | 1 | 2>(0); 
  // 0 = not started, 1 = auto marking walls 2-4, 2 = auto marking walls 5-6-1

  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef<boolean>(true);
  const retryCountRef = useRef<number>(0);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (pollingRef.current) clearTimeout(pollingRef.current);
    };
  }, []);

  const isFinalStep = currentStep === steps.length - 1;

  // Map wall number to step index for this flow
  const wallNumberToStepIndex = (wall: number): number => {
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

  const scheduleNextPoll = (delayMs: number = 2000) => {
    if (!mountedRef.current) return;
    if (pollingRef.current) clearTimeout(pollingRef.current);
    pollingRef.current = window.setTimeout(fetchMarkingStatus, delayMs);
  };

  const startPhaseOne = async () => {
    setStatus("pending");
    setErrorMessage(null);
    setProgress(null);

    try {
      const res = await axios.post(`${API_BASE_URL}/start_marking`, {
        phase: 1,
      });
      const initialWall: number | undefined = res.data?.currentWall;

      setAutoModePhase(1);
      setStatus("pending");

      if (initialWall && [2, 3, 4].includes(initialWall)) {
        setCurrentStep(wallNumberToStepIndex(initialWall));
      }
      retryCountRef.current = 0;
      scheduleNextPoll(1000);
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(
        err?.response?.data?.message ||
          err?.message ||
          "Failed to start phase 1 marking."
      );
      setAutoModePhase(0);
    }
  };

  const startPhaseTwo = async () => {
    setStatus("pending");
    setErrorMessage(null);
    setProgress(null);

    try {
      const res = await axios.post(`${API_BASE_URL}/resume_marking`, {
        phase: 2,
      });
      const initialWall: number | undefined = res.data?.currentWall;

      setAutoModePhase(2);
      setStatus("pending");

      if (initialWall && [5, 6, 1].includes(initialWall)) {
        setCurrentStep(wallNumberToStepIndex(initialWall));
      } else {
        // Wait for polling if not provided
      }
      retryCountRef.current = 0;
      scheduleNextPoll(1000);
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(
        err?.response?.data?.message ||
          err?.message ||
          "Failed to start phase 2 marking."
      );
      // Remain at placement 2 for retry
    }
  };

  const fetchMarkingStatus = async () => {
    // Only poll during auto phases
    if (!mountedRef.current || autoModePhase === 0) return;

    try {
      const res = await axios.get<MarkingStatusResponse>(
        `${API_BASE_URL}/marking_status`
      );
      const data = res.data;

      if (data.done) {
        setProgress(null);
        setCurrentStep(steps.length - 1);
        setStatus("idle");
        setAutoModePhase(0);
        return;
      }

      if (data.currentWall && [2,3,4,5,6,1].includes(data.currentWall)) {
        const newStep = wallNumberToStepIndex(data.currentWall);
        if (newStep !== currentStep) setCurrentStep(newStep);
      }

      if (
        typeof data.progressPercent === "number" &&
        data.progressPercent >= 0 &&
        data.progressPercent <= 100
      ) {
        setProgress(data.progressPercent);
      } else {
        setProgress(null);
      }

      setStatus("pending");
      retryCountRef.current = 0;
      scheduleNextPoll();
    } catch (err: any) {
      retryCountRef.current += 1;
      if (retryCountRef.current > 5) {
        setStatus("error");
        setErrorMessage(
          err?.response?.data?.message ||
            err?.message ||
            "Status polling failed."
        );
        return;
      }
      const backoff = Math.min(8000, 2000 * retryCountRef.current);
      scheduleNextPoll(backoff);
    }
  };

  const handlePlacementNext = () => {
    if (currentStep === 0) {
      startPhaseOne();
    } else if (currentStep === 4) {
      startPhaseTwo();
    }
  };

  // When phase 1 finishes (wall 4 complete) backend should stop advancing walls and not set done yet.
  // Frontend will stay at step 3 until backend indicates pause or operator moves manually to step 4.
  // Optionally: If backend sends a "phaseComplete":1 we could auto step to Placement 2.
  // For now, we assume we manually move to step 4 when current wall sequence (2-4) ends.
  // If you want automatic transition, add logic below (e.g., detect absence of currentWall for >N polls).

  // Instructions content
  const getInstructionContent = (): React.ReactNode => {
    if (isFinalStep) {
      return <>Marking complete! You may now proceed to turn off the robot.</>;
    }

    if (currentStep === 0) {
      return (
        <>
          Position the robot facing <strong>wall two</strong> and{" "}
          <strong>1m away</strong> from the wall.
        </>
      );
    }

    if (currentStep === 4) {
      return (
        <>
          Reposition the robot for <strong>second placement</strong> facing{" "}
          <strong>wall one</strong> and <strong>1m away</strong>{" "}
          from the wall. Press Next to continue marking walls 5, 6 and 1.
        </>
      );
    }

    if (currentStep >= 1 && currentStep <= 3) {
      return (
        <>
          Currently marking <strong>wall {currentStep + 1}</strong> please wait.
        </>
      );
    }

    if (currentStep >= 5 && currentStep <= 7) {
      // Steps 5->Wall5,6->Wall6,7->Wall1
      const wallDisplay =
        currentStep === 7 ? 1 : currentStep === 5 ? 5 : 6;
      return (
        <>
          Currently marking <strong>wall {wallDisplay}</strong> please wait.
        </>
      );
    }

    return <>Starting marking process...</>;
  };

  const getStatusLine = (): React.ReactNode => {
    if (isFinalStep) return null;

    // Placement steps show no progress
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

    // Auto marking steps
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
    } catch {
      // fallback
    }
  };

  return (
    <>
      <div className="flex flex-col items-center-safe justify-center mb-8">
        <h2 className="text-4xl md:text-5xl font-bold mb-8">
          Marking of PBU (6-Wall Flow)
        </h2>
        <ul className="steps w-full max-w-5xl">
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

      <div className="flex flex-row items-stretch gap-4 w-full">
        <div className="max-w-2xl card bg-base-100 shadow-sm flex-shrink-0">
          <img
            src={images[currentStep]}
            alt={`6 Wall Flow ${steps[currentStep]}`}
            className="block w-full h-auto max-h-[70vh] object-contain"
          />
        </div>

        <div className="flex flex-col justify-between w-max items-center-safe self-stretch">
          <div className="menu bg-base-200 rounded-box w-full max-h-full p-3 text-black">
            <p className="md:text-2xl">
              <b>Instructions:</b>
            </p>
            <p className="text-2xl">{getInstructionContent()}</p>
            {getStatusLine()}
          </div>

          {/* Buttons logic:
              - Placement steps (0 & 4): show Next with start/resume logic.
              - Final step: Exit.
              - Auto marking steps: no button.
          */}
          {currentStep === 0 && (
            <button
              className={`btn btn-primary md:btn-md lg:btn-lg py-2 px-4 border-b-4
                          border-gray-500 hover:border-gray-700 rounded 
                          ${status === "pending" ? "loading" : ""}`}
              onClick={startPhaseOne}
              disabled={status === "pending"}
            >
              {status === "error"
                ? "Retry Start"
                : status === "pending"
                ? "Starting..."
                : "Next"}
            </button>
          )}

          {currentStep === 4 && (
            <button
              className={`btn btn-primary md:btn-md lg:btn-lg py-2 px-4 border-b-4
                          border-gray-500 hover:border-gray-700 rounded 
                          ${status === "pending" ? "loading" : ""}`}
              onClick={startPhaseTwo}
              disabled={status === "pending"}
            >
              {status === "error"
                ? "Retry Resume"
                : status === "pending"
                ? "Resuming..."
                : "Next"}
            </button>
          )}

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
    </>
  );
};

export default SixWallFlow;