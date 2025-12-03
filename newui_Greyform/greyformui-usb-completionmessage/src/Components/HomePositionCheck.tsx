import React, { useState } from "react";

interface Props {
  ABBHOMEImage: string;
  RobotPowerONOutside: string;
  v: { variant: string; primaryText: string };
  verifyHomePosition?: () => void | Promise<any>;
}

const HomePositionCheck: React.FC<Props> = ({
  ABBHOMEImage,
  RobotPowerONOutside,
  v,
  verifyHomePosition,
}) => {
  const [loading, setLoading] = useState(false);
  const [rawLines, setRawLines] = useState<string[]>([]);
  const [robotData, setRobotData] = useState<any>({
    rax: null,
    joints: null,
  });
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // --------------------------------------------------------
  // 1) Extract raw text lines from backend response
  // --------------------------------------------------------
  const extractLines = (res: any): string[] => {
    if (!res) return ["<empty response>"];

    if (Array.isArray(res?.data)) return res.data.map(String);
    if (typeof res?.data === "string") return res.data.split(/\r?\n/);
    if (Array.isArray(res)) return res.map(String);

    return ["<unknown response format>"];
  };

  // --------------------------------------------------------
  // 2) Extract rax values AND j0–j6 from lines
  // --------------------------------------------------------
  const parseRobotValues = (lines: string[]) => {
    const parsed = {
      rax: null as any,
      joints: null as any,
      inHome: null as any,
    };

    for (const ln of lines) {
      const match = ln.match(/\{.*\}/);
      if (!match) continue;

      try {
        const json = JSON.parse(match[0]);

        if ("rax_1" in json) parsed.rax = json;
        if ("j0" in json) parsed.joints = json;
      } catch (_) {}
    }

    return parsed;
  };

  // --------------------------------------------------------
  // 3) HOME determination logic
  // Adjust thresholds if needed
  // --------------------------------------------------------

  // --------------------------------------------------------
  // 4) Verify button handler
  // --------------------------------------------------------
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

      const lines = extractLines(rawRes);
      setRawLines(lines);

      const parsed = parseRobotValues(lines);
      setRobotData(parsed);

      const last = rawRes.data.at(-1);
      
      if (last === "True") {
        setStatus("HOME VERIFIED");
        alert("Robot is in HOME position.");
      } else if (last === "False") {
        setStatus("HOME VERIFIED");
        alert("Robot is NOT in HOME position.");
      } else {
        setStatus("UNKNOWN");
        alert(
          "Could not determine HOME."
        );
      }
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------------
  // UI
  // --------------------------------------------------------
  return (
    <div className="w-full">
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
            <p className="text-black">Match the image shown.</p>
          </div>
          <figure>
            <img src={ABBHOMEImage} alt="HOME Position" />
          </figure>
        </div>
      </div>

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
              <span className="text-yellow-600">⚠ Unable to determine the HOME position</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePositionCheck;
