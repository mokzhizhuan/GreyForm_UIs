// =========================================================
// SixWallFlow.tsx (UI-STABLE / FRONTEND-ONLY FIX)
// - HomeCheck table is backend-driven (status.homeCheckOutput)
// - Retry/Continue are stable (action lock + no UI clearing fights poll)
// - Poll never overlaps; no stale updates; no hidden table issues
// =========================================================

import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

import placementOne from "../assets/six_wall_flow/6_wall_flow_placement1.jpg";
import placementTwo from "../assets/six_wall_flow/6_wall_flow_placement2.jpg";
import wallMarking1 from "../assets/six_wall_flow/6_wall_flow_placement1_1.png";
import wallMarking2 from "../assets/six_wall_flow/6_wall_flow_placement2_1.png";
import manToAuto1 from "../assets/Manual_to_auto_1.png";
import manToAuto2 from "../assets/Manual_to_auto_2.png";
import manToAuto3 from "../assets/Manual_to_auto_3.png";
import manToAuto4 from "../assets/Manual_to_auto_4.png";
import manToAuto5 from "../assets/Manual_to_auto_5().png";
import manToAuto6 from "../assets/Manual_to_auto_6.png";
import emergencyStop from "../assets/flex_pendant_emergency_stop.png";

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
  phase: number | null;
  hasError: boolean;
  errorSummary?: string | null;
  lastFailedWall?: number | null;
  homeCheckPending?: boolean;
  homeCheckWall?: number | null;
  homeCheckOutput?: string | null;
}

// --------------------------------------------------------
// CONSTANTS
// --------------------------------------------------------
const PHASE1_ORDER = ["wall_2", "wall_3", "wall_4"];
const PHASE2_ORDER = ["wall_5", "wall_6", "wall_1"];
const TOTAL_STAGES = 3;

type FlowStep = {
  type: "placement" | "wall" | "complete";
  label: string;
  phase: 0 | 1 | 2;
  wall: string | null;
};

// Auto Mode Instructions steps (overlay pages)
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
// HELPERS
// --------------------------------------------------------
const getWallNo = (wallKey: string) => wallKey.replace("wall_", "");

const findExcelForWall = (files: string[], stage: number, wallKey: string) => {
  const wallNo = getWallNo(wallKey);

  return (
    files.find((file) => {
      const filename = file.split(/[\\/]/).pop()?.toLowerCase() ?? "";

      return (
        filename.includes(`stage${stage}`) &&
        (filename.includes(`wall_${wallNo}`) || filename.includes(`wall${wallNo}`)) &&
        filename.endsWith(".xlsx")
      );
    }) ?? ""
  );
};
const parseHomeCheck = (output: string) => {
  const lines = (output || "").split(/\r?\n/).map((l) => l.trim());
  const rax = lines.find((l) => l.includes("rax_1"));
  const tgt = lines.find((l) => l.includes("j0"));
  let current: any = {};
  let target: any = {};
  try {
    if (rax) current = JSON.parse(rax.replace(/'/g, '"'));
    if (tgt) target = JSON.parse(tgt.replace(/'/g, '"'));
  } catch {
    // ignore parse errors
  }
  return Object.entries(target).map(([k, v], i) => {
    const m = k.match(/^j(\d+)$/i);
    const idx = m ? parseInt(m[1], 10) : i;
    return {
      axis: `J${idx + 1}`,
      target: v,
      current: current[`rax_${idx + 1}`],
    };
  });
};
// --------------------------------------------------------
// COMPONENT
// --------------------------------------------------------
const SixWallFlow: React.FC<any> = ({
  wallDetails,
  maxWall,
  excelFiles,
  meshfile,
  folderdirectory,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [currentStage, setCurrentStage] = useState(1);
  // Canonical status snapshot (single source of truth in UI)
  const [status, setStatus] = useState<MarkingStatusResponse | null>(null);
  // Derived flags
  const running = !!status?.running;
  const paused = !!status?.paused;
  const hasError = !!status?.hasError;
  const homeCheckPending = !!status?.homeCheckPending;
  const homeCheckWall = status?.homeCheckWall ?? null;
  const homeCheckOutput = status?.homeCheckOutput ?? "";
  // Error targeting
  const [lastErrorWall, setLastErrorWall] = useState<number | null>(null);
  // UI messaging/logs
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [cmdLogs, setCmdLogs] = useState<string[]>([]);
  const logEndRef = useRef<HTMLDivElement | null>(null);
  // Action locking (prevents double-click / poll fights)
  const actionLockRef = useRef(false);
  const [actionBusy, setActionBusy] = useState(false);
  // Poll control (no overlap)
  const pollingTimerRef = useRef<number | null>(null);
  const pollInFlightRef = useRef(false);
  const aliveRef = useRef(true);
  const currentStepRef = useRef(currentStep);
  const currentStageRef = useRef(currentStage);
  const flowStepsRef = useRef<FlowStep[]>([]);
  const forcedPlacement2Ref = useRef(false);
    // Overlay state for auto mode instructions (multi-step)
  const [showAutoInstr, setShowAutoInstr] = useState(false);
  const [autoStep, setAutoStep] = useState(0);
  const totalAutoSteps = AUTO_STEPS.length;
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
  const getRows = (w: string) => normalized[w] ?? [];

  const getExcelForWall = (stage: number, wallKey: string) =>
    findExcelForWall(excelFiles || [], stage, wallKey);

  const phase1OrderForStage = useMemo(
    () => PHASE1_ORDER.filter((w) => getExcelForWall(currentStage, w)),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [currentStage, excelFiles]
  );

  const phase2OrderForStage = useMemo(
    () => PHASE2_ORDER.filter((w) => getExcelForWall(currentStage, w)),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [currentStage, excelFiles]
  );

  const flowSteps = useMemo<FlowStep[]>(() => {
    const steps: FlowStep[] = [
      {
        type: "placement",
        label: `Stage ${currentStage} - Placement 1`,
        phase: 1,
        wall: null,
      },
      ...phase1OrderForStage.map((w) => ({
        type: "wall" as const,
        label: `Stage ${currentStage} - Wall ${getWallNo(w)}`,
        phase: 1 as const,
        wall: w,
      })),
      {
        type: "placement",
        label: `Stage ${currentStage} - Placement 2`,
        phase: 2,
        wall: null,
      },
      ...phase2OrderForStage.map((w) => ({
        type: "wall" as const,
        label: `Stage ${currentStage} - Wall ${getWallNo(w)}`,
        phase: 2 as const,
        wall: w,
      })),
      { type: "complete", label: "Marking Complete", phase: 0, wall: null },
    ];

    return steps;
  }, [currentStage, phase1OrderForStage, phase2OrderForStage]);

  const currentFlowStep = flowSteps[currentStep] ?? flowSteps[0];
  const completeStepIndex = Math.max(flowSteps.length - 1, 0);
  const placement2StepIndex = flowSteps.findIndex(
    (s) => s.type === "placement" && s.phase === 2
  );
  const phase1LastWall = phase1OrderForStage[phase1OrderForStage.length - 1] ?? null;
  const phase2LastWall = phase2OrderForStage[phase2OrderForStage.length - 1] ?? null;
  const phase1LastStepIndex = phase1LastWall
    ? flowSteps.findIndex((s) => s.wall === phase1LastWall)
    : -1;

  const getStepImage = (step: FlowStep | undefined) => {
    if (!step) return placementOne;
    if (step.type === "complete") return wallMarking2;
    if (step.type === "placement") return step.phase === 2 ? placementTwo : placementOne;
    return step.phase === 2 ? wallMarking2 : wallMarking1;
  };

  const activeExcelFile =
    currentFlowStep?.type === "wall" && currentFlowStep.wall
      ? getExcelForWall(currentStage, currentFlowStep.wall)
      : "";
  const activeExcelName = activeExcelFile
    ? activeExcelFile.split(/[\\/]/).pop()
    : "";
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
    // your homeposcheck prints "True" in output
    return homeCheckOutput.split(/\r?\n/).some((l) => l.trim() === "True");
  }, [homeCheckPending, homeCheckWall, homeCheckOutput]);
  const extractFinalSummary = (logs: string[]) => {
  if (!logs || logs.length === 0) return null;
  // Prefer final ERROR
  for (let i = logs.length - 1; i >= 0; i--) {
    if (logs[i].startsWith("[ERROR]")) {
      return logs[i];
    }
  }
  // Otherwise final SUCCESS
  for (let i = logs.length - 1; i >= 0; i--) {
    if (logs[i].startsWith("[SUCCESS]")) {
      return logs[i];
    }
  }
  return null;
};
  // --------------------------------------------------------
  // AUTO SCROLL LOGS
  // --------------------------------------------------------
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [cmdLogs]);
const [forcedPlacement2, setForcedPlacement2] = useState(false);

  useEffect(() => {
    currentStepRef.current = currentStep;
  }, [currentStep]);

  useEffect(() => {
    currentStageRef.current = currentStage;
  }, [currentStage]);

  useEffect(() => {
    flowStepsRef.current = flowSteps;
  }, [flowSteps]);

  useEffect(() => {
    forcedPlacement2Ref.current = forcedPlacement2;
  }, [forcedPlacement2]);
  // --------------------------------------------------------
  // Small helper: safely lock actions
  // --------------------------------------------------------
  const withActionLock = async (fn: () => Promise<void>) => {
    if (actionLockRef.current) return;
    actionLockRef.current = true;
    setActionBusy(true);
    try {
      await fn();
    } finally {
      actionLockRef.current = false;
      setActionBusy(false);
    }
  };
  // --------------------------------------------------------
  // API: start phases
  // --------------------------------------------------------
  const startPhaseOne = async () =>
    withActionLock(async () => {
      setErrorMessage(null);
      setCmdLogs([]);
      setForcedPlacement2(false);
      forcedPlacement2Ref.current = false;
      await axios.post(`${API_BASE_URL}/marking/start`, {
        walls: phase1OrderForStage.map((w) => ({
          wall: w,
          rows: getRows(w),
          excel: getExcelForWall(currentStage, w),
        })),
        meshfile,
        folder: folderdirectory,
        max_wall: maxWall,
        phase: 1,
        stage: currentStage,
      });
      // Kick the first available wall homecheck via backend homecheck endpoint:
      if (phase1OrderForStage[0]) {
        await axios.post(`${API_BASE_URL}/marking/homecheck`, {
          target: phase1OrderForStage[0],
        });
      }
      // No local state changes; poll will reflect backend state.
    });
  const startPhaseTwo = async () =>
  withActionLock(async () => {
    setForcedPlacement2(false); // 🔓 unlock Placement 2
    forcedPlacement2Ref.current = false;
    setErrorMessage(null);
    setCmdLogs([]);
    await axios.post(`${API_BASE_URL}/marking/start`, {
      walls: phase2OrderForStage.map((w) => ({
        wall: w,
        rows: getRows(w),
        excel: getExcelForWall(currentStage, w),
      })),
      meshfile,
      folder: folderdirectory,
      max_wall: maxWall,
      phase: 2,
      stage: currentStage,
    });
    if (phase2OrderForStage[0]) {
      await axios.post(`${API_BASE_URL}/marking/homecheck`, {
        target: phase2OrderForStage[0],
      });
    }
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
        return;
      }
      // IMPORTANT: Do not run homecheck directly here unless you really want it.
      // If your backend requires it, you can keep it.
      // Most stable approach: backend sets homeCheckPending + homeCheckWall.
      // Poll will show it and operator can proceed.
      // If you want auto-trigger, uncomment:
      // const w = status?.homeCheckWall ?? status?.lastFailedWall ?? lastErrorWall;
      // if (w) await axios.post(`${API_BASE_URL}/marking/homecheck`, { target: `wall_${w}` });
    });
  const continueNextWall = async () =>
  withActionLock(async () => {
    // ------------------------------------------------------
    // PHASE 1 → PLACEMENT 2 (UI-controlled transition)
    // Allow if:
    // - phase 1
    // - UI currently on the last available Phase 1 wall
    // - idle (not running, not homecheck pending)
    // This avoids relying on one fixed wall number.
    // ------------------------------------------------------
    const phase1IdleOnLastAvailableWall =
      status?.phase === 1 &&
      currentStep === phase1LastStepIndex &&
      !status?.running &&
      !status?.homeCheckPending;
    if (phase1IdleOnLastAvailableWall) {
      setForcedPlacement2(true);
      forcedPlacement2Ref.current = true;
      if (placement2StepIndex >= 0) {
        setCurrentStep(placement2StepIndex);
        currentStepRef.current = placement2StepIndex;
      }
      return;
    }
    // ------------------------------------------------------
    // MARKING COMPLETE (terminal)
    // ------------------------------------------------------
    if (
      status?.phase === 2 &&
      currentFlowStep?.wall === phase2LastWall &&
      !status?.running &&
      !status?.homeCheckPending
    ) {
      if (currentStage < TOTAL_STAGES) {
        const nextStage = currentStage + 1;
        setCurrentStage(nextStage);
        currentStageRef.current = nextStage;
        setForcedPlacement2(false);
        forcedPlacement2Ref.current = false;
        setCurrentStep(0);
        currentStepRef.current = 0;
      } else {
        setCurrentStep(completeStepIndex);
        currentStepRef.current = completeStepIndex;
      }
      return;
    }
    // ------------------------------------------------------
    // Otherwise normal backend continue
    // ------------------------------------------------------
    setErrorMessage(null);
    setCmdLogs([]);
    const res = await axios.post(`${API_BASE_URL}/marking/continue`);
    if (res.data?.homeCheckRequired && res.data?.next_wall) {
      await axios.post(`${API_BASE_URL}/marking/homecheck`, {
        target: `wall_${res.data.next_wall}`,
      });
    }
  });
  // Show actions:
  // - Marking error => show buttons
  // - HomeCheck failed => also show buttons (operator expects Retry/Continue
const isPlacement2 = currentStep === placement2StepIndex;
const isPhase1LastWall = status?.phase === 1 && currentStep === phase1LastStepIndex;
const isHomeCheckFailed = homeCheckPending && homeCheckPassed === false;
const isCurrentMarkingStep = currentFlowStep?.type === "wall";
const isRealMarkingError =
  hasError &&
  !running &&
  !homeCheckPending &&
  !isPhase1LastWall &&
  !isPlacement2;
const isPhase1LastWallMarkingError =
  !running &&
  !homeCheckPending &&
  status?.phase === 1 &&
  currentStep === phase1LastStepIndex;
const showErrorBanner = errorMessage && isCurrentMarkingStep; 
const isTerminalStep = currentFlowStep?.type === "complete";
  // --------------------------------------------------------
  // POLLING (single loop, no overlap, stable)
  // --------------------------------------------------------
  const poll = async () => {
  if (!aliveRef.current) return;
  // Prevent overlapping polls
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
    // -------------------------------
    // 🔴 Derive last failed wall safely
    // -------------------------------
    if (data.lastFailedWall !== undefined && data.lastFailedWall !== null) {
      setLastErrorWall(data.lastFailedWall);
    } else if (data.hasError) {
      const failed = data.startedWall ?? data.doneWall ?? null;
      if (failed !== null) setLastErrorWall(failed);
    }
    // -------------------------------
    // 🔴 Error message handling
    // -------------------------------
    if (data.hasError) {
      setErrorMessage(data.errorSummary || "Marking error detected");
    } else if (data.homeCheckPending && data.homeCheckWall !== null) {
      // Homecheck table itself is the message
      setErrorMessage(null);
    } else {
      setErrorMessage(null);
    }
    // =========================================================
    // 🧠 STEP RESOLUTION (PRIORITY-ORDERED, SAFE)
    // =========================================================
    const stepNow = currentStepRef.current;
    const stepsNow = flowStepsRef.current;
    const stageNow = currentStageRef.current;
    const completeIdxNow = Math.max(stepsNow.length - 1, 0);
    const placement2IdxNow = stepsNow.findIndex(
      (s) => s.type === "placement" && s.phase === 2
    );
    const phase1OrderNow = PHASE1_ORDER.filter((w) =>
      findExcelForWall(excelFiles || [], stageNow, w)
    );
    const phase2OrderNow = PHASE2_ORDER.filter((w) =>
      findExcelForWall(excelFiles || [], stageNow, w)
    );
    const phase1LastWallNow =
      phase1OrderNow.length > 0 ? phase1OrderNow[phase1OrderNow.length - 1] : undefined;
    const phase2LastWallNow =
      phase2OrderNow.length > 0 ? phase2OrderNow[phase2OrderNow.length - 1] : undefined;
    const phase1LastWallNoNow = phase1LastWallNow
      ? Number(getWallNo(phase1LastWallNow))
      : null;
    const phase2LastWallNoNow = phase2LastWallNow
      ? Number(getWallNo(phase2LastWallNow))
      : null;

    const wallToDynamicStep = (wall: number | null) => {
      if (wall === null) return 0;
      const idx = stepsNow.findIndex((s) => s.wall === `wall_${wall}`);
      return idx >= 0 ? idx : 0;
    };

    let nextStep = stepNow;
    // 🔒 ABSOLUTE TERMINAL — NEVER LEAVE
    if (stepNow === completeIdxNow && stepsNow[stepNow]?.type === "complete") {
      // Do nothing forever once completed
      pollInFlightRef.current = false;
      pollingTimerRef.current = window.setTimeout(poll, 1500);
      return;
    }
    // 🔒 MARKING COMPLETE (backend truth only)
    const isStageComplete =
      data.phase === 2 &&
      !data.running &&
      !data.homeCheckPending &&
      phase2LastWallNoNow !== null &&
      data.doneWall === phase2LastWallNoNow;
    
    if (isStageComplete) {
      if (stageNow < TOTAL_STAGES) {
        const nextStage = stageNow + 1;
        setCurrentStage(nextStage);
        currentStageRef.current = nextStage;
        setForcedPlacement2(false);
        forcedPlacement2Ref.current = false;
        nextStep = 0;
      } else {
        nextStep = completeIdxNow;
      }
    }
    else if (
      data.phase === 1 &&
      phase1LastWallNoNow !== null &&
      data.doneWall === phase1LastWallNoNow &&
      !data.running &&
      !data.homeCheckPending && 
      !forcedPlacement2Ref.current    
    ) {
      setForcedPlacement2(true); // 🔒 lock it
      forcedPlacement2Ref.current = true;
      nextStep = placement2IdxNow >= 0 ? placement2IdxNow : stepNow;
    }
    // 🔒 PLACEMENT 2 — operator-forced, never overridden
    else if (forcedPlacement2Ref.current) {
      nextStep = placement2IdxNow >= 0 ? placement2IdxNow : stepNow;
    }
    // 🟡 HOME CHECK PENDING
    else if (data.homeCheckPending && data.homeCheckWall !== null) {
      nextStep = wallToDynamicStep(data.homeCheckWall);
    }
    // 🟢 MARKING RUNNING
    else if (data.running && data.startedWall !== null) {
      nextStep = wallToDynamicStep(data.startedWall);
    }
    // 🟠 IDLE FALLBACK (safe now, terminal guarded)
    else if (!data.running && data.doneWall !== null) {
      nextStep = wallToDynamicStep(data.doneWall);
    }
    if (nextStep !== stepNow) {
      setCurrentStep(nextStep);
      currentStepRef.current = nextStep;
    }
    // -------------------------------
    // 🔴 Logs (single-line summary only)
    // -------------------------------
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
        Marking of PBU (6-Wall Flow) — Stage {currentStage} / {TOTAL_STAGES}
      </h2>

      <ul className="steps w-full mb-6">
        {flowSteps.map((step, i) => (
          <li
            key={`${step.type}-${step.phase}-${step.wall ?? i}`}
            className={i === currentStep ? "step step-primary" : "step"}
          >
            {step.label}
          </li>
        ))}
      </ul>

      <div className="flex gap-6">
        <img
          src={getStepImage(currentFlowStep)}
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
              {!homeCheckPending && currentFlowStep?.type === "wall" && currentFlowStep.wall && (
                <>Marking Wall {getWallNo(currentFlowStep.wall)} in progress.</>
              )}
              {currentFlowStep?.type === "placement" && currentFlowStep.phase === 1 &&
                "Prepare robot for Placement 1."}
              {currentFlowStep?.type === "placement" && currentFlowStep.phase === 2 &&
                "Prepare robot for Placement 2."}
              {currentFlowStep?.type === "complete" && "Marking complete."}
            </p>
            {activeExcelName && (
              <p className="mt-2 text-xs opacity-70">
                Export file: <span className="font-mono">{activeExcelName}</span>
              </p>
            )}
            <p className="mt-1 text-sm">
              Ensure that the laser leveller is turned on and is facing the wall that is to be marked.
            </p>
          </div>
          {/*
          <div className="bg-black font-mono text-xs rounded p-3 max-h-[220px] overflow-y-auto shadow">
            <div className="text-green-300 mb-1">Backend Output</div>
            {cmdLogs.length === 0 ? (
              <div className="opacity-60 text-green-400">Waiting for backend output…</div>
            ) : (
              cmdLogs.map((l, i) => (
                <div key={i} className={getLogClass(l)}>
                  {l}
                </div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
          */}
          {showErrorBanner && (
            <div className="p-3 bg-red-100 text-red-700 rounded">
              <pre className="whitespace-pre-wrap text-sm">
                {errorMessage}
              </pre>
            </div>
          )}
          {/* HOME CHECK TABLE (backend-driven, stable) */}
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
            {currentStep === 0 && (
              <button className="btn btn-primary" onClick={startPhaseOne} disabled={actionBusy}>
                {actionBusy ? "Working..." : "Next"}
              </button>
            )}
            {currentStep === placement2StepIndex && !isHomeCheckFailed  && (
              <button className="btn btn-primary" onClick={startPhaseTwo} disabled={actionBusy}>
                {actionBusy ? "Working..." : "Next"}
              </button>
            )}
            {running && isCurrentMarkingStep && !hasError && (
              <button className="btn btn-warning" onClick={pauseMarking} disabled={actionBusy}>
                {actionBusy ? "Working..." : "Pause"}
              </button>
            )}
            {isHomeCheckFailed && (
              <button
                className="btn btn-error"
                onClick={retryCurrentWall}
                disabled={actionBusy}
              >
                Retry
              </button>
            )}
            {/* WALL 4 MARKING ERROR → Retry + Continue (to Placement 2) */}
            {isPhase1LastWallMarkingError && (
              <div className="flex gap-2">
                <button
                  className="btn btn-error flex-1"
                  onClick={retryCurrentWall}
                  disabled={actionBusy}
                >
                  Retry
                </button>
                <button
                  className="btn btn-warning flex-1"
                  onClick={continueNextWall}
                  disabled={actionBusy}
                >
                  Continue →
                </button>
              </div>
            )}
            {/* Error / HomeCheck failure */}
            {isRealMarkingError && !isTerminalStep && (
              <div className="flex gap-2">
                <button
                  className="btn btn-error flex-1"
                  onClick={retryCurrentWall}
                  disabled={actionBusy}
                >
                  Retry
                </button>
                <button
                  className="btn btn-warning flex-1"
                  onClick={continueNextWall}
                  disabled={actionBusy}
                >
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
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setShowAutoInstr(false)}
          />
          {/* Panel */}
          <div className="absolute inset-0 flex items-center justify-center p-4">
            <div className="w-full max-w-3xl rounded-xl bg-base-100 shadow-2xl">
              {/* Header */}
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
              {/* Body */}
              <div className="p-5 space-y-4 text-sm leading-6">
                {AUTO_STEPS[autoStep].body}
                <div className="alert alert-info mt-2">
                  <div>
                    Ensure the laser leveller is turned on and facing the active wall. Keep
                    the area clear while the robot is moving.
                  </div>
                </div>
              </div>
              {/* Footer controls */}
              <div className="flex justify-between border-t px-5 py-3">
                <div className="flex gap-2">
                  <button
                    className="btn btn-ghost"
                    onClick={() => setShowAutoInstr(false)}
                  >
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
                    <button
                      className="btn btn-primary"
                      onClick={() => setShowAutoInstr(false)}
                    >
                      Finish
                    </button>
                  )}
                </div>
                {/*
                <div className="text-xs opacity-60">
            running={String(running)} paused={String(paused)} hasError={String(hasError)}{" "}
            homeCheckPending={String(homeCheckPending)}
          </div>
          */}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
export default SixWallFlow;                