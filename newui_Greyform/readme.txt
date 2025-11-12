Before your url start , npm run dev , this will run a nodejs script /scripts/start-all.js to start a uvicorn.
Take note important method to look out:
  const API = useMemo(() => {
    const base = import.meta.env.VITE_API_URL ?? "http://localhost:800";
    return base.replace(/\/+$/, "");
  }, []);
this method is to access the port 800 fastapi python. I cant give the same port as react ui as it may collide with the main url itself. 
Mainly , this will be my backend port for ros.

react, tsx js. was added for automatically run the function for ros:
  useEffect(() => {
    if (ran.current) return;
    ran.current = true;

    (async () => {
	try {
        await postWithRetries(`${API}/roscore/start`, null, { params: { restart: true } });
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
        await postWithRetries(`${API}/ros/listener/start`, null, { params: { restart: true } });
        console.log("[auto] listener started");
      } catch (e: any) {
        console.warn("[auto] listener error:", e?.response?.data || e?.message);
      }
    })})

After that I may leave the rest of the API below.
Note : these api are for the workflow . or you can do a full restart from the above react js , to prevent any conflict(only for ${API}/build/stop , ${API}/roscore/stop)
`${API}/build/stop , ${API}/roscore/stop , ${API}/ros/file_execute_data , ${API}/ros/file_execute_data ,${API}/ros/execute_wall_data


