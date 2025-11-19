import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

import placementOne from "../assets/four_wall_flow/4_wall_flow_placement1.jpg";
import wallMarking from "../assets/four_wall_flow/wall_marking_4_walls.jpg";
import { API_BASE_URL } from "./config";

type StepStatus = "idle" | "pending" | "success" | "error";

const FourWallFlow: React.FC = () => {
  const steps = ["Placement", "Wall 2", "Wall 3", "Wall 4", "Marking Complete"];
  const images = [
    placementOne,
    wallMarking,
    wallMarking,
    wallMarking,
    wallMarking,
  ];

  const instructions: React.ReactNode[] = [
    <>
      Position the robot facing <strong>wall two</strong> and{" "}
      <strong>1m away</strong> from the wall.
    </>,
    <>
      Click on next step to start marking <strong>wall 2</strong>.
    </>,
    <>
      Click on next step to start marking <strong>wall 3</strong>.
    </>,
    <>
      Click on next step to start marking <strong>wall 4</strong>.
    </>,
    <>Marking complete! You may now proceed to turn off the robot.</>,
  ];

  const [currentStep, setCurrentStep] = useState<number>(0);
  const [status, setStatus] = useState<StepStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);

  // completedSteps: whether each step is already done/verified
  const [completedSteps, setCompletedSteps] = useState<boolean[]>(() =>
    Array(steps.length).fill(false)
  );

  const [closeFailedNote, setCloseFailedNote] = useState<string | null>(null);
  const pollingRef = useRef<number | null>(null);
  const mountedRef = useRef<boolean>(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
      }
    };
  }, []);

  // derive a user-facing status message based on step and status
  const statusMessage = (() => {
    if (status === "pending") {
      const label = steps[currentStep] ?? "";
      if (currentStep === 0) return "Validating placement — please wait...";
      return `Please wait, the robot is now marking ${label}...`;
    }

    if (status === "success") {
      if (currentStep === 0)
        return "Placement verified. Click on Next Step to continue.";
      return "Step completed. Please proceed to the next step.";
    }

    if (status === "error") {
      return errorMessage ? `Error: ${errorMessage}` : "Operation failed";
    }

    if (currentStep === 0) {
      return "Checking robot position — please wait...";
    }

    const wallLabel = steps[currentStep];
    if (progress != null) {
      return `Marking ${wallLabel} — ${progress}% complete`;
    }

    return `Marking ${wallLabel} — in progress...`;
  })();

  const markStepCompleted = (index: number) => {
    setCompletedSteps((prev) => {
      const copy = prev.slice();
      copy[index] = true;
      return copy;
    });
  };

  // Utility to cancel any ongoing polling before retrying
  const cancelPolling = () => {
    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
      pollingRef.current = null;
    }
  };

  // ✅ Only API we keep: validate placement
  const validatePlacement = async (): Promise<void> => {
    setErrorMessage(null);
    setStatus("pending");
    setProgress(null);
    try {
      const res = await axios.post(`${API_BASE_URL}/validate_placement`, {
        step: "placement",
      });

      if (res.data?.ok) {
        setStatus("success");
        markStepCompleted(0);
        setTimeout(() => {
          if (!mountedRef.current) return;
          setStatus("idle");
          setCurrentStep((s) => Math.min(s + 1, steps.length - 1));
        }, 350);
      } else {
        setStatus("error");
        setErrorMessage(res.data?.reason || "Placement validation failed");
      }
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(
        err?.response?.data?.message || err.message || "Placement API error"
      );
    }
  };

  // For steps 1–4: just mark as done locally, no backend call
  const completeStepLocally = () => {
    setStatus("success");
    markStepCompleted(currentStep);
    setTimeout(() => {
      if (!mountedRef.current) return;
      setStatus("idle");
      setProgress(null);
      setCurrentStep((s) => Math.min(s + 1, steps.length - 1));
    }, 350);
  };

  const handleNextClick = async () => {
    if (status === "pending") return;

    // If it just finished successfully, move on
    if (status === "success") {
      cancelPolling();
      setErrorMessage(null);
      setStatus("idle");
      setProgress(null);
      setCurrentStep((s) => Math.min(s + 1, steps.length - 1));
      return;
    }

    // If step already completed, just advance
    if (completedSteps[currentStep]) {
      cancelPolling();
      setErrorMessage(null);
      setStatus("idle");
      setProgress(null);
      setCurrentStep((s) => Math.min(s + 1, steps.length - 1));
      return;
    }

    cancelPolling();
    setErrorMessage(null);

    // Step 0: call validatePlacement (only backend call)
    if (currentStep === 0) {
      await validatePlacement();
      return;
    }

    // Steps 1–3: local-only completion (no /file_execute_data, no /execute_wall_data)
    if (currentStep >= 1 && currentStep <= 3) {
      completeStepLocally();
      return;
    }

    // Final step: just advance (though UI will show Exit button)
    setCurrentStep((s) => Math.min(s + 1, steps.length - 1));
  };

  const handleExit = () => {
    cancelPolling();
    try {
      window.close();
      setTimeout(() => {
        setCloseFailedNote(
          "If the window did not close automatically, please close the window manually."
        );
      }, 300);
      return;
    } catch (e) {
      setCloseFailedNote("Please close the window manually.");
    }
  };

  const isFinalStep = currentStep === steps.length - 1;

  return (
    <>
      <div className="flex flex-col items-center-safe justify-center mb-8">
        <h2 className="text-4xl md:text-5xl font-bold mb-8">Marking of PBU</h2>

        <ul className="steps w-full max-w-lg">
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

            <p className="text-2xl">
              {status === "idle" ? instructions[currentStep] : statusMessage}
            </p>

            {closeFailedNote && (
              <p className="mt-2 text-sm text-gray-600">{closeFailedNote}</p>
            )}
          </div>

          {isFinalStep ? (
            <button
              className="btn btn-error md:btn-md lg:btn-lg py-2 px-4 border-b-4
                           border-gray-500 hover:border-gray-700 rounded
                           text-white"
              onClick={handleExit}
              disabled={status === "pending"}
            >
              Exit
            </button>
          ) : (
            <button
              className={`btn btn-primary md:btn-md lg:btn-lg py-2 px-4 border-b-4
                           border-gray-500 hover:border-gray-700 rounded 
                           ${status === "pending" ? "loading" : ""}`}
              onClick={handleNextClick}
              disabled={currentStep === steps.length - 1 || status === "pending"}
            >
              {status === "error"
                ? "Retry"
                : status === "pending"
                ? "Working..."
                : "Next Step"}
            </button>
          )}
        </div>
      </div>
    </>
  );
};

export default FourWallFlow;
