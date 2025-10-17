import React from "react";

interface Props {
  ABBHOMEImage: string;
  v: {
    variant: string;
    primaryText: string;
  };
  verifyHomePosition: () => void | Promise<void>;
}

const HomePositionCheck: React.FC<Props> = ({
  ABBHOMEImage,
  v,
  verifyHomePosition,
}) => {
  return (
    <div className="w-full overflow-x-auto">
      <div className="card bg-base-100 w-96 shadow-sm">
        <div className="card-body">
          <h2 className="card-title text-black">Is the ABB Robot in HOME position?</h2>
          <p className="text-black">
            Please verify that the ABB robot is in the HOME position as illustrated in the photo below.
          </p>
        </div>
        <figure>
          <img src={ABBHOMEImage} alt="ABB Robot HOME position" />
        </figure>
      </div>
      <div className="divider" />
      <button
        className={`btn btn-${v.variant} md:btn-md lg:btn-lg`}
        onClick={verifyHomePosition}
      >
        {v.primaryText}
      </button>
    </div>
  );
};

export default HomePositionCheck;