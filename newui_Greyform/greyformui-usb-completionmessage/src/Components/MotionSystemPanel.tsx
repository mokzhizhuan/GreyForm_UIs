import { useEffect, useState } from "react";
import axios from "axios"; 

export default function MotionSystemPanel() {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/motionsystem")
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch(e => setErr(e.message));
  }, []);

  if (err) return <div>Failed: {err}</div>;
  if (!data) return <div>Loading…</div>;
  return <pre style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(data, null, 2)}</pre>;
}

export const getMechs = async () => 
  (await axios.get("/api/rws/mechunits")).data; 
export const getRobTarget = async (mech="ROB_1") => 
  (await axios.get("/api/rws/robtarget", { params:{ mech } })).data; 
export const getJointTarget = async (mech="ROB_1") => 
  (await axios.get("/api/rws/jointtarget", { params:{ mech } })).data; 