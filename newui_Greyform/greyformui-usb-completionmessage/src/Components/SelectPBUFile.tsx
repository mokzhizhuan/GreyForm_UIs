import React from "react";

export type FileEntry = {
  filename: string;   // e.g. "PBU_TERRAHL2_wall_2.xlsx"
  fullPath: string;   // e.g. "/home/.../PBU_TERRAHL2_wall_2.xlsx"
};

interface SelectPBUFileProps {
  files: FileEntry[];
  onConfirm?: (file: FileEntry | null) => void;
}

const SelectPBUFile: React.FC<SelectPBUFileProps> = ({ files, onConfirm }) => {
  const [selectedFilename, setSelectedFilename] = React.useState<string | null>(
    null
  );

  const handleToggle = (filename: string) => {
    setSelectedFilename((prev) => (prev === filename ? null : filename));
  };

  const handleConfirm = () => {
    if (!onConfirm) return;
    if (!selectedFilename) {
      onConfirm(null);
      return;
    }
    const selected = files.find((f) => f.filename === selectedFilename) || null;
    onConfirm(selected);
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-black">PBU Excel Files</h2>
      </div>

      <ul role="list" className="divide-y divide-gray-200">
        {files.map((f) => {
          const isSelected = selectedFilename === f.filename;
          return (
            <li
              key={f.fullPath}
              className={`p-3 sm:p-4 ${
                isSelected ? "bg-base-200" : "hover:bg-base-200"
              }`}
            >
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  className="checkbox"
                  aria-label={`Select ${f.filename}`}
                  checked={isSelected}
                  onChange={() => handleToggle(f.filename)}
                />
                <button
                  type="button"
                  className="min-w-0 flex-1 text-left"
                  onClick={() => handleToggle(f.filename)}
                >
                  <span className="font-medium truncate text-black">
                    {f.filename}
                  </span>
                  {/*
                  <div className="text-xs text-gray-500 truncate">
                    {f.fullPath}
                  </div>
                  */}
                </button>
              </div>
            </li>
          );
        })}
      </ul>

      <div className="p-3 border-t border-gray-200 flex items-center gap-2">
        <button
          className="btn btn-sm"
          disabled={!selectedFilename}
          onClick={handleConfirm}
        >
          Select File
        </button>
      </div>
    </div>
  );
};

export default SelectPBUFile;
