import React from "react"

interface ReadDirectoryResponse {
  ok: boolean;
  data: string[];
}

interface Props {
  v: {
    variant: string;
    primaryText: string;
  };
  searchFilePath: () => void | Promise<ReadDirectoryResponse>;

}

const DetectPBU: React.FC<Props> = ({
  v,
  searchFilePath,
}) => {
  return (
    <>
      <div className="w-full flex flex-row overflow-x-auto gap-4">
        <div className="divider" />
      </div>
      <div className="mt-4">
        <button
          className={`btn btn-${v.variant} md:btn-md lg:btn-lg py-2 px-4 border-b-4
                      border-gray-500 hover:border-gray-700 rounded`}
          onClick={searchFilePath}
        >
          {v.primaryText}
        </button>
      </div>
    </>
  );
}

export default DetectPBU