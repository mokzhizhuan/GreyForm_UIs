import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import type { AxiosRequestConfig } from "axios";

import SelectPBU from "./SelectPBU";
import DetectPBU from "./DetectPBU";
import { API_BASE_URL } from "./config";
import HomePositionCheck from "./HomePositionCheck";
import HomeVerified from "./HomeVerified";
import FourWallFlow from "./FourWallFlow";
import { WallInfo, ExecuteWallDataResponse } from "./types/walls";

// Import images
import ABBHOMEImage from "../assets/ABB Robot placeholder image.jpg";
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
  | "four_wall_flow";

const views = {
  select_PBU: {
    title: "File Selection Menu",
    variant: "primary",
    primaryText: "Start",
    showSpinner: false,
  },
  detect_PBU: {
    title: "PBU detection",
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
    title: "Error reading USB drive",
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
  four_wall_flow: {
    title: "Marking of PBU",
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
  const [appState, setAppState] = useState<CurrentState>("detect_PBU");
  const v = views[appState];

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jointTarget, setJointTarget] = useState<any | null>(null);

  // Small status for auto-boot (optional)
  const [autoBootStatus, setAutoBootStatus] = useState<
    "idle" | "booting" | "ok" | "error"
  >("idle");
  const [autoBootError, setAutoBootError] = useState<string | null>(null);


  
interface JointTargetResponse {
  ok: boolean;
  jointtarget: any;   // change to a stricter type later if you want
}

// 🔹 Simple helper to call FastAPI
async function getRobotJointTarget(): Promise<JointTargetResponse> {
  console.log("API triggered at /jointtarget/connection");
  const res = await axios.get<JointTargetResponse>(
    `${API_BASE_URL}/jointtarget/connection`
  );
  console.log(res.data)
  if (res.data?.ok){ setAppState("home_verified")} 
  else{
      console.warn("jointtarget returned ok=false", res.data);
    }
} 


interface ReadDirectoryResponse {
  ok: boolean;
  data: string[];
}
// ---------- Request payload ----------


async function readDirectory(): Promise<ReadDirectoryResponse> {
  // no body, just POST
  console.log("readDirectoryAPI triggered!")
  const res = await axios.post<ReadDirectoryResponse>(`${API_BASE_URL}/read_directory`);
  if (res.data?.ok){ 
    console.log(res.data)
    setAppState("home_position_setup")} 
  else{
      console.warn("readDirectoryAPI returned ok=false", res.data);
    }
}

interface RunScriptResponse {
  ok: boolean;
  data: string[];
}
async function executeWallDataForWall(
  walls: WallInfo[],
  wallId: string
): Promise<ExecuteWallDataResponse> {
  const wallData = walls.find((w) => w.wall === wallId);

  if (!wallData) {
    throw new Error(`Wall "${wallId}" not found in walls array`);
  }

  const res = await axios.post<ExecuteWallDataResponse>(
    `${API_BASE_URL}/execute_wall_data`,
    wallData.rows
  );

  return res.data;
}
// Call /run_ros (no body)
async function executeWallDataForWall(
  walls: WallInfo[],
  wallId: string
): Promise<ExecuteWallDataResponse> {
  const wallData = walls.find((w) => w.wall === wallId);

  if (!wallData) {
    throw new Error(`Wall "${wallId}" not found in walls array`);
  }

  const res = await axios.post<ExecuteWallDataResponse>(
    `${API_BASE_URL}/execute_wall_data`,
    wallData.rows
  );

  return res.data;
}

  const handleAdvanceToFourWall = () => {
    setAppState("four_wall_flow");
  };

  // UI
  return (
    <>
      {appState !== "four_wall_flow" && (
        <div
          className="hero min-h-screen relative bg-cover bg-center"
          style={{ backgroundImage: `url("${bgDataUri}")` }}
        >
          <div className="hero-overlay bg-neutral/50" />
          <div className="hero-content text-neutral-content text-center relative">
            <div className="max-w-max space-y-5">
              <h1 className="text-4xl md:text-5xl font-bold">{v.title}</h1>

              {/* Auto boot status display (optional) */}
              <div className="text-sm opacity-80">
                {autoBootStatus === "booting" && (
                  <span className="text-blue-300">
                    Starting ROS & listener…
                  </span>
                )}
                {autoBootStatus === "ok" && (
                  <span className="text-green-300">
                    ROS & listener ready ✅
                  </span>
                )}
                {autoBootStatus === "error" && (
                  <span className="text-red-300">
                    Auto boot error: {autoBootError}
                  </span>
                )}
              </div>

              {appState === "detect_PBU" && (
                <DetectPBU
                  v={v}
                  searchFilePath={readDirectory}
                />
              )}

              {appState === "select_PBU" && <SelectPBU />}

              {appState === "home_position_setup" && (
                <HomePositionCheck
                  ABBHOMEImage={ABBHOMEImage}
                  RobotPowerONOutside={RobotPowerONOutside}
                  v={v}
                  verifyHomePosition={getRobotJointTarget}
                  loading={loading}
                  error={error}
                  jointTarget={jointTarget}
                  appState={appState}
                />
              )}

              {appState === "home_verified" && (
                <HomeVerified
                  pushRobotIntoPBUImage={pushRobotIntoPBUImage}
                  FlexPendantImage={FlexPendantImage}
                  RobotPowerOFFOutside={RobotPowerOFFOutside}
                  RobotPowerONInside={RobotPowerONInside}
                  v={v}
                  onNext={handleAdvanceToFourWall}
                />
              )}
            </div>
          </div>
        </div>
      )}

      {appState === "four_wall_flow" && <FourWallFlow />}
    </>
  );
}
