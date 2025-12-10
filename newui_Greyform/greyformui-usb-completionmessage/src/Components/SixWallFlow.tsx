// =========================================================
// FINAL SixWallFlow.tsx
// With: Auto HomeCheck on Error + Retry + Point Counter
// =========================================================

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
interface WallRow {
  [key: string]: any;
}

interface MarkingStatusResponse {
  running: boolean;
  paused: boolean;
  startedWall: number | null;
  doneWall: number | null;
  queue: string[];
  phase: number | null;
  maxWalls: number;
  folder: string;
  excelMap: Record<number, string>;
  meshFile: string;
  lineCount: number;
  totalPoints: number;
  hasError: boolean;
  errorSummary?: string | null;
  rowTotals: Record<number, number>;
}

interface SixWallFlowProps {
  wallDetails: Record<string, WallRow[]>;
  maxWall: number;
  excelFiles: string[]; // wall_2, wall_3, wall_4, wall_5, wall_6, wall_1 mapping by index
  meshfile: string;
  folderdirectory: string;
}

// --------------------------------------------------------
// CONSTANTS (flow order + UI mapping)
// --------------------------------------------------------
const PHASE1_ORDER = ["wall_2", "wall_3", "wall_4"];
const PHASE2_ORDER = ["wall_5", "wall_6", "wall_1"];

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

const NEXT_KEY_FOR_WALL: Record<number, number | "P2" | "DONE"> = {
  2: 3,
  3: 4,
  4: "P2",
  5: 6,
  6: 1,
  1: "DONE",
};

const STEP_IMAGES = [
  placementOne, // 0
  wallMarking1, // 1
  wallMarking1, // 2
  wallMarking1, // 3
  placementTwo, // 4
  wallMarking2, // 5
  wallMarking2, // 6
  wallMarking2, // 7
  wallMarking2, // 8
];

const STEP_LABELS = [
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

// --------------------------------------------------------
// COMPONENT
// --------------------------------------------------------
const SixWallFlow: React.FC<SixWallFlowProps> = ({
  wallDetails,
  maxWall,
  excelFiles,
  meshfile,
  folderdirectory,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [paused, setPaused] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [errorWall, setErrorWall] = useState<number | null>(null);

  // homecheck state
  const [homeCheckRows, setHomeCheckRows] = useState<any[]>([]);
  const [homeCheckTriggered, setHomeCheckTriggered] = useState(false);

  const pollingRef = useRef<number | null>(null);
  const currentStepRef = useRef(0);

  useEffect(() => {
    currentStepRef.current = currentStep;
  }, [currentStep]);

  // -------------------------------------------------------
  // NORMALIZE WALL DETAILS
  // -------------------------------------------------------
  const normalized: Record<string, WallRow[]> = {};
  for (const [key, rows] of Object.entries(wallDetails)) {
    const m = key.match(/\d+/);
    const label = m ? `wall_${m[0]}` : key;
    normalized[label] = rows;
  }

  const getDetails = (label: string) => normalized[label] ?? [];
  const getRowCountForWall = (n: number) =>
    normalized[`wall_${n}`]?.length ?? 0;

  // -------------------------------------------------------
  // HOME CHECK CALL
  // -------------------------------------------------------
  const requestHomeCheckForWall = async (label: string) => {
    try {
      setHomeCheckTriggered(true);

      const res = await axios.post(`${API_BASE_URL}/marking/homecheck`, {
        target: label,
      });

      const output = res.data.output || "";
      const lines = output
        .split(/\r?\n/)
        .map((x: string) => x.trim())
        .filter(Boolean);

      const raxLine = lines.find((l: string) => l.includes("rax_1"));
      const targetLine = lines.find((l: string) => l.includes("j0"));

      let current: any = {};
      let target: any = {};

      if (raxLine) {
        try {
          current = JSON.parse(raxLine.replace(/'/g, '"'));
        } catch {}
      }

      if (targetLine) {
        try {
          target = JSON.parse(targetLine.replace(/'/g, '"'));
        } catch {}
      }

      const rows = Object.entries(target).map(([key, val], idx) => ({
        axis: key.toUpperCase(),
        target: val,
        current: current[`rax_${idx + 1}`],
      }));

      setHomeCheckRows(rows);
    } catch (err) {
      console.error("HomeCheck error:", err);
    }
  };

  // -------------------------------------------------------
  // START PHASE 1
  // -------------------------------------------------------
  const startPhaseOne = async () => {
     /*const ok = await requestHomeCheck("wall_2");
    if (!ok) return;*/
    const walls = PHASE1_ORDER.map((label, index) => ({
      wall: label,
      rows: getDetails(label),
      excel: excelFiles[index], // index 0→wall_2, 1→wall_3, 2→wall_4
    }));

    await axios.post(`${API_BASE_URL}/marking/start`, {
      walls,
      meshfile,
      folder: folderdirectory,
      max_wall: maxWall,
      phase: 1,
    });

    setCurrentStep(1);
  };

  // -------------------------------------------------------
  // START PHASE 2
  // -------------------------------------------------------
  const startPhaseTwo = async () => {
     /*const ok = await requestHomeCheck(wall_5);
    if (!ok) return;*/
    const walls = PHASE2_ORDER.map((label, index) => ({
      wall: label,
      rows: getDetails(label),
      excel: excelFiles[index + 3], // 3→wall_5, 4→wall_6, 5→wall_1
    }));

    await axios.post(`${API_BASE_URL}/marking/start`, {
      walls,
      meshfile,
      folder: folderdirectory,
      max_wall: maxWall,
      phase: 2,
    });

    setCurrentStep(5);
  };

  // -------------------------------------------------------
  // RETRY WALL
  // -------------------------------------------------------
  const retryCurrentWall = async () => {
    const step = currentStepRef.current;
    const wall =
      step === 1
        ? 2
        : step === 2
        ? 3
        : step === 3
        ? 4
        : step === 5
        ? 5
        : step === 6
        ? 6
        : step === 7
        ? 1
        : null;

    if (!wall) return;

    // must pass homecheck first
    /*const ok = await requestHomeCheckForWall(`wall_${wall}`);
    if (!ok) return;*/

    await axios.post(`${API_BASE_URL}/marking/retry`, null, {
      params: { wall },
    });

    setHasError(false);
    setErrorMessage(null);
  };

  // -------------------------------------------------------
  // FETCH STATUS (Polling)
  // -------------------------------------------------------
  const schedulePoll = (t = 2000) => {
    if (pollingRef.current) clearTimeout(pollingRef.current);
    pollingRef.current = window.setTimeout(fetchStatus, t);
  };

  const fetchStatus = async () => {
    try {
      const res = await axios.get<MarkingStatusResponse>(
        `${API_BASE_URL}/marking/status`
      );
      const data = res.data;

      setPaused(data.paused);
      setHasError(data.hasError);
      if (data.errorSummary) setErrorMessage(data.errorSummary);
      if (data.hasError && data.startedWall) {
          setErrorWall(data.startedWall);
        } else if (!data.hasError) {
          setErrorWall(null);
        }

      // ---- Auto HomeCheck when error ----
      /*if (data.hasError && data.startedWall) {
        const wallLabel = `wall_${data.startedWall}`;
        if (!homeCheckTriggered) {
          console.log("🔍 Auto homecheck (error detected)");
          requestHomeCheckForWall(wallLabel);
        }
      }*/

      // ---- point counter (hidden) ----
      if (data.startedWall) {
        const wall = data.startedWall;
        const localRows = getRowCountForWall(wall);
        const total = data.totalPoints || localRows;
        console.log(`🔢 Wall ${wall}: ${data.lineCount} / ${total}`);

        // auto-advance
        if (!data.hasError && total > 0 && data.lineCount >= total) {
          const nextKey = NEXT_KEY_FOR_WALL[wall];
          const nextStep = STEP_SEQUENCE[nextKey];
          if (nextStep !== undefined) setCurrentStep(nextStep);
        }
      }

      schedulePoll(2000);
    } catch (err) {
      console.error("Polling error:", err);
      schedulePoll(4000);
    }
  };

  useEffect(() => {
    fetchStatus();
    return () => {
      if (pollingRef.current) clearTimeout(pollingRef.current);
    };
  }, []);

  // -------------------------------------------------------
  // UI HELPERS
  // -------------------------------------------------------
  const isMarkingStep = (s: number) => [1, 2, 3, 5, 6, 7].includes(s);
  const showHomeCheck =
    homeCheckRows.length > 0 &&
    ((currentStep === 0 || currentStep === 4) ||
      (isMarkingStep(currentStep) && hasError));

  // -------------------------------------------------------
  // RENDER UI
  // -------------------------------------------------------
  return (
    <>
      <h2 className="text-4xl font-bold text-center mb-6">
        Marking of PBU (6-Wall Flow)
      </h2>

      <ul className="steps w-full mb-6">
        {STEP_LABELS.map((s, i) => (
          <li
            key={s}
            className={i === currentStep ? "step step-primary" : "step"}
          >
            {s}
          </li>
        ))}
      </ul>

      <div className="flex gap-6">
        {/* IMAGE */}
        <img
          src={STEP_IMAGES[currentStep]}
          className="max-w-2xl max-h-[70vh] object-contain rounded-lg shadow"
        />

        {/* RIGHT PANEL */}
        <div className="flex flex-col w-[420px] gap-4">
          <div className="p-4 bg-base-200 rounded-lg shadow">
            <h3 className="font-bold text-xl mb-2">Instructions</h3>
            <p>{STEP_LABELS[currentStep]}</p>
            {errorMessage && (
              <p className="text-red-600 mt-2 whitespace-pre-line">
                {errorMessage}
              </p>
            )}
          </div>
          
          {/* HOME CHECK TABLE */}
          {/*{(currentStep === 0 || currentStep === 4) &&
            homeCheckRows.length > 0 || showHomeCheck && (
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <table className="w-full text-sm text-black">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-3 py-2">Axis</th>
                    <th className="px-3 py-2 text-right">Current</th>
                    <th className="px-3 py-2 text-right">Target</th>
                  </tr>
                </thead>
                <tbody>
                  {homeCheckRows.map((row) => (
                    <tr key={row.axis} className="border-t">
                      <td className="px-3 py-2">{row.axis}</td>
                      <td className="px-3 py-2 text-right">
                        {row.current?.toFixed(3)}
                      </td>
                      <td className="px-3 py-2 text-right">
                        {row.target?.toFixed(3)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}*/}

          {/* BUTTONS */}
          <div className="flex flex-col gap-3 mt-4">
            {currentStep === 0 && (
              <button
                className="btn btn-primary"
                onClick={startPhaseOne}
              >
                Next (Placement 1 → Wall 2)
              </button>
            )}

            {currentStep === 4 && (
              <button
                className="btn btn-primary"
                onClick={startPhaseTwo}
              >
                Next (Placement 2 → Wall 5)
              </button>
            )}

            {isMarkingStep(currentStep) && hasError && (
                <button className="btn btn-error" onClick={retryCurrentWall}>
                  {errorWall
                    ? `Retry Current Wall ${errorWall}`
                    : "Retry Current Wall"}
                </button>
              )}

            {currentStep === 8 && (
              <button
                className="btn btn-error"
                onClick={() => window.close()}
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

