import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

import placementOne from "../assets/four_wall_flow/4_wall_flow_placement1.jpg";
import wallMarking from "../assets/four_wall_flow/wall_marking_4_walls.jpg";
import { API_BASE_URL } from "./config";

type StepStatus = "idle" | "pending" | "error";

interface MarkingStatusResponse {
  // Adjust these fields to match your backend contract
  currentWall?: number;     // 1 | 2 | 3 | 4 when in progress
  progressPercent?: number; // 0–100
  done?: boolean;           // true when all walls finished
  message?: string;
}
 interface WallRow {
  // You can make this stricter later; for now it's fine as a generic row.
  [key: string]: any;
}

interface WallInfo {
  wall: string;      // "1", "2", "3", ...
  count: number;     // number of rows for that wall
  rows: WallRow[];   // the actual rows to send to /execute_wall_data
}
  interface RunScriptResponse {
  ok: boolean;
  data: string[];
}
interface ExecuteWallDataResponse {
  ok: boolean;
  queued?: boolean;
  error?: string;
}
interface FourWallFlowProps {
  walls: WallInfo[];
  maxWall: number;
}
/**
 * Step indexes:
 * 0: Placement
 * 1: Wall 2
 * 2: Wall 3
 * 3: Wall 4
 * 4: Wall 1
 * 5: Marking Complete
 */
const steps = ["Placement", "Wall 2", "Wall 3", "Wall 4", "Wall 1", "Marking Complete"];
const images = [placementOne, wallMarking, wallMarking, wallMarking, wallMarking, wallMarking];

const FourWallFlow: React.FC<FourWallFlowProps> = ({ walls, maxWall }) => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [status, setStatus] = useState<StepStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);

  // Whether automatic marking mode has started (after first click)
  const [autoMode, setAutoMode] = useState<boolean>(false);

  // Polling refs & lifecycle
  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef<boolean>(true);
  const retryCountRef = useRef<number>(0);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
      }
    };
  }, []);

  // Translate a wall number (2,3,4,1) to a step index
  const wallNumberToStepIndex = (wall: number): number => {
    if (wall === 2) return 1;
    if (wall === 3) return 2;
    if (wall === 4) return 3;
    if (wall === 1) return 4;
    return 0;
  };
async function executeWallDataForWall(
  walls: WallInfo[],
  wallId: string
): Promise<ExecuteWallDataResponse> {
  const wallData = walls.find((w) => w.wall === wallId);

  if (!wallData) {
    throw new Error(`Wall "${wallId}" not found in walls array`);
  }

  const res = await axios.post<ExecuteWallDataResponse>(
    `${API_BASE_URL}/execute_wall_data`,
    wallData.rows
  );

  return res.data;
}

  const scheduleNextPoll = (delayMs: number = 2000) => {
    if (!mountedRef.current) return;
    if (pollingRef.current) clearTimeout(pollingRef.current);
    pollingRef.current = window.setTimeout(fetchMarkingStatus, delayMs);
  };

  const startMarking = async () => {
    setStatus("pending");
    setErrorMessage(null);
    setProgress(null);

    try {
      // Backend should trigger SSH script here.
      const res = await axios.post(`${API_BASE_URL}/start_marking`, {});
      const initialWall: number | undefined = res.data?.currentWall;

      setAutoMode(true);
      setStatus("pending");

      if (initialWall && [2, 3, 4, 1].includes(initialWall)) {
        setCurrentStep(wallNumberToStepIndex(initialWall));
      } else {
        // If backend does not report initial wall, we wait for /marking_status.
      }

      retryCountRef.current = 0;
      scheduleNextPoll(1000);
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(
        err?.response?.data?.message ||
          err?.message ||
          "Failed to start marking process."
      );
      setAutoMode(false);
    }
  };

  const fetchMarkingStatus = async () => {
    if (!mountedRef.current || !autoMode) return;

    try {
      const res = await axios.get<MarkingStatusResponse>(
        `${API_BASE_URL}/marking_status`
      );
      const data = res.data;

      if (data.done) {
        setProgress(null);
        setCurrentStep(steps.length - 1); // Marking Complete
        setStatus("idle");
        return;
      }

      if (data.currentWall && [2, 3, 4, 1].includes(data.currentWall)) {
        const newStep = wallNumberToStepIndex(data.currentWall);
        if (newStep !== currentStep) {
          setCurrentStep(newStep);
        }
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
            "Marking status polling failed."
        );
        return;
      }
      const backoff = Math.min(8000, 2000 * retryCountRef.current);
      scheduleNextPoll(backoff);
    }
  };

  const handleExit = () => {
    try {
      window.close();
    } catch {
      // Fallback if window.close is disallowed
    }
  };

  const isFinalStep = currentStep === steps.length - 1;

  const getInstructionContent = (): React.ReactNode => {
    if (!autoMode) {
      return (
        <>
          Position the robot facing <strong>wall two</strong> and{" "}
          <strong>1m away</strong> from the wall.
        </>
      );
    }

    if (isFinalStep) {
      return <>Marking complete! You may now proceed to turn off the robot.</>;
    }

    if (currentStep >= 1 && currentStep <= 4) {
      return (
        <>
          Currently marking <strong>wall {currentStep === 4 ? 1 : currentStep + 1}</strong> please wait.
        </>
      );
    }

    return <>Starting marking process...</>;
  };

  const getStatusLine = (): React.ReactNode => {
    if (!autoMode || isFinalStep) return null;

    if (status === "error") {
      return (
        <p className="text-red-600 mt-2">
          Error: {errorMessage || "Unknown error. Please refresh and retry."}
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

  return (
    <>
      <div className="flex flex-col items-center-safe justify-center mb-8">
        <h2 className="text-4xl md:text-5xl font-bold mb-8">Marking of PBU</h2>

        <ul className="steps w-full max-w-3xl">
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
            alt={`4 Wall Flow ${steps[currentStep]}`}
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

          {!autoMode && (
            <button
              className={`btn btn-primary md:btn-md lg:btn-lg py-2 px-4 border-b-4
                           border-gray-500 hover:border-gray-700 rounded 
                           ${status === "pending" ? "loading" : ""}`}
              onClick={startMarking}
              disabled={status === "pending"}
            >
              {status === "error"
                ? "Retry Start"
                : status === "pending"
                ? "Starting..."
                : "Next"}
            </button>
          )}

          {autoMode && isFinalStep && (
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

export default FourWallFlow;