import React from "react";

interface Props {
  pushRobotIntoPBUImage: string;
  LevellerImage: string;
  RemoteControlImage: string;
  v: {
    variant: string;
    primaryText: string;
  };
}

const PushIntoPBUAndLevel: React.FC<Props> = ({
  pushRobotIntoPBUImage,
  LevellerImage,
  RemoteControlImage,
  v
}) => {
  return (
    <div className="flex flex-row w-full gap-4">
      <div className="card bg-base-100 flex-1 max-w-sm shadow-sm">
        <div className="card-body">
          <h2 className="card-title text-black">1. Push the robot into the PBU</h2>
        </div>
        <figure>
          <img src={pushRobotIntoPBUImage} alt="Push Robot Into PBU" />
        </figure>
      </div>
      <div className="card bg-base-100 flex-1 max-w-sm shadow-sm">
        <div className="card-body">
          <h2 className="card-title text-black">2. Turn on the Leveller as shown below</h2>
        </div>
        <figure>
          <img src={LevellerImage} alt="Leveller" />
        </figure>
      </div>
      <div className="card bg-base-100 flex-1 max-w-sm shadow-sm">
        <div className="card-body">
          <h2 className="card-title text-black">3. Use the Remote Control as shown below to horizontally level the robot</h2>
        </div>
        <figure>
          <img src={RemoteControlImage} alt="Remote Control" />
        </figure>
      </div>
    </div>
  );
};

export default PushIntoPBUAndLevel;