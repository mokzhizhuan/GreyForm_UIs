// src/config.ts
const rawBaseUrl =
  import.meta.env.VITE_API_URL ?? "http://localhost:800"; // change 8000 to 800 if your API is on 800

// Strip any trailing slashes so you don't end up with `//` in URLs
export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, "");