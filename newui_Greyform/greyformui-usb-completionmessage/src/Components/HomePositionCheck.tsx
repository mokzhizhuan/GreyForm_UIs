import React from "react";

interface JointTargetResponse {
  ok: boolean;
  jointtarget: any;
}

interface Props {
  ABBHOMEImage: string;
  RobotPowerONOutside: string;
  v: {
    variant: string;
    primaryText: string;
  };
  verifyHomePosition: () => void | Promise<JointTargetResponse>;
  loading?: boolean;
  error?: string | null;
  jointTarget?: any | null;
  appState?: string | null;
}

const HomePositionCheck: React.FC<Props> = ({
  ABBHOMEImage,
  RobotPowerONOutside,
  v,
  verifyHomePosition,
  loading,
  error = null,
  jointTarget = null,
  appState = null,
}) => {
  return (
    <>
      <div className="w-full flex flex-row overflow-x-auto gap-4">
        <div className="card bg-base-100 w-96 shadow-sm">
          <div className="card-body">
            <h2 className="card-title text-black text-left">1. Power on the ABB Robot</h2>
            <p className="text-black text-left">
              Ensure that the ABB robot is powered on and ready for operation.
            </p>
          </div>
          <figure>
            <img src={RobotPowerONOutside} alt="ABB Robot HOME position" />
          </figure>
        </div>
        <div className="card bg-base-100 w-96 shadow-sm">
          <div className="card-body">
            <h2 className="card-title text-black text-left">2. Using the flex pendant, adjust the ABB Robot to HOME position</h2>
            <p className="text-black text-left">
              Ensure that the ABB robot is in the HOME position as illustrated in the photo below.
            </p>
          </div>
          <figure>
            <img src={ABBHOMEImage} alt="ABB Robot HOME position" />
          </figure>
        </div>
        <div className="divider" />
      </div>
      <div className="mt-4">
        <button
          className={`btn btn-${v.variant} md:btn-md lg:btn-lg py-2 px-4 border-b-4
                      border-gray-500 hover:border-gray-700 rounded
                      ${loading ? "text-white" : "text-black"}`}
          onClick={verifyHomePosition}
          disabled={loading}
          aria-busy={loading}
        >
          {loading ? "Connecting..." : v.primaryText}
        </button>

        
        {error && <div className="text-red-600 mt-2">Error: {error}</div>}

        {jointTarget && (
          <pre className="mt-2 max-w-full overflow-auto text-sm bg-gray-100 p-2 rounded">
            {JSON.stringify(jointTarget, null, 2)}
          </pre>
        )}

        {appState === "home_verified" && (
          <div className="mt-2 text-green-600">Home position verified</div>
        )}
      </div>
    </>
  );
};

export default HomePositionCheck;