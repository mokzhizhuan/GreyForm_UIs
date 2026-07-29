// =========================================================
// WallFlow.tsx
// Replaces FourWallFlow.tsx / SixWallFlow.tsx. The wall-marking flow
// (how many walls, which walls, how many placement breaks) is now
// driven entirely by STAGE, not by the room's physical wall count
// (maxWall). Each stage's exact operator-facing order is defined in
// STAGE_FLOWS below, per the specified sequence:
//   Stage 1: Placement 1 -> Wall 3 -> Placement 2 -> Wall 5
//   Stage 2: Placement 1 -> Wall 2,3,4 -> Placement 2 -> Wall 5,6,1
//   Stage 3: Placement 1 -> Wall 4 -> Placement 2 -> Wall 1,5
// =========================================================

import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

// Generic Auto Mode overlay photos — same regardless of stage/PBU.
import manToAuto1 from "../assets/Manual_to_auto_1.png";
import manToAuto2 from "../assets/Manual_to_auto_2.png";
import manToAuto3 from "../assets/Manual_to_auto_3.png";
import manToAuto4 from "../assets/Manual_to_auto_4.png";
import manToAuto5 from "../assets/Manual_to_auto_5().png";
import manToAuto6 from "../assets/Manual_to_auto_6.png";
import emergencyStop from "../assets/flex_pendant_emergency_stop.png";
// Fallback image for the terminal "Marking Complete" step — there's no
// per-PBU photo for that, unlike the placement/wall photos below.
import markingCompleteFallback from "../assets/six_wall_flow/6_wall_flow_placement2_1.png";

import { API_BASE_URL } from "./config";
import type { WallRow, MarkingStatusResponse } from "./flowShared";
import { buildExcelMap, parseHomeCheck, useActionLock, buildPbuImageUrl } from "./flowShared";

// --------------------------------------------------------
// STAGE FLOWS
// --------------------------------------------------------
// For 6-wall rooms, the flow shape (which walls, how split across the
// two placements) differs per stage:
const SIX_WALL_STAGE_FLOWS: Record<number, { phase1: string[]; phase2: string[] }> = {
  1: { phase1: ["wall_3"], phase2: ["wall_5"] },
  2: { phase1: ["wall_2", "wall_3", "wall_4"], phase2: ["wall_5", "wall_6", "wall_1"] },
  3: { phase1: ["wall_4"], phase2: ["wall_1", "wall_5"] },
};

// For 4-wall rooms, one placement reaches every wall — there is no
// second placement or phase 2, regardless of stage.
const FOUR_WALL_FLOW: { phase1: string[]; phase2: string[] } = {
  phase1: ["wall_2", "wall_3", "wall_4", "wall_1"],
  phase2: [],
};

// --------------------------------------------------------
// INSTRUCTION TEXT — everything shown in the "Instruction" panel.
// Edit the strings below for each stage; anything left out falls back
// to the generic default at the bottom.
// --------------------------------------------------------
interface StageInstructions {
  placement1?: string;
  placement2?: string;
  wall?: (wallNum: number) => string;
  complete?: string;
}

const STAGE_INSTRUCTIONS: Record<number, StageInstructions> = {
  1: {
    placement1: "Position the robot at Placement 1. The robot should be facing wall 2 and be 1m away from the wall.",
    placement2: "Move the robot to Placement 2. The robot should be facing wall 1 and be 1m away from the wall.",
    wall: (w) => `Marking pipe positions on Wall ${w} in progress.`,
    complete: "Stage 1 (pipe) marking complete.",
  },
  2: {
    placement1: "Position the robot at Placement 1. The robot should be facing wall 2 and be 1m away from the wall.",
    placement2: "Move the robot to Placement 2. The robot should be facing wall 1 and be 1m away from the wall.",
    wall: (w) => `Marking Wall ${w} in progress.`,
    complete: "Stage 2 (tile) marking complete.",
  },
  3: {
    placement1: "Position the robot at Placement 1. The robot should be facing wall 2 and be 1m away from the wall.",
    placement2: "Move the robot to Placement 2. The robot should be facing wall 1 and be 1m away from the wall.",
    wall: (w) => `Marking fixture positions on Wall ${w} in progress.`,
    complete: "Stage 3 (fixture) marking complete.",
  },
};

const DEFAULT_INSTRUCTIONS: Required<StageInstructions> = {
  placement1: "Position the robot at Placement 1.",
  placement2: "Move the robot to Placement 2.",
  wall: (w) => `Marking Wall ${w} in progress.`,
  complete: "Marking complete.",
};

function getStageInstructions(stage: number): Required<StageInstructions> {
  const custom = STAGE_INSTRUCTIONS[stage] ?? {};
  return { ...DEFAULT_INSTRUCTIONS, ...custom };
}

function getFlowForRoom(maxWall: number, stage: number) {
  if (maxWall === 4) {
    return FOUR_WALL_FLOW;
  }
  return SIX_WALL_STAGE_FLOWS[stage] ?? SIX_WALL_STAGE_FLOWS[2];
}

function wallNumFromLabel(label: string): number {
  const m = label.match(/\d+/);
  return m ? parseInt(m[0], 10) : 0;
}

// Builds the ordered step plan for a room/stage combination:
//   step 0                = Placement 1
//   steps 1..P1len        = phase1 walls, in order
//   [only if phase2 non-empty:]
//     step P1len+1          = Placement 2
//     steps P1len+2..+P2len = phase2 walls, in order
//   last step             = Marking Complete (terminal)
function buildStepPlan(maxWall: number, stage: number) {
  const { phase1, phase2 } = getFlowForRoom(maxWall, stage);
  const hasSecondPlacement = phase2.length > 0;

  const labels: string[] = ["Placement 1"];
  const wallForStep: (number | null)[] = [null];

  for (const w of phase1) {
    const n = wallNumFromLabel(w);
    labels.push(`Wall ${n}`);
    wallForStep.push(n);
  }

  let placement2Step: number | null = null;
  if (hasSecondPlacement) {
    placement2Step = labels.length;
    labels.push("Placement 2");
    wallForStep.push(null);

    for (const w of phase2) {
      const n = wallNumFromLabel(w);
      labels.push(`Wall ${n}`);
      wallForStep.push(n);
    }
  }

  const terminalStep = labels.length;
  labels.push("Marking Complete");
  wallForStep.push(null);

  const wallToStep: Record<number, number> = {};
  wallForStep.forEach((w, i) => {
    if (w !== null) wallToStep[w] = i;
  });

  const lastPhase1Step = hasSecondPlacement ? (placement2Step as number) - 1 : terminalStep - 1;
  const lastPhase2Step = hasSecondPlacement ? terminalStep - 1 : null;

  return {
    phase1,
    phase2,
    hasSecondPlacement,
    labels,
    wallForStep,
    wallToStep,
    placement1Step: 0,
    placement2Step,
    terminalStep,
    lastPhase1Step,
    lastPhase2Step,
  };
}

// Auto Mode Instructions steps (overlay pages) — generic, unrelated to stage.
const AUTO_STEPS = [
  {
    title: "Control panel",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>At the top right corner of the screen, select the "..." button.</li>
          <li>Next, select Control.</li>
          <li>You should now see the control panel.</li>
        </ul>
        <img src={manToAuto1} width="600" alt="Manual to Auto Mode Overview" />
      </>
    ),
  },
  {
    title: "Selection of Auto button",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Select the "Auto" button.</li>
          <li>A prompt should now be displayed. Select the "Acknowledge" button.</li>
        </ul>
        <img src={manToAuto2} width="600" alt="Press on Auto button" />
      </>
    ),
  },
  {
    title: "Motors on",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Select the "Motors on" button.</li>
          <li>The "Motors on" button should now be highlighted in blue.</li>
        </ul>
        <img src={manToAuto3} width="600" alt="Press on Motor on button" />
      </>
    ),
  },
  {
    title: "Reset program (PP to main)",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Select the "Reset program (PP to main)" button.</li>
          <li>Select "Yes" when the acknowledgement prompt appears.</li>
        </ul>
        <img src={manToAuto4} width="650" alt="Press on Reset Program button" />
      </>
    ),
  },
  {
    title: "Press the Play Button",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Select the play button (right below "Reset PP to main")"</li>
          <li>You have to press the "Play" button</li>
        </ul>
        <img src={manToAuto5} width="250" alt="Press the Play button" />
      </>
    ),
  },
  {
    title: "Complete Auto mode Setup",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>You should now be seeing the screen below.</li>
        </ul>
        <img src={manToAuto6} width="600" alt="Manual to Auto Mode Overview" />
      </>
    ),
  },
  {
    title: "Safety Instructions",
    body: (
      <>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Always keep the workspace clear while the robot operates.</li>
          <li>The operator should always be ready to hit the emergency stop switch in case of emergencies.</li>
        </ul>
        <img src={emergencyStop} width="600" alt="Emergency Stop Button" />
      </>
    ),
  },
];

// --------------------------------------------------------
// COMPONENT
// --------------------------------------------------------
const WallFlow: React.FC<any> = ({
  wallDetails,
  maxWall,
  excelFiles,
  meshfile,
  folderdirectory,
  stage,
  outputName,
}) => {
  const stagePlan = useMemo(() => buildStepPlan(maxWall, stage), [maxWall, stage]);
  const stageInstructions = useMemo(() => getStageInstructions(stage), [stage]);
  const {
    phase1,
    phase2,
    hasSecondPlacement,
    labels: STEP_LABELS,
    wallForStep,
    wallToStep,
    placement1Step,
    placement2Step,
    terminalStep,
    lastPhase1Step,
    lastPhase2Step,
  } = stagePlan;

  const [currentStep, setCurrentStep] = useState(0);
  // Canonical status snapshot (single source of truth in UI)
  const [status, setStatus] = useState<MarkingStatusResponse | null>(null);
  const running = !!status?.running;
  const hasError = !!status?.hasError;
  const homeCheckPending = !!status?.homeCheckPending;
  const homeCheckWall = status?.homeCheckWall ?? null;
  const homeCheckOutput = status?.homeCheckOutput ?? "";
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [cmdLogs, setCmdLogs] = useState<string[]>([]);
  const logEndRef = useRef<HTMLDivElement | null>(null);
  const { actionBusy, withActionLock } = useActionLock();
  const pollingTimerRef = useRef<number | null>(null);
  const pollInFlightRef = useRef(false);
  const aliveRef = useRef(true);
  const [showAutoInstr, setShowAutoInstr] = useState(false);
  const [autoStep, setAutoStep] = useState(0);
  const totalAutoSteps = AUTO_STEPS.length;
  const [forcedPlacement2, setForcedPlacement2] = useState(false);

  // Reset to step 0 whenever the active stage or room's wall count
  // changes (different flow shape)
  useEffect(() => {
    setCurrentStep(0);
    setForcedPlacement2(false);
  }, [stage, maxWall]);

  // Prevent background scroll when overlay open
  useEffect(() => {
    if (showAutoInstr) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = prev;
      };
    }
  }, [showAutoInstr]);

  // Keyboard navigation when overlay is open
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (!showAutoInstr) return;
      if (e.key === "Escape") {
        setShowAutoInstr(false);
      } else if (e.key === "ArrowRight") {
        setAutoStep((s) => Math.min(s + 1, totalAutoSteps - 1));
      } else if (e.key === "ArrowLeft") {
        setAutoStep((s) => Math.max(s - 1, 0));
      } else if (e.key.toLowerCase() === "home") {
        setAutoStep(0);
      } else if (e.key.toLowerCase() === "end") {
        setAutoStep(totalAutoSteps - 1);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [showAutoInstr, totalAutoSteps]);

  // --------------------------------------------------------
  // NORMALIZATION
  // --------------------------------------------------------
  const normalized = useMemo(() => {
    const out: Record<string, WallRow[]> = {};
    for (const [k, v] of Object.entries(wallDetails || {})) {
      const m = k.match(/\d+/);
      out[`wall_${m ? m[0] : k}`] = v as any;
    }
    return out;
  }, [wallDetails]);
  const excelMap = useMemo(() => buildExcelMap(excelFiles || []), [excelFiles]);
  const getRows = (w: string) => normalized[w] ?? [];

  // --------------------------------------------------------
  // CURRENT STEP IMAGE (fetched from the Linux PC, per stage/wall)
  // --------------------------------------------------------
  const stepImageSrc = useMemo(() => {
    if (currentStep === placement1Step) {
      return buildPbuImageUrl(folderdirectory, `${outputName}_pos1.png`);
    }
    if (currentStep === placement2Step) {
      return buildPbuImageUrl(folderdirectory, `${outputName}_pos2.png`);
    }
    const w = wallForStep[currentStep];
    if (w) {
      return buildPbuImageUrl(folderdirectory, `stage${stage}_wall${w}.png`);
    }
    return markingCompleteFallback; // terminal step
  }, [currentStep, stage, folderdirectory, outputName, placement1Step, placement2Step, wallForStep]);

  // --------------------------------------------------------
  // HOME CHECK TABLE (backend-driven; never stored in state)
  // --------------------------------------------------------
  const homeCheckRows = useMemo(() => {
    if (!homeCheckPending || homeCheckWall === null) return [];
    if (!homeCheckOutput) return [];
    return parseHomeCheck(homeCheckOutput);
  }, [homeCheckPending, homeCheckWall, homeCheckOutput]);
  const homeCheckPassed = useMemo(() => {
    if (!homeCheckPending || homeCheckWall === null) return null;
    if (!homeCheckOutput) return null;
    return homeCheckOutput.split(/\r?\n/).some((l) => l.trim() === "True");
  }, [homeCheckPending, homeCheckWall, homeCheckOutput]);

  const extractFinalSummary = (logs: string[]) => {
    if (!logs || logs.length === 0) return null;
    for (let i = logs.length - 1; i >= 0; i--) {
      if (logs[i].startsWith("[ERROR]")) return logs[i];
    }
    for (let i = logs.length - 1; i >= 0; i--) {
      if (logs[i].startsWith("[SUCCESS]")) return logs[i];
    }
    return null;
  };

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [cmdLogs]);

  // --------------------------------------------------------
  // API: start phases
  // --------------------------------------------------------
  const startPhaseOne = async () =>
    withActionLock(async () => {
      setErrorMessage(null);
      setCmdLogs([]);
      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls: phase1.map((w) => ({
          wall: w,
          rows: getRows(w),
          excel: excelMap[w] ?? "",
        })),
        meshfile,
        folder: folderdirectory,
        max_wall: maxWall,
        stage,
        phase: 1,
      });
      await axios.post(`${API_BASE_URL}/marking/homecheck`, { target: phase1[0] });
    });

  const startPhaseTwo = async () =>
    withActionLock(async () => {
      setForcedPlacement2(false);
      setErrorMessage(null);
      setCmdLogs([]);
      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls: phase2.map((w) => ({
          wall: w,
          rows: getRows(w),
          excel: excelMap[w] ?? "",
        })),
        meshfile,
        folder: folderdirectory,
        max_wall: maxWall,
        stage,
        phase: 2,
      });
      await axios.post(`${API_BASE_URL}/marking/homecheck`, { target: phase2[0] });
    });

  // --------------------------------------------------------
  // ACTIONS
  // --------------------------------------------------------
  const pauseMarking = async () =>
    withActionLock(async () => {
      await axios.post(`${API_BASE_URL}/marking/pause`);
    });

  const retryCurrentWall = async () =>
    withActionLock(async () => {
      setErrorMessage(null);
      setCmdLogs([]);
      try {
        await axios.post(`${API_BASE_URL}/marking/retry`);
      } catch (e: any) {
        setErrorMessage(e?.response?.data?.detail || "Retry failed (backend error)");
      }
    });

  const continueNextWall = async () =>
    withActionLock(async () => {
      const idleOnLastPhase1Wall =
        status?.phase === 1 &&
        currentStep === lastPhase1Step &&
        !status?.running &&
        !status?.homeCheckPending;

      if (idleOnLastPhase1Wall) {
        if (hasSecondPlacement) {
          // Phase 1's last wall -> Placement 2
          setForcedPlacement2(true);
          setCurrentStep(placement2Step as number);
        } else {
          // Single-phase room (e.g. 4 walls) — last wall IS the last
          // step, go straight to Marking Complete.
          setCurrentStep(terminalStep);
        }
        return;
      }
      // Phase 2's last wall -> Marking Complete (terminal); only
      // applicable to rooms that have a second placement/phase at all.
      if (
        hasSecondPlacement &&
        status?.phase === 2 &&
        currentStep === lastPhase2Step &&
        !status?.running &&
        !status?.homeCheckPending
      ) {
        setCurrentStep(terminalStep);
        return;
      }
      // Otherwise normal backend continue
      setErrorMessage(null);
      setCmdLogs([]);
      const res = await axios.post(`${API_BASE_URL}/marking/continue`);
      if (res.data?.homeCheckRequired && res.data?.next_wall) {
        await axios.post(`${API_BASE_URL}/marking/homecheck`, {
          target: `wall_${res.data.next_wall}`,
        });
      }
    });

  const isPlacement2 = hasSecondPlacement && currentStep === placement2Step;
  const isPhase1LastWall = status?.phase === 1 && currentStep === lastPhase1Step;
  const isHomeCheckFailed = homeCheckPending && homeCheckPassed === false;
  const isRealMarkingError =
    hasError && !running && !homeCheckPending && !isPhase1LastWall && !isPlacement2;
  const isPhase1LastWallIdle =
    !running && !homeCheckPending && status?.phase === 1 && currentStep === lastPhase1Step;
  const showErrorBanner = !!errorMessage && wallForStep[currentStep] !== null;
  const isTerminalStep = currentStep === terminalStep;

  // --------------------------------------------------------
  // POLLING (single loop, no overlap, stable)
  // --------------------------------------------------------
  const poll = async () => {
    if (!aliveRef.current) return;
    if (pollInFlightRef.current) {
      pollingTimerRef.current = window.setTimeout(poll, 1200);
      return;
    }
    pollInFlightRef.current = true;
    try {
      const { data } = await axios.get<MarkingStatusResponse>(
        `${API_BASE_URL}/marking/status`
      );
      if (!aliveRef.current) return;
      setStatus(data);

      if (data.hasError) {
        setErrorMessage(data.errorSummary || "Marking error detected");
      } else {
        setErrorMessage(null);
      }

      if (currentStep === terminalStep) {
        pollInFlightRef.current = false;
        pollingTimerRef.current = window.setTimeout(poll, 1500);
        return;
      }

      let nextStep = currentStep;

      // Which phase/wall marks "everything is actually done" depends on
      // whether this room has a second placement at all.
      const finalPhase = hasSecondPlacement ? 2 : 1;
      const finalWall = hasSecondPlacement
        ? wallForStep[lastPhase2Step as number]
        : wallForStep[lastPhase1Step];
      const isMarkingComplete =
        data.phase === finalPhase &&
        !data.running &&
        !data.homeCheckPending &&
        data.doneWall === finalWall;

      const lastPhase1Wall = wallForStep[lastPhase1Step];

      if (isMarkingComplete) {
        nextStep = terminalStep;
      } else if (
        hasSecondPlacement &&
        data.phase === 1 &&
        data.doneWall === lastPhase1Wall &&
        !data.running &&
        !data.homeCheckPending &&
        !forcedPlacement2
      ) {
        setForcedPlacement2(true);
        nextStep = placement2Step as number;
      } else if (hasSecondPlacement && forcedPlacement2) {
        nextStep = placement2Step as number;
      } else if (data.homeCheckPending && data.homeCheckWall !== null) {
        nextStep = wallToStep[data.homeCheckWall] ?? nextStep;
      } else if (data.running && data.startedWall !== null) {
        nextStep = wallToStep[data.startedWall] ?? nextStep;
      } else if (!data.running && data.doneWall !== null) {
        nextStep = wallToStep[data.doneWall] ?? nextStep;
      }

      if (nextStep !== currentStep) {
        setCurrentStep(nextStep);
      }

      const logWall =
        data.homeCheckPending && data.homeCheckWall !== null
          ? data.homeCheckWall
          : data.startedWall ??
            (data.hasError ? data.startedWall ?? data.doneWall : null);

      if (logWall !== null) {
        try {
          const logRes = await axios.get(
            `${API_BASE_URL}/marking/errorlog/${logWall}`
          );
          if (logRes.data?.error) {
            const logs = logRes.data.error as string[];
            const finalLine = extractFinalSummary(logs);
            setCmdLogs(finalLine ? [finalLine] : []);
          }
        } catch {
          // ignore log fetch errors
        }
      }
    } catch {
      // ignore polling errors; keep polling
    } finally {
      pollInFlightRef.current = false;
      pollingTimerRef.current = window.setTimeout(poll, 1500);
    }
  };

  useEffect(() => {
    aliveRef.current = true;
    poll();
    return () => {
      aliveRef.current = false;
      if (pollingTimerRef.current) clearTimeout(pollingTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --------------------------------------------------------
  // RENDER
  // --------------------------------------------------------
  return (
    <>
      <h2 className="text-4xl font-bold text-center mb-6">
        Marking of PBU — Stage {stage}
      </h2>

      <ul className="steps w-full mb-6">
        {STEP_LABELS.map((l, i) => (
          <li
            key={`${l}-${i}`}
            className={i === currentStep ? "step step-primary" : "step"}
          >
            {l}
          </li>
        ))}
      </ul>

      <div className="flex gap-6">
        <img
          src={stepImageSrc}
          className="max-w-2xl max-h-[70vh] rounded-lg shadow object-contain"
          alt="step"
        />
        <div className="flex flex-col w-[520px] gap-4">
          <div className="menu bg-base-200 rounded-box p-4 shadow">
            <p className="text-lg font-semibold">Instruction</p>
            <p className="mt-1 text-sm">
              {homeCheckPending && homeCheckWall !== null && (
                <>Home position check required for Wall {homeCheckWall}.</>
              )}
              {!homeCheckPending && currentStep === placement1Step && stageInstructions.placement1}
              {!homeCheckPending && isPlacement2 && stageInstructions.placement2}
              {!homeCheckPending && !isTerminalStep && wallForStep[currentStep] !== null &&
                stageInstructions.wall(wallForStep[currentStep] as number)}
              {isTerminalStep && stageInstructions.complete}
            </p>
          </div>

          {showErrorBanner && (
            <div className="p-3 bg-red-100 text-red-700 rounded">
              <pre className="whitespace-pre-wrap text-sm">
                {errorMessage}
              </pre>
            </div>
          )}

          {homeCheckPending && homeCheckWall !== null && homeCheckRows.length > 0 && (
            <div className="bg-white shadow rounded overflow-hidden">
              <div
                className={`text-center font-bold py-1 ${
                  homeCheckPassed === false
                    ? "bg-red-100 text-red-800"
                    : "bg-green-100 text-green-800"
                }`}
              >
                {homeCheckPassed === false ? "✖ Home check failed" : "✔ Home position verified"}
              </div>
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="p-2 text-left">Axis</th>
                    <th className="p-2 text-left">Current</th>
                    <th className="p-2 text-left">Target</th>
                  </tr>
                </thead>
                <tbody>
                  {homeCheckRows.map((r, i) => (
                    <tr key={i} className="border-t">
                      <td className="p-2">{r.axis}</td>
                      <td className="p-2">{r.current?.toFixed?.(3)}</td>
                      <td className="p-2">{r.target?.toFixed?.(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="flex flex-col gap-3">
            {currentStep === placement1Step && (
              <button className="btn btn-primary" onClick={startPhaseOne} disabled={actionBusy}>
                {actionBusy ? "Working..." : "Next"}
              </button>
            )}
            {currentStep === placement2Step && !isHomeCheckFailed && (
              <button className="btn btn-primary" onClick={startPhaseTwo} disabled={actionBusy}>
                {actionBusy ? "Working..." : "Next"}
              </button>
            )}
            {running && wallForStep[currentStep] !== null && !hasError && (
              <button className="btn btn-warning" onClick={pauseMarking} disabled={actionBusy}>
                {actionBusy ? "Working..." : "Pause"}
              </button>
            )}
            {isHomeCheckFailed && (
              <button className="btn btn-error" onClick={retryCurrentWall} disabled={actionBusy}>
                Retry
              </button>
            )}
            {/* Phase 1's last wall finished (success or error) -> Retry or Continue to Placement 2 */}
            {isPhase1LastWallIdle && (
              <div className="flex gap-2">
                <button className="btn btn-error flex-1" onClick={retryCurrentWall} disabled={actionBusy}>
                  Retry
                </button>
                <button className="btn btn-warning flex-1" onClick={continueNextWall} disabled={actionBusy}>
                  Continue →
                </button>
              </div>
            )}
            {/* Any other marking error */}
            {isRealMarkingError && !isTerminalStep && (
              <div className="flex gap-2">
                <button className="btn btn-error flex-1" onClick={retryCurrentWall} disabled={actionBusy}>
                  Retry
                </button>
                <button className="btn btn-warning flex-1" onClick={continueNextWall} disabled={actionBusy}>
                  Continue →
                </button>
              </div>
            )}
            {isTerminalStep && (
              <button className="btn btn-success" onClick={() => window.location.reload()}>
                Exit
              </button>
            )}
          </div>

          <div>
            <button
              className="btn btn-neutral btn-sm"
              onClick={() => {
                setAutoStep(0);
                setShowAutoInstr(true);
              }}
              aria-haspopup="dialog"
              aria-expanded={showAutoInstr}
              aria-controls="auto-mode-instructions"
            >
              Click here to view auto mode instructions
            </button>
          </div>
        </div>
      </div>

      {/* Overlay / Modal for Auto Mode Instructions (multi-step) */}
      {showAutoInstr && (
        <div
          id="auto-mode-instructions"
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50"
        >
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setShowAutoInstr(false)}
          />
          <div className="absolute inset-0 flex items-center justify-center p-4">
            <div className="w-full max-w-3xl rounded-xl bg-base-100 shadow-2xl">
              <div className="flex items-center justify-between border-b px-5 py-3">
                <div>
                  <h3 className="text-lg font-semibold">
                    Auto Mode Instructions — {AUTO_STEPS[autoStep].title}
                  </h3>
                  <div className="text-xs text-base-content/70">
                    Step {autoStep + 1} of {totalAutoSteps}
                  </div>
                </div>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setShowAutoInstr(false)}
                  aria-label="Close"
                  title="Close"
                >
                  ✕
                </button>
              </div>
              <div className="p-5 space-y-4 text-sm leading-6">
                {AUTO_STEPS[autoStep].body}
                <div className="alert alert-info mt-2">
                  <div>
                    Ensure the laser leveller is turned on and facing the active wall. Keep
                    the area clear while the robot is moving.
                  </div>
                </div>
              </div>
              <div className="flex justify-between border-t px-5 py-3">
                <div className="flex gap-2">
                  <button className="btn btn-ghost" onClick={() => setShowAutoInstr(false)}>
                    Close
                  </button>
                </div>
                <div className="flex gap-2">
                  <button
                    className="btn"
                    onClick={() => setAutoStep((s) => Math.max(s - 1, 0))}
                    disabled={autoStep === 0}
                  >
                    ← Back
                  </button>
                  {autoStep < totalAutoSteps - 1 ? (
                    <button
                      className="btn btn-primary"
                      onClick={() => setAutoStep((s) => Math.min(s + 1, totalAutoSteps - 1))}
                    >
                      Next →
                    </button>
                  ) : (
                    <button className="btn btn-primary" onClick={() => setShowAutoInstr(false)}>
                      Finish
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default WallFlow;
