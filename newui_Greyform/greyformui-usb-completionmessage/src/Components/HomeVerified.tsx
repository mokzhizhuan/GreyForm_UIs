import React from "react";

interface Props {
  RobotPowerOFFOutside: string;
  pushRobotIntoPBUImage: string;
  RobotPowerONInside: string;
  v: {
    variant: string;
    primaryText: string;
  };
  onNext: () => void;
}

const HomeVerified: React.FC<Props> = ({
  RobotPowerOFFOutside,
  pushRobotIntoPBUImage,
  RobotPowerONInside,
  v,
  onNext
}) => {
  return (
    <>
      <div className="flex flex-row w-full gap-4">
        <div className="card bg-base-100 flex-1 max-w-xs shadow-sm">
          <div className="card-body">
            <h2 className="card-title text-black">1. Turn off the ABB Robot</h2>
          </div>
          <figure>
            <img src={RobotPowerOFFOutside} alt="Robot Power Off Outside" />
          </figure>
        </div>
        <div className="card bg-base-100 flex-1 max-w-xs shadow-sm">
          <div className="card-body">
            <h2 className="card-title text-black">2. Push the robot into the PBU</h2>
          </div>
          <figure>
            <img src={pushRobotIntoPBUImage} alt="Push Robot Into PBU" />
          </figure>
        </div>
        <div className="card bg-base-100 flex-1 max-w-xs shadow-sm">
          <div className="card-body">
            <h2 className="card-title text-black">3. Power on the ABB Robot</h2>
          </div>
          <figure>
            <img src={RobotPowerONInside} alt="Robot Power On Inside" />
          </figure>
        </div>
      </div>
      <div className="mt-4">
        <button
          className={`btn btn-${v.variant} md:btn-md lg:btn-lg py-2 px-4 border-b-4
                      border-gray-500 hover:border-gray-700 rounded`}
          onClick={() => {
            onNext();
          }}
        >
          {v.primaryText}
        </button>
      </div>
    </>
  );
};

export default HomeVerified;
