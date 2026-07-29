// src/Components/flowShared.ts
// Shared types/helpers used by both FourWallFlow and SixWallFlow — they
// follow the same "poll marking status, drive a step UI" pattern, just
// with a different wall sequence/step count. Previously this logic was
// copy-pasted in both files; consolidated here so a fix only needs to
// happen once.

import { useRef, useState } from "react";
import { API_BASE_URL } from "./config";

// --------------------------------------------------------
// PBU-specific images (stage/wall diagrams, placement photos) live on
// the Linux PC alongside the Excel file, not as bundled frontend
// assets — fetch them through the backend's /get_image endpoint.
// --------------------------------------------------------
export function buildPbuImageUrl(folder: string, filename: string): string {
  const params = new URLSearchParams({ folder, filename });
  return `${API_BASE_URL}/get_image?${params.toString()}`;
}

// --------------------------------------------------------
// TYPES
// --------------------------------------------------------
export interface WallRow {
  [key: string]: any;
}

export interface MarkingStatusResponse {
  running: boolean;
  paused: boolean;
  startedWall: number | null;
  doneWall: number | null;
  phase: number | null;
  hasError: boolean;
  errorSummary?: string | null;
  lastFailedWall?: number | null;
  homeCheckPending?: boolean;
  homeCheckWall?: number | null;
  homeCheckOutput?: string | null;
}

// --------------------------------------------------------
// Map excel filenames (e.g. "..._wall_2.xlsx") to their wall id,
// so each wall step knows which Excel file belongs to it.
// --------------------------------------------------------
export function buildExcelMap(files: string[]): Record<string, string> {
  const map: Record<string, string> = {};
  for (const f of files) {
    const m = f.match(/_wall_(\d+)\.xlsx$/);
    if (m) map[`wall_${m[1]}`] = f;
  }
  return map;
}

// --------------------------------------------------------
// Parse the raw text output of homeposcheck.py into
// [{ axis: "J1", current, target }, ...] rows for the table.
//
// Note: this is SixWallFlow's version of the parser (it derives the
// axis index from the "j<N>" key itself via regex), which is more
// robust than FourWallFlow's old version (which assumed object key
// order matched axis order). Both flows now use this one.
// --------------------------------------------------------
export function parseHomeCheck(output: string) {
  const lines = (output || "").split(/\r?\n/).map((l) => l.trim());
  const rax = lines.find((l) => l.includes("rax_1"));
  const tgt = lines.find((l) => l.includes("j0"));

  let current: Record<string, number> = {};
  let target: Record<string, number> = {};

  try {
    if (rax) current = JSON.parse(rax.replace(/'/g, '"'));
    if (tgt) target = JSON.parse(tgt.replace(/'/g, '"'));
  } catch {
    // ignore parse errors — table just stays empty until valid output arrives
  }

  return Object.entries(target).map(([k, v], i) => {
    const m = k.match(/^j(\d+)$/i);
    const idx = m ? parseInt(m[1], 10) : i;
    return {
      axis: `J${idx + 1}`,
      target: v,
      current: current[`rax_${idx + 1}`],
    };
  });
}

// --------------------------------------------------------
// Prevents overlapping/double-clicked actions (Start/Pause/Retry/etc.)
// while an API call for that action is still in flight.
// --------------------------------------------------------
export function useActionLock() {
  const actionLockRef = useRef(false);
  const [actionBusy, setActionBusy] = useState(false);

  const withActionLock = async (fn: () => Promise<void>) => {
    if (actionLockRef.current) return;
    actionLockRef.current = true;
    setActionBusy(true);
    try {
      await fn();
    } finally {
      actionLockRef.current = false;
      setActionBusy(false);
    }
  };

  return { actionBusy, withActionLock };
}
