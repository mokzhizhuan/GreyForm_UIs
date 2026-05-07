// scripts/start-all.js
const { spawn } = require("child_process");
const path = require("path");

const ROOT_DIR = path.resolve(__dirname, "..");

const FRONTEND_DIR =
  process.env.FRONTEND_DIR ||
  path.join(ROOT_DIR, "greyformui-usb-completionmessage");

const LAUNCHER =
  process.env.LAUNCHER_PATH ||
  path.join(ROOT_DIR, "backend", "launcher.py");

const PYTHON_CMD =
  process.env.PYTHON_CMD ||
  (process.platform === "win32" ? "python" : "python3");

const NPM_CMD = process.platform === "win32" ? "npm.cmd" : "npm";

const API_ENV = {
  ...process.env,
  HOST: process.env.HOST || "0.0.0.0",
  PORT: process.env.PORT || "8000",
  APP: process.env.APP || "backend.main:app",
  WORKERS: process.env.WORKERS || "1",
  RELOAD: "0",
  UVICORN_EXTRA: process.env.UVICORN_EXTRA || "",
  PYTHONPATH:
    ROOT_DIR +
    (process.env.PYTHONPATH ? path.delimiter + process.env.PYTHONPATH : ""),
};

let apiProc = null;
let uiProc = null;
let shuttingDown = false;

function run(cmd, args, name, opts = {}) {
  console.log(`[manager] ${name} command:`, cmd, args.join(" "));
  console.log(`[manager] ${name} cwd:`, opts.cwd || process.cwd());

  const child = spawn(cmd, args, {
    stdio: "inherit",
    shell: false,
    env: opts.env || process.env,
    cwd: opts.cwd || process.cwd(),
    windowsHide: false,
  });

  child.on("close", (code) => {
    console.log(`[${name}] exited with code ${code}`);

    if (name === "UI" && !shuttingDown) {
      console.log("[manager] UI stopped; shutting down API...");
      shutdown().finally(() => process.exit(code ?? 0));
    }
  });

  child.on("error", (err) => {
    console.error(`[${name}] failed to start:`, err);

    if (!shuttingDown) {
      shutdown().finally(() => process.exit(1));
    }
  });

  return child;
}

function startAll() {
  console.log("[manager] starting API via launcher...");
  apiProc = run(PYTHON_CMD, [LAUNCHER, "start"], "API", {
    env: API_ENV,
    cwd: ROOT_DIR,
  });

  console.log("[manager] starting UI (npm start)...");
  if (process.platform === "win32") {
    uiProc = run("cmd.exe", ["/d", "/s", "/c", "npm run start"], "UI", {
      cwd: FRONTEND_DIR,
    });
  } else {
    uiProc = run("npm", ["run", "start"], "UI", {
      cwd: FRONTEND_DIR,
    });
}
}

async function stopAPI() {
  return new Promise((resolve) => {
    console.log("[manager] stopping API via launcher...");

    const stopper = spawn(PYTHON_CMD, [LAUNCHER, "stop"], {
      stdio: "inherit",
      shell: false,
      env: API_ENV,
      cwd: ROOT_DIR,
    });

    stopper.on("close", () => resolve());
    stopper.on("error", () => resolve());
  });
}

async function shutdown() {
  if (shuttingDown) return;
  shuttingDown = true;

  await stopAPI();

  try {
    if (uiProc && !uiProc.killed) {
      uiProc.kill("SIGINT");
      setTimeout(() => {
        try {
          uiProc.kill();
        } catch {}
      }, 500);
    }
  } catch {}

  try {
    if (apiProc && !apiProc.killed) {
      apiProc.kill("SIGINT");
      setTimeout(() => {
        try {
          apiProc.kill();
        } catch {}
      }, 500);
    }
  } catch {}
}

process.on("SIGINT", () => {
  console.log("\n[manager] SIGINT");
  shutdown().finally(() => process.exit(0));
});

process.on("SIGTERM", () => {
  console.log("\n[manager] SIGTERM");
  shutdown().finally(() => process.exit(0));
});

startAll();