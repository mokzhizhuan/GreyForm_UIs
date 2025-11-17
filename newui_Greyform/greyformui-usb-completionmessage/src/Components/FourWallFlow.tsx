import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

import placementOne from '../assets/four_wall_flow/4_wall_flow_placement1.jpg';
import wallMarking from '../assets/four_wall_flow/wall_marking_4_walls.jpg';

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
        <>Position the robot facing <strong>wall two</strong> and <strong>1m away</strong> from the wall.</>,
        <>Click on next step to start marking <strong>wall 2</strong>.</>,
        <>Click on next step to start marking <strong>wall 3</strong>.</>,
        <>Click on next step to start marking <strong>wall 4</strong>.</>,
        <>Marking complete! You may now proceed to turn off the robot.</>,
    ];

    const [currentStep, setCurrentStep] = React.useState<number>(0);
    const [status, setStatus] = React.useState<StepStatus>("idle");
    const [errorMessage, setErrorMessage] = React.useState<string|null>(null);
    const [progress, setProgress] = React.useState<number|null>(null);

    // completedSteps: whether each step is already done/verified
    const [completedSteps, setCompletedSteps] = useState<boolean[]>(
        () => Array(steps.length).fill(false)
    );

    const [closeFailedNote, setCloseFailedNote] = React.useState<string | null>(null);
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
            return `Please wait, the robot is now marking ${label}...`;
        }

        if (status === "success") {
            if (currentStep === 0) return "Placement verified. Click on Next Step to continue.";
            return "Marking complete. Please proceed to the next step.";
        }

        if (status === "error") {
            // show either the error message or a generic one
            return errorMessage ? `Error: ${errorMessage}` : "Operation failed";
        }

        // while an operation is running show a step-specific message
        if (currentStep === 0) {
            return "Checking robot position — please wait...";
        }
        // wall marking: show progress if available
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

    // API call to Validate placement: returns success or failure
    const validatePlacement = async (): Promise<void> => {
        setErrorMessage(null);
        setStatus("pending");
        setProgress(null);
        try {
            const res = await axios.post("/api/validate-placement", {
                // include any payload needed (e.g. robot id, coordinates)
                step: "placement",
            });
            // Example response: { ok: true } or { ok: false, reason: '...' }
            if (res.data?.ok) {
                setStatus("success");
                // small delay to show success state then advance
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
            setErrorMessage(err?.response?.data?.message || err.message || "Placement API error");
        }
    };

    // Start marking process for a wall and poll for given wall index until finished
    const startMarkingAndPoll = async (wallIndex: number): Promise<void> => {
        setErrorMessage(null);
        setStatus("pending");
        setProgress(null);
        try {
            // Start marking operation on server. Response returns an operation id.
            const startRes = await axios.post("/api/start-marking", {
                wall: wallIndex + 1,
                // any additional payload...
        });

            const operationId = startRes.data?.operationId;
            if (!operationId) {
                setStatus("error");
                setErrorMessage("Failed to start marking: no operation id returned");
                return;
            }

        // poll function
        const poll = async () => {
            try {
                const statusRes = await axios.get(`/api/marking-status/${operationId}`);
                // expected shape: { status: 'pending' | 'in_progress' | 'finished' | 'failed', progress: 0-100 }
                const s = statusRes.data?.status;
                if (s === "finished") {
                    if (!mountedRef.current) return;
                    setStatus("success");
                    markStepCompleted(wallIndex);
                    // advance after brief pause so user sees success
                    setTimeout(() => {
                        if (!mountedRef.current) return;
                        setStatus("idle");
                        setCurrentStep((cur) => Math.min(cur + 1, steps.length - 1));
                    }, 350);
                    return;
                }
                if (s === "failed") {
                    if (!mountedRef.current) return;
                    setStatus("error");
                    setErrorMessage(statusRes.data?.reason || "Marking failed");
                    return;
                }
                // still in progress -> schedule next poll
                if (!mountedRef.current) return;
                pollingRef.current = window.setTimeout(poll, 1200);
            } catch (pollErr: any) {
                if (!mountedRef.current) return;
                // transient error: schedule retry or surface error
                // Here we retry a few times; for simplicity just schedule another poll.
                pollingRef.current = window.setTimeout(poll, 2000);
            }
        };

        // start first poll
        pollingRef.current = window.setTimeout(poll, 700);
        } catch (err: any) {
            setStatus("error");
            setErrorMessage(err?.response?.data?.message || err.message || "Failed to start marking");
        }
    };

    const handleNextClick = async () => {
        // prevent double clicks while an operation is pending
        if (status === "pending") return;

        // If the current step just succeeded, treat it as completed and advance
        if (status === "success") {
            // ensure any leftover timers are cancelled (safety)
            cancelPolling();
            setErrorMessage(null);
            setStatus("idle");
            setProgress(null);
            setCurrentStep((s) => Math.min(s + 1, steps.length - 1));
            return;
        }

        // If already completed (from a previous success that updated completedSteps),
        // advance immediately (also cancel any polling)
        if (completedSteps[currentStep]) {
            cancelPolling();
            setErrorMessage(null);
            setStatus("idle");
            setProgress(null);
            setCurrentStep((s) => Math.min(s + 1, steps.length - 1));
            return;
        }

        // Clear any previous polling and errors, then run the step-specific API
        cancelPolling();
        setErrorMessage(null);

        if (currentStep === 0) {
            await validatePlacement();
            return;
        }

        if (currentStep >= 1 && currentStep <= 4) {
            await startMarkingAndPoll(currentStep);
            return;
        }

        setCurrentStep((s) => Math.min(s + 1, steps.length - 1));
    };

    // Exit logic, once marking is complete
    const handleExit = () => {
        // Reset any timers and state
        cancelPolling();

        // Browser: attempt to close the window/tab
        try {
            window.close();
            // Give the browser a moment — if window didn't close we show fallback text below
            setTimeout(() => {
                // If still open, show a small user-facing note
                setCloseFailedNote("If the window did not close automatically, please close the window manually.");
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

                {/* Steps indicator - mark the current step as primary */}
                <ul className="steps w-full max-w-lg">
                    {steps.map((label, i) => (
                        <li key={label} className={i === currentStep ? "step step-primary" : "step"}>
                        {label}
                        </li>
                    ))}
                </ul>
            </div>

            <div className="flex flex-row items-stretch gap-4 w-full">
                {/* Image Card for the current step */}
                <div className="max-w-2xl card bg-base-100 shadow-sm flex-shrink-0">
                    <img
                        src={images[currentStep]}
                        alt={`4 Wall Flow ${steps[currentStep]}`}
                        className="block w-full h-auto max-h-[70vh] object-contain"
                    />
                </div>

                {/* Instructions and Next Button */}
                <div className="flex flex-col justify-between w-max items-center-safe self-stretch">
                    <div className="menu bg-base-200 rounded-box w-full max-h-full p-3 text-black">
                        <p className="md:text-2xl"><b>Instructions:</b></p>

                        {/*Instruction Text*/}
                        <p className="text-2xl">
                            {status === "idle" ? instructions[currentStep] : statusMessage}
                        </p>
                    </div>

                    {/* Feedback Section */}
                    {/*}
                    <div className="menu rounded-box w-full max-h-full p-3 text-black">
                        {status === "success" && (
                            <div className="text-green-700">Positioning completed.</div>
                        )}

                        {status === "error" && (
                            <div className="text-red-700">Error: {errorMessage}</div>
                        )}
                    </div>
                    */}

                    {isFinalStep ? (
                        <button
                            className="btn btn-error md:btn-md lg:btn-lg py-2 px-4 border-b-4
                                         border-gray-500 hover:border-gray-700 rounded
                                         text-white"
                            onClick={handleExit}
                            // allow exit as long as not pending; you may require marking to be success before exit
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
                            {status === "error" ? "Retry" : status === "pending" ? "Working..." : "Next Step"}
                        </button>
                    )}
                </div>
            </div>
        </>
    );
};

export default FourWallFlow;
