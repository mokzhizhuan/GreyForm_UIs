export type RobotCreds = { host: string; username?: string; password?: string };

function normalizeHost(h?: string) {
  // Treat undefined / null / empty / whitespace-only as the default host
  const raw = h && h.trim() ? h.trim() : "192.168.1.200";

  if (/^https?:\/\//.test(raw)) {
    // remove trailing slashes for http(s) prefixed values
    return raw.replace(/\/+$/, "");
  }
  // add https:// for hosts without protocol and remove trailing slashes
  return `https://${raw.replace(/\/+$/, "")}`;
}

function basicAuthHeader(username = "Default User", password = "robotics") {
  return `Basic ${btoa(`${username}:${password}`)}`;
}

export async function getRobotJointTarget(
  creds: RobotCreds,
  path = "/rw/motionsystem/mechunits/ROB_1/jointtarget"
) {
  const host = normalizeHost(creds.host);
  const url = `${host}${path}`;
  const headers: Record<string, string> = {
    Accept: "application/hal+json;v=2.0",
    "Content-Type": "application/x-www-form-urlencoded;v=2.0",
    Authorization: basicAuthHeader(creds.username, creds.password),
  };

  const resp = await fetch(url, { method: "GET", headers });
  if (!resp.ok) {
    const t = await resp.text().catch(() => "");
    throw new Error(`Status ${resp.status} ${resp.statusText} ${t ? "- " + t : ""}`);
  }
  const text = await resp.text();
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}