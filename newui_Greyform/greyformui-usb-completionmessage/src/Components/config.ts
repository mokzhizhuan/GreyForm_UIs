// src/config.ts
const rawBaseUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Strip any trailing slashes so you don't end up with `//` in URLs
export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, "");
