import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import type { AxiosRequestConfig } from "axios";

import SelectPBU from "./SelectPBUFile";
import type { FileEntry } from "./SelectPBUFile";
import DetectPBU from "./DetectPBU";
import { API_BASE_URL } from "./config";
import HomePositionCheck from "./HomePositionCheck";
import HomeVerified from "./HomeVerified";
import FourWallFlow from "./FourWallFlow";
import SixWallFlow from "./SixWallFlow";
//import { SetToAutoMode } from "./SetToAutoMode";

// Import images
import ABBHOMEImage from "../assets/ABB_Robot_HOME.jpg";
import FlexPendantImage from "../assets/ABB_Robot_FlexPendant.jpg";
import pushRobotIntoPBUImage from "../assets/PushIntoPBU.jpg";
import RobotPowerONOutside from "../assets/ABB_Robot_Power_ON_outside.jpg";
import RobotPowerOFFOutside from "../assets/ABB_Robot_Power_OFF_outside.jpg";
import RobotPowerONInside from "../assets/ABB_Robot_Power_ON_inside.jpg";

const svg = `
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 800'>
  <rect fill='#020133' width='800' height='800'/>
  <g fill='none' stroke='#1C60FF' stroke-width='1'>
    <path d='M769 229L1037 260.9M927 880L731 737 520 660 309 538 40 599 295 764 126.5 879.5 40 599-197 493 102 382-31 229 126.5 79.5-69-63'/>
    <path d='M-31 229L237 261 390 382 603 493 308.5 537.5 101.5 381.5M370 905L295 764'/>
    <path d='M520 660L578 842 731 737 840 599 603 493 520 660 295 764 309 538 390 382 539 269 769 229 577.5 41.5 370 105 295 -36 126.5 79.5 237 261 102 382 40 599 -69 737 127 880'/>
    <path d='M520-140L578.5 42.5 731-63M603 493L539 269 237 261 370 105M902 382L539 269M390 382L102 382'/>
    <path d='M-222 42L126.5 79.5 370 105 539 269 577.5 41.5 927 80 769 229 902 382 603 493 731 737M295-36L577.5 41.5M578 842L295 764M40-201L127 80M102 382L-261 269'/>
  </g>
  <g fill='#8F8B8B'>
    <circle cx='769' cy='229' r='5'/><circle cx='539' cy='269' r='5'/><circle cx='603' cy='493' r='5'/>
    <circle cx='731' cy='737' r='5'/><circle cx='520' cy='660' r='5'/><circle cx='309' cy='538' r='5'/>
    <circle cx='295' cy='764' r='5'/><circle cx='40' cy='599' r='5'/><circle cx='102' cy='382' r='5'/>
    <circle cx='127' cy='80' r='5'/><circle cx='370' cy='105' r='5'/><circle cx='578' cy='42' r='5'/>
    <circle cx='237' cy='261' r='5'/><circle cx='390' cy='382' r='5'/>
  </g>
</svg>
`.trim();

const bgDataUri = `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;

type CurrentState =
  | "detect_PBU"
  | "select_PBU"
  | "success"
  | "error"
  | "shutdown"
  | "checked_ok"
  | "invalid_model"
  | "home_position_setup"
  | "home_verified"
  //| "set_to_auto_mode"
  | "four_wall_flow"
  | "six_wall_flow";

const views = {
  select_PBU: {
    title: "File Selection Menu",
    variant: "primary",
    primaryText: "Start",
    showSpinner: false,
  },
  detect_PBU: {
    title: "Start Menu",
    variant: "primary",
    primaryText: "Start",
    showSpinner: false,
  },
  success: {
    title: "USB drive detected",
    variant: "success",
    primaryText: "Check selection",
    showSpinner: false,
  },
  error: {
    title: "An error has occurred",
    variant: "error",
    primaryText: "Try Again",
    showSpinner: false,
  },
  shutdown: {
    title: "Please power off the machine",
    variant: "neutral",
    primaryText: "",
    showSpinner: false,
  },
  home_position_setup: {
    title: "Home position setup",
    variant: "success",
    primaryText: "Verify HOME position",
    showSpinner: false,
  },
  home_verified: {
    title: "Move Robot into PBU",
    variant: "success",
    primaryText: "Next Step",
    showSpinner: false,
  },
  /*set_to_auto_mode: {
    title: "Robot automatic mode setup",
    variant: "success",
    primaryText: "Next Step",
    showSpinner: false,
  },*/
  four_wall_flow: {
    title: "Marking of PBU (Four Walls)",
  },
  six_wall_flow: {
    title: "Marking of PBU (Six Walls)",
  },
} as const;

async function postWithRetries(
  url: string,
  data?: any,
  config?: AxiosRequestConfig,
  tries = 10,
  delayMs = 400
) {
  let lastErr: any;
  for (let i = 0; i < tries; i++) {
    try {
      return await axios.post(url, data, { timeout: 0, ...(config || {}) });
    } catch (e: any) {
      lastErr = e;
      const code = e?.response?.status;
      if (code && code !== 409 && code < 500) break;
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }
  throw lastErr;
}

export default function Status() {
  const [appState, setAppState] = useState<CurrentState>("select_PBU");
  const v = views[appState];

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jointTarget, setJointTarget] = useState<any | null>(null);
  const [walls, setWalls] = useState<WallInfo[]>([]);
  const [maxWall, setMaxWall] = useState<number | null>(null);
  const [currentWall, setCurrentWall] = useState<number>(1);

  const [autoBootStatus, setAutoBootStatus] = useState<
    "idle" | "booting" | "ok" | "error"
  >("idle");
  const [autoBootError, setAutoBootError] = useState<string | null>(null);

  interface JointTargetResponse {
    ok: boolean;
    jointtarget: any;
  }

  const [fileEntries, setFileEntries] = useState<FileEntry[]>([]);
  const [pathByFilename, setPathByFilename] = useState<Record<string, string>>(
    {}
  );

  // NEW: remember which Excel has already been processed by detectwalls
  const [processedExcel, setProcessedExcel] = useState<string | null>(null);

  async function handleGetDirectory() {
    try {
      const res = await axios.get(`${API_BASE_URL}/getdirectory`);

      if (!res.data.ok) {
        console.error("Backend returned not ok");
        return;
      }

      const lines: string[] = res.data.data || [];

      const entries: FileEntry[] = lines
        .filter((line) => line.toLowerCase().includes("found"))
        .map((line) => {
          const fullPath = line.replace(/found\s*\w*\s*:?/i, "").trim();
          const filename = fullPath.split("/").pop() || fullPath;
          return { filename, fullPath };
        });

      setFileEntries(entries);

      const map: Record<string, string> = {};
      for (const e of entries) map[e.filename] = e.fullPath;
      setPathByFilename(map);
    } catch (err) {
      console.error("getdirectory error:", err);
    }
  }

  async function getRobotJointTarget(): Promise<any> {
    console.log("API triggered at /jointtarget/connection");
    try {
      const res = await axios.get(`${API_BASE_URL}/jointtarget/connection`);
      console.log("JOINTTARGET RAW RESPONSE:", res.data);
      return res.data;
    } catch (err) {
      setAppState("home_verified");
      return { ok: false, data: [] };
    }
  }

  interface ReadDirectoryResponse {
    ok: boolean;
    data: string[];
  }
  interface WallRow {
    [key: string]: any;
  }

  interface WallInfo {
    wall: string;
    count: number;
    rows: WallRow[];
  }

  const [directory, setDirectory] = useState<string>("");
  async function readDirectory(): Promise<ReadDirectoryResponse> {
    console.log("readDirectoryAPI triggered!");
    const res = await axios.post<ReadDirectoryResponse>(
      `${API_BASE_URL}/read_directory`
    );
    if (res.data?.ok) {
      console.log(res.data);
      setAppState("home_position_setup");
    } else {
      console.log(res.data);
    }
    return res.data;
  }

  const [excelfile, setExcelfile] = useState<string>(
    "/root/catkin_ws/newui_Greyform/TERRAHL2-FP-MB-T1am(JMB)_out.xlsx"
  );
  const [excelFiles, setExcelFiles] = useState<string[]>([]);
  const [meshfile, setMeshfile] = useState<string>("SIMTech_L_PBU.stl");
  const [file_direct, set_file_direct] = useState<string>(
    "/home/ros_user/catkin_ws/"
  );

  type WallRowDict = { [key: string]: string };
  interface FileExecuteResult {
    folder: string;
    excelFile: string;
    excelFiles: string[]; 
    maxWall: number;
    allWalls: number[];
    wallRows: Record<number, number>;
    wallDetails: Record<number, WallRowDict[]>;
    rawLines: string[];
  }

  useEffect(() => {
    if (appState === "select_PBU") {
      (async () => {
        await handleGetDirectory();
      })();
    }
  }, [appState]);

  const [allWalls, setAllWalls] = useState<number[]>([]);
  const [wallRows, setWallRows] = useState<Record<number, number>>({});
  const [wallDetails, setWallDetails] =
    useState<Record<number, WallRowDict[]>>({});

  async function handleFileExecute(folderPath: string): Promise<FileExecuteResult> {
  console.log("➡ handleFileExecute() starting with folder:", folderPath);

  const res = await axios.post(`${API_BASE_URL}/file_execute_data`, {
    folder: folderPath,   // ✅ CHANGED
  });

  const lines: string[] = res.data.data || [];

  // ---------------------------------------------
  // NEW: array of excel files
  // ---------------------------------------------
  const excelFiles: string[] = [];

  // keep backward compatibility
  let excelFile = "";

  let folder = folderPath;   // ✅ now comes from argument
  let maxWall = 0;
  let allWalls: number[] = [];
  let wallRows: Record<number, number> = {};
  const wallLines: Record<number, string[]> = {};

  let currentWall: number | null = null;
  let currentBlock: string[] = [];

  // ---------------------------------------------------------
  // 1. FIRST PASS – PARSE TOP-LEVEL INFO
  // ---------------------------------------------------------
  for (const rawLine of lines) {
    const line = (rawLine ?? "").trim();

    if (!line) continue;

    if (line.startsWith("Folder:")) {
      folder = line.replace("Folder:", "").trim();
    }

    // ---------------------------------------------
    // collect ALL Working Excel paths
    // ---------------------------------------------
    if (line.startsWith("Working Excel:")) {
      const path = line.replace("Working Excel:", "").trim();
      excelFiles.push(path);
      excelFile = path; // last one for backward compatibility
    }

    if (line.startsWith("MaxWall") || line.startsWith("Max wall number:")) {
      const parts = line.split(":");
      if (parts.length >= 2) maxWall = Number(parts[1].trim());
    }

    if (line.startsWith("Walls Found") || line.startsWith("All walls found:")) {
      const match = line.match(/\[(.*)\]/);
      if (match) {
        allWalls = match[1]
          .split(",")
          .map((n) => Number(n.trim()))
          .filter((n) => !isNaN(n));
      }
    }

    // Wall X — Y rows
    const upper = line.toUpperCase();
    if (upper.includes("WALL") && upper.includes("ROWS")) {
      const nums = line.match(/\d+/g);
      if (nums && nums.length >= 2) {
        const wallNum = Number(nums[0]);
        const rowCount = Number(nums[1]);

        if (currentWall !== null && currentBlock.length > 0) {
          wallLines[currentWall] = currentBlock;
        }

        currentWall = wallNum;
        wallRows[wallNum] = rowCount;
        currentBlock = [line];
        continue;
      }
    }

    if (currentWall !== null) currentBlock.push(line);
  }

  if (currentWall !== null && currentBlock.length > 0) {
    wallLines[currentWall] = currentBlock;
  }

  // ---------------------------------------------------------
  // 2. SECOND PASS – PARSE FULL ROW DETAILS
  // ---------------------------------------------------------
  const wallDetails: Record<number, WallRowDict[]> = {};

  for (const [wallStr, linesArr] of Object.entries(wallLines)) {
    const wall = Number(wallStr);
    const rows: WallRowDict[] = [];
    let currentRow: WallRowDict | null = null;

    for (const raw of linesArr) {
      const clean = (raw ?? "").trim();
      if (!clean) continue;

      const rm = clean.match(/^Row\s+(\d+):/i);
      if (rm) {
        if (currentRow) rows.push(currentRow);
        currentRow = { Row: rm[1] };
        continue;
      }

      if (!currentRow) continue;

      const kv = clean.match(/^(.+?):\s*(.*)$/);
      if (kv) {
        const key = kv[1].trim();
        const value = kv[2].trim();
        currentRow[key] = value;
      }
    }

    if (currentRow) rows.push(currentRow);
    wallDetails[wall] = rows;
  }

  // ---------------------------------------------------------
  // RETURN
  // ---------------------------------------------------------
  return {
    folder,
    excelFile,      // last excel (compat)
    excelFiles,     // ⭐ ALL excels found in subfolders
    maxWall,
    allWalls,
    wallRows,
    wallDetails,
    rawLines: lines,
  };
}

  async function handleStartLayout(maxWallValue: number | null) {
    console.log("➡️ Starting layout with maxWall =", maxWallValue);
    if (maxWallValue === null) {
      console.warn("⚠ No maxWall yet, cannot start layout");
      setError("Excel file is missing Wall Number column");
      setAppState("error");
      return;
    }
    if (maxWallValue === 4) {
      setAppState("four_wall_flow");
    } else if (maxWallValue === 6) {
      setAppState("six_wall_flow");
    } else {
      console.error("❌ Unsupported wall count:", maxWallValue);
      setError(`Excel contains invalid wall count: ${maxWallValue}`);
      setAppState("error");
    }
  }

 const handleFileExecuteAndStartLayout = async (folderPath: string) => {
  console.log("▶ handleFileExecuteAndStartLayout (folder):", folderPath);

  if (!folderPath) {
    console.error("❌ handleFileExecuteAndStartLayout called with undefined folderPath");
    setError("Missing folder path");
    setAppState("error");
    return;
  }

  // ✅ If this folder has already been processed, DO NOT run detectwalls again.
  // This prevents extra folder creation & keeps wallDetails intact.
  if (file_direct === folderPath && maxWall !== null) {
    console.log("🔁 Re-using cached detectwalls result for folder:", folderPath);
    console.log("   cached folder =", file_direct);
    console.log("   cached maxWall =", maxWall);
    console.log("   cached wallDetails keys =", Object.keys(wallDetails));
    await handleStartLayout(maxWall);
    return;
  }

  try {
    const result = await handleFileExecute(folderPath); // ✅ CHANGED

    // If you still want to cache, cache by folder now
    // (processedExcel no longer makes sense if you start from folder)
    setProcessedExcel(result.excelFile); // optional: keep if you still use it elsewhere

    set_file_direct(result.folder);
    setExcelFiles(result.excelFiles);
    setExcelfile(result.excelFile);

    setMaxWall(result.maxWall);
    setAllWalls(result.allWalls);
    setWallRows(result.wallRows);
    setWallDetails(result.wallDetails);

    console.log("📂 folder:", result.folder);
    console.log("📄 excelFiles:", result.excelFiles);
    console.log("📄 excelFile:", result.excelFile);
    console.log("🔢 maxWall:", result.maxWall);
    console.log("📊 wallRows:", result.wallRows);

    if (result.wallDetails[1]?.[0]) {
      console.log("🧱 wallDetails[1][0]:", result.wallDetails[1][0]);
    } else {
      console.log("⚠ no wallDetails[1][0]");
    }

    await handleStartLayout(result.maxWall);
  } catch (err) {
    console.error("❌ Failed to execute folder:", err);
    setError(err instanceof Error ? err.message : String(err));
    setAppState("error");
  }
};


  return (
    <>
      {appState !== "four_wall_flow" && appState !== "six_wall_flow" && (
        <div
          className="hero min-h-screen relative bg-cover bg-center"
          style={{ backgroundImage: `url("${bgDataUri}")` }}
        >
          <div className="hero-overlay bg-neutral/50" />
          <div className="hero-content text-neutral-content text-center relative">
            <div className="max-w-max space-y-5">
              <h1 className="text-4xl md:text-5xl font-bold">{v.title}</h1>

              {appState === "detect_PBU" && (
                <DetectPBU v={v} searchFilePath={readDirectory} />
              )}

              {appState === "select_PBU" && (
                <SelectPBU
                  files={fileEntries}
                  onConfirm={async (file) => {
                    if (!file) return;

                    const selectedFolder = file.fullPath;

                    console.log("Selected PBU Folder:", selectedFolder);
                    await handleFileExecuteAndStartLayout(selectedFolder);

                    setAppState("home_position_setup");
                  }}
                />
              )}
              {/*
              {appState === "home_position_setup" && (
                <HomePositionCheck
                  ABBHOMEImage={ABBHOMEImage}
                  RobotPowerONOutside={RobotPowerONOutside}
                  v={v}
                  verifyHomePosition={getRobotJointTarget}
                  onHomeVerified={() => setAppState("home_verified")}
                />
              )}*/}
                {appState === "home_position_setup" && (
                  <>
                    // AUTO SKIP HOME CHECK
                    {setAppState("home_verified")}
                  </>
                )}
              {appState === "home_verified" && (
                <HomeVerified
                  pushRobotIntoPBUImage={pushRobotIntoPBUImage}
                  FlexPendantImage={FlexPendantImage}
                  RobotPowerOFFOutside={RobotPowerOFFOutside}
                  RobotPowerONInside={RobotPowerONInside}
                  v={v}
                  onNext={() => handleFileExecuteAndStartLayout(file_direct)}
                />
              )}

              {/*
              {appState === "set_to_auto_mode" && (
                <SetToAutoMode/>
              )}
                */}

              {appState === "error" && (
                <div className="text-red-400">
                  <h2 className="text-2xl font-bold mb-2">
                    {error ?? "Unknown error"}
                  </h2>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {appState === "four_wall_flow" && (
        <FourWallFlow wallDetails={wallDetails}
          maxWall={maxWall ?? 0}
          excelFiles={excelFiles}
          meshfile={meshfile}
          folderdirectory={file_direct}/>
      )}

      {appState === "six_wall_flow" && (
        <SixWallFlow
          wallDetails={wallDetails}
          maxWall={maxWall ?? 0}
          excelFiles={excelFiles}
          meshfile={meshfile}
          folderdirectory={file_direct}
        />
      )}
    </>
  );
}
