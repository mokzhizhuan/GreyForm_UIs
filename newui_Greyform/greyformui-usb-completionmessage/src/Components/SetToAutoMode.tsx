import { useState } from "react";

import step1 from "../assets/Manual_to_auto_1.jpeg";
import step2 from "../assets/Manual_to_auto_2.jpeg";
import step3 from "../assets/Manual_to_auto_3.jpeg";
import step4 from "../assets/Manual_to_auto_4.jpeg";
import step5 from "../assets/Manual_to_auto_5.jpeg";
import step6 from "../assets/Manual_to_auto_6.jpeg";
import step7 from "../assets/Manual_to_auto_7.jpeg";

type StepData = {
  title: string;
  description: string;
  image: string;
};

const STEPS: StepData[] = [
  {
    title: "Step 1",
    description: "Click on the 'Auto' button.",
    image: step1,
  },
  {
    title: "Step 2",
    description: "You should see the following prompt pictured below. Click on 'Acknowledge'.",
    image: step2,
  },
  {
    title: "Step 3",
    description: "'Mode' should now be highlighted in blue.",
    image: step3,
  },
  {
    title: "Step 4",
    description: "Click on the 'Motors on' button.",
    image: step4,
  },
  {
    title: "Step 5",
    description: "The following prompt should show. Click on 'Yes'.",
    image: step5,
  },
  {
    title: "Step 6",
    description: "'Motors on' should now be highlighted in blue.",
    image: step6,
  },
  {
    title: "Step 7",
    description: "You should be able to see the operator message as 'Idling...'",
    image: step7,
  },
];

export function SetToAutoMode() {
  const [stepIndex, setStepIndex] = useState(0);
  const step = STEPS[stepIndex];

  const isFirst = stepIndex === 0;
  const isLast = stepIndex === STEPS.length - 1;

  return (
    <div className="space-y-4">
      {/* Text panel */}
      <div className="flex justify-center">
        <div className="menu bg-base-200 rounded-box p-4 shadow">
            <p className="text-black font-semibold text-lg">
            {step.title}
            </p>
            <p className="text-black text-sm mt-1">
            {step.description}
            </p>
        </div>
      </div>

      {/* Image */}
      <div className="flex justify-center">
        <img
          src={step.image}
          alt={step.title}
          className="w-full max-w-3xl h-auto object-contain rounded-lg shadow"
        />
      </div>

      {/* Navigation buttons */}
      <div className="flex justify-between items-center pt-2">
        <button
          className="btn btn-outline"
          disabled={isFirst}
          onClick={() => setStepIndex((s) => s - 1)}
        >
          ◀ Previous
        </button>

        <span className="text-sm text-gray-500">
          Step {stepIndex + 1} of {STEPS.length}
        </span>

        <button
          className="btn btn-primary"
          disabled={isLast}
          onClick={() => setStepIndex((s) => s + 1)}
        >
          Next ▶
        </button>
      </div>
    </div>
  );
}
