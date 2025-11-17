import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import SelectPBU from "./SelectPBU";
import { getRobotJointTarget } from "../services/robotApi";
import HomePositionCheck from "./HomePositionCheck";
import HomeVerified from "./HomeVerified";
import FourWallFlow from "./FourWallFlow";

// Import images
import ABBHOMEImage from '../assets/ABB Robot placeholder image.jpg';
import FlexPendantImage from '../assets/ABB_Robot_FlexPendant.jpg';
import pushRobotIntoPBUImage from '../assets/PushIntoPBU.jpg';
import RobotPowerONOutside from '../assets/ABB_Robot_Power_ON_outside.jpg';
import RobotPowerOFFOutside from '../assets/ABB_Robot_Power_OFF_outside.jpg';
import RobotPowerONInside from '../assets/ABB_Robot_Power_ON_inside.jpg';


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
  | "select_PBU" // Alternative UI where there is option to choose the PBU
  | "success"
  | "error"
  | "shutdown"
  | "checked_ok"
  | "invalid_model"
  | "home_position_setup"
  | "home_verified"
  | "four_wall_flow";

const views = {
  select_PBU: { title: "File Selection Menu", variant: "primary", primaryText: "Start", showSpinner: false },
  success:  { title: "USB drive detected",    variant: "success", primaryText: "Check selection", showSpinner: false },
  error:    { title: "Error reading USB drive", variant: "error",   primaryText: "Try Again", showSpinner: false },
  shutdown: { title: "Please power off the machine", variant: "neutral", primaryText: "", showSpinner: false },
  home_position_setup: { title: "Home position setup", variant: "success", primaryText: "Verify HOME position", showSpinner: false },
  home_verified: { title: "Move Robot into PBU", variant: "success", primaryText: "Next Step", showSpinner: false },
  four_wall_flow: { title: "Marking of PBU"},
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
      return await axios.post(url, data, { timeout: 8000, ...(config || {}) });
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
  const [appState, setAppState] = useState<CurrentState>("home_position_setup");
  const v = views[appState];
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jointTarget, setJointTarget] = useState<any | null>(null);

  const API = useMemo(() => {
    const base = import.meta.env.VITE_API_URL ?? "http://localhost:800";
    return base.replace(/\/+$/, "");
  }, []);

  const ran = useRef(false);

  // Auto start roscore + build + listener once (when UI opens)
  useEffect(() => {
    if (ran.current) return;
    ran.current = true;

    (async () => {
      try {
        await postWithRetries(`${API}/roscore/start`);
        console.log("[auto] roscore started");
      } catch (e: any) {
        console.warn("[auto] roscore error:", e?.response?.data || e?.message);
      }

      try {
        await postWithRetries(`${API}/build/start`);
        console.log("[auto] build started");
      } catch (e: any) {
        console.warn("[auto] build error:", e?.response?.data || e?.message);
      }

      try {
        await postWithRetries(`${API}/ros/listener/start`, null, {
          params: { restart: true },
        });
        console.log("[auto] listener started");
      } catch (e: any) {
        console.warn("[auto] listener error:", e?.response?.data || e?.message);
      }
    })();
  }, [API]);

  const verifyHomePosition = async () => {
    setError(null)
    setJointTarget(null);
    setLoading(true)
      try {
        const creds = { host: "192.168.1.200", username: "Default User", password: "robotics" };
        const jointTarget = await getRobotJointTarget(creds);
        console.log("Robot joint target:", jointTarget);
        setJointTarget(jointTarget);
        // Add logic to verify joint target
        setAppState("home_verified");
      } catch (error) {
        console.error("Failed to get robot joint target:", error);
        // Handle error, maybe set an error state
        setError("Failed to get robot joint target");
      } finally {
        setLoading(false);
      }
  };

  const handleAdvanceToFourWall = () => {
    setAppState("four_wall_flow");
  };

  // UI (balanced braces/parens)
  return (
    <>
      {appState !== "four_wall_flow" && (
        <div className="hero min-h-screen relative bg-cover bg-center" style={{ backgroundImage: `url("${bgDataUri}")` }}>
          <div className={`hero-overlay bg-neutral/50`} />
          <div className="hero-content text-neutral-content text-center relative">
            <div className="max-w-max space-y-5">
              <h1 className="text-4xl md:text-5xl font-bold">{v.title}</h1>

              {appState === "detect_PBU" && (
                <DetectPBU />
              )}

              {appState === "select_PBU" && (
                <SelectPBU />
              )}

              {appState === "home_position_setup" && (
                <>
                  <HomePositionCheck
                    ABBHOMEImage={ABBHOMEImage}
                    RobotPowerONOutside={RobotPowerONOutside}
                    v={v}
                    verifyHomePosition={verifyHomePosition}
                    loading={loading}
                    error={error}
                    jointTarget={jointTarget}
                    appState={appState}
                  />
                </>
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
      {appState === "four_wall_flow" && (
        <FourWallFlow />
      )}
    </>
  );
}