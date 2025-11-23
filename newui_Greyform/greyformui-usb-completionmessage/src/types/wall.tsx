interface WallRow {
  // Use your real column names here if you know them
  [key: string]: string | number | boolean | null;
}

interface WallInfo {
  wall: string;      // "1", "2", "3", ...
  count: number;
  rows: WallRow[];   // all Excel rows for that wall
}

interface ExecuteWallDataResponse {
  ok: boolean;
  queued?: boolean;
  error?: string;
}