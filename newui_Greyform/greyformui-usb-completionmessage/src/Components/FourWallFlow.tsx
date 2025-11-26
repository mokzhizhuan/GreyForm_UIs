import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "./config";

// Images
import wallImg from "../assets/four_wall_flow/wall_marking_4_walls.jpg";

interface WallRow {
  [key: string]: any;
}

interface WallInfo {
  wall: string;
  count: number;
  rows: WallRow[];
}

interface ExecuteWallDataResponse {
  ok: boolean;
  error?: string;
}

interface FourWallFlowProps {
  walls: WallInfo[];
  maxWall: number;
  excelfile: string;        // <-- required for backend
}

const steps = ["Wall 2", "Wall 3", "Wall 4", "Wall 1", "Marking Complete"];

const images = [wallImg, wallImg, wallImg, wallImg, wallImg];

export default function FourWallFlow({ walls, maxWall, excelfile }: FourWallFlowProps) {
  const [currentStep, setCurrentStep] = useState(0); // start on Wall 2
  const [status, setStatus] = useState<"idle" | "pending" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);
  const [paused, setPaused] = useState(false);
  const [autoMode, setAutoMode] = useState(false);

  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef(true);
  const retryCountRef = useRef(0);

  // -----------------------
  // Map wall → UI step
  // -----------------------
  const wallToStep = (wall: number) => {
    if (wall === 2) return 0;
    if (wall === 3) return 1;
    if (wall === 4) return 2;
    if (wall === 1) return 3;
    return 0;
  };

  // -----------------------
  // Execute one wall block
  // -----------------------
  async function executeWallDataForWall(wallId: string) {
    const wallData = walls.find((w) => w.wall === wallId);
    if (!wallData) throw new Error(`Wall "${wallId}" not found`);

    const res = await axios.post<ExecuteWallDataResponse>(
      `${API_BASE_URL}/execute_wall_data`,
      wallData.rows
    );
    return res.data;
  }

  // -----------------------
  // Polling helper
  // -----------------------
  const schedulePoll = (delay = 2000) => {
    if (!mountedRef.current) return;
    if (pollingRef.current) clearTimeout(pollingRef.current);
    pollingRef.current = window.setTimeout(fetchStatus, delay);
  };

  // -----------------------
  // Start ROS + listener
  // -----------------------
  async function startRoscore() {
    try {
      await axios.post(`${API_BASE_URL}/roscore/start`);
    } catch (e) {
      console.warn("ROS already running or failed:", e);
    }
  }

  // -----------------------
  // Start marking process
  // -----------------------
  async function startMarking() {
    try {
      setStatus("pending");
      setErrorMessage(null);
      setAutoMode(true);

      await axios.post(`${API_BASE_URL}/marking/start`, {
        max_wall: maxWall,   // always 4
        walls,
        excelfile,
      });

      await axios.post(`${API_BASE_URL}/marking/run`);

      schedulePoll(1000);
    } catch (e: any) {
      setErrorMessage(e?.message ?? "Failed to start marking");
      setStatus("error");
    }
  }

  // -----------------------
  // Poll backend /marking/status
  // -----------------------
  async function fetchStatus() {
    if (!mountedRef.current) return;

    try {
      const res = await axios.get(`${API_BASE_URL}/marking/status`);
      const data = res.data;

      // wall started
      if (data.startedWall) {
        const w = Number(data.startedWall);
        setCurrentStep(wallToStep(w));
      }

      // wall done
      if (data.doneWall) {
        const w = Number(data.doneWall);
        if (w === 1) {
          // Last wall complete
          setCurrentStep(4); // step index 4 = "Marking Complete"
          setStatus("idle");
          return;
        }
      }

      setStatus("pending");
      retryCountRef.current = 0;
      schedulePoll();
    } catch (e) {
      retryCountRef.current++;
      if (retryCountRef.current > 5) {
        setStatus("error");
        setErrorMessage("Polling failed repeatedly");
        return;
      }
      schedulePoll(3000);
    }
  }

  // -----------------------
  // Pause / Continue toggle button
  // -----------------------
  const handlePauseContinue = async () => {
    if (!paused) {
      // → PAUSE
      try {
        const res = await axios.post(`${API_BASE_URL}/marking/pause`);
        if (res.data?.paused) setPaused(true);
      } catch {
        setErrorMessage("Failed to pause marking");
      }
    } else {
      // → CONTINUE
      try {
        await axios.post(`${API_BASE_URL}/marking/continue`);
        setPaused(false);
      } catch {
        setErrorMessage("Failed to continue marking");
      }
    }
  };

  // -----------------------
  // Component Mount
  // -----------------------
  useEffect(() => {
    mountedRef.current = true;
    startRoscore().finally(() => startMarking());

    return () => {
      mountedRef.current = false;
      if (pollingRef.current) clearTimeout(pollingRef.current);
    };
  }, []);

  const isFinalStep = currentStep === steps.length - 1;

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
            <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
              <button onClick={handlePauseClick} disabled={loadingPause || paused}>
                {loadingPause ? "Pausing..." : "Pause"}
              </button>
              <button
                onClick={handleContinueClick}
                disabled={loadingContinue || !paused}
              >
                {loadingContinue ? "Continuing..." : "Continue"}
              </button>
            </div>
          {!autoMode && (
            <button
              className={`btn btn-primary md:btn-md lg:btn-lg py-2 px-4 border-b-4
                           border-gray-500 hover:border-gray-700 rounded 
                           ${status === "pending" ? "loading" : ""}`}
              onClick={startMarking}
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

