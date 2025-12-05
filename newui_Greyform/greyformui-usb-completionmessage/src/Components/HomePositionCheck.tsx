import React, { useState, useEffect } from "react";

interface Props {
  ABBHOMEImage: string;
  RobotPowerONOutside: string;
  v: { variant: string; primaryText: string };
  verifyHomePosition?: () => void | Promise<any>;
  onHomeVerified?: () => void;
}

type JointMap = Record<string, number>;

const HomePositionCheck: React.FC<Props> = ({
  ABBHOMEImage,
  RobotPowerONOutside,
  v,
  verifyHomePosition,
  onHomeVerified,
}) => {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [jointTarget, setJointTarget] = useState<JointMap | null>(null); // j0..j5
  const [raxValues, setRaxValues] = useState<JointMap | null>(null);     // rax_1..rax_6

  const extractLines = (res: any): string[] => {
    if (!res) return ["<empty response>"];
    if (Array.isArray(res?.data)) return res.data.map(String);
    if (typeof res?.data === "string") return res.data.split(/\r?\n/);
    if (Array.isArray(res)) return res.map(String);
    return ["<unknown response format>"];
  };

  const handleVerify = async () => {
    setLoading(true);
    setError(null);

    try {
      let rawRes: any;
      if (verifyHomePosition) {
        const maybe = verifyHomePosition();
        rawRes = maybe instanceof Promise ? await maybe : maybe;
      } else {
        const resp = await fetch("/jointtarget/connection");
        rawRes = await resp.json();
      }

      const dataArr: any[] | undefined = rawRes?.data;
      extractLines(rawRes); // still available if you log raw lines

      if (Array.isArray(dataArr)) {
        // line 2: '{"rax_1": ... }'
        const raxRaw = dataArr.at(2);
        if (raxRaw && typeof raxRaw === "string") {
          try {
            const raxObj = JSON.parse(raxRaw) as JointMap;
            setRaxValues(raxObj);
          } catch (err) {
            console.warn("Failed to parse rax values:", err);
          }
        } else if (raxRaw && typeof raxRaw === "object") {
          setRaxValues(raxRaw as JointMap);
        }

        // second last: "{'j0': 4.71, ...}"
        const jtRaw = dataArr.at(-2);
        let jtObj: JointMap | null = null;

        if (jtRaw) {
          if (typeof jtRaw === "string") {
            try {
              const cleaned = jtRaw.replace(/'/g, '"');
              jtObj = JSON.parse(cleaned);
            } catch (err) {
              console.warn("Failed to parse joint target:", err);
            }
          } else if (typeof jtRaw === "object") {
            jtObj = jtRaw as JointMap;
          }
        }
        setJointTarget(jtObj);
      }

      const last = rawRes?.data?.at?.(-1);
      if (last === "True") {
        setStatus("HOME VERIFIED");
        alert("Robot is in HOME position. Moving to next step");
        onHomeVerified?.();
      } else if (last === "False") {
        setStatus("NOT HOME");
        alert("Robot is NOT in HOME position.");
      } else {
        setStatus("UNKNOWN");
        alert("Could not determine HOME.");
      }
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleVerify();
  }, []);

  // Build combined rows: J0..J5 with matching rax_1..rax_6 by index
  const combinedRows =
    jointTarget && raxValues
      ? Object.entries(jointTarget).map(([jKey, targetVal], index) => {
          const rKey = `rax_${index + 1}`;
          const currentVal = raxValues[rKey];
          return {
            label: jKey.toUpperCase(), // J0, J1, ...
            current: currentVal,
            target: targetVal,
          };
        })
      : [];

  return (
    <div className="w-full">
      {/* TOP ROW: cards on the left, table on the right */}
      <div className="flex flex-row gap-6 items-start">
        {/* LEFT: cards */}
        <div className="flex flex-row gap-4 overflow-x-auto">
          <div className="card bg-base-100 w-96 shadow-sm">
            <div className="card-body">
              <h2 className="card-title text-black">1. Power on ABB Robot</h2>
              <p className="text-black">Ensure robot is powered ON.</p>
            </div>
            <figure>
              <img src={RobotPowerONOutside} alt="ABB Robot ON" />
            </figure>
          </div>

          <div className="card bg-base-100 w-96 shadow-sm">
            <div className="card-body">
              <h2 className="card-title text-black">2. Move robot to HOME</h2>
              <p className="text-black">
                Using the image as a reference, move the robot to HOME.
              </p>
            </div>
            <figure>
              <img src={ABBHOMEImage} alt="HOME Position" />
            </figure>
          </div>
        </div>

        {/* RIGHT: combined table in white box */}
        <div className="flex-1 min-w-[260px]">
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <table className="w-full text-sm text-black">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-2 text-left">Axis</th>
                  <th className="px-4 py-2 text-right">Current Position</th>
                  <th className="px-4 py-2 text-right">Target HOME</th>
                </tr>
              </thead>
              <tbody>
                {combinedRows.length > 0 ? (
                  combinedRows.map((row) => (
                    <tr key={row.label} className="border-t border-gray-200">
                      <td className="px-4 py-2 font-semibold">{row.label}</td>
                      <td className="px-4 py-2 text-right">
                        {row.current !== undefined
                          ? Number(row.current).toFixed(3) + " deg"
                          : "-"}
                      </td>
                      <td className="px-4 py-2 text-right">
                        {Number(row.target).toFixed(3) + " deg"}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan={3}
                      className="px-4 py-3 text-center text-gray-500"
                    >
                      Waiting for joint data...
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* BOTTOM: button + status */}
      <div className="mt-4">
        <button
          className={`btn btn-${v.variant} lg:btn-lg px-6`}
          disabled={loading}
          onClick={handleVerify}
        >
          {loading ? "Verifying..." : v.primaryText}
        </button>

        {error && <div className="text-red-600 mt-2">Error: {error}</div>}

        {status && (
          <div className="mt-2 text-lg font-bold">
            {status === "HOME VERIFIED" && (
              <span className="text-green-600">✔ HOME Verified</span>
            )}
            {status === "NOT HOME" && (
              <span className="text-red-600">✖ Not at HOME</span>
            )}
            {status === "UNKNOWN" && (
              <span className="text-yellow-600">
                ⚠ Unable to determine the HOME position
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePositionCheck;
