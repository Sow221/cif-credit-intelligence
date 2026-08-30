const TOKEN_KEY = "cif_access_token";
const AGENT_KEY = "cif_agent_id";
const ROLE_KEY = "cif_role";

export type Role = "agent" | "supervisor";

export interface Session {
  token: string;
  agentId: string;
  role: Role;
}

/** Decode le role depuis le claim subject du JWT ({agent_id}@{role}). */
export function decodeRole(token: string): Role | null {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = JSON.parse(atob(normalized)) as { sub?: string };
    const sub = json.sub ?? "";
    const role = sub.split("@")[1] ?? "";
    return role === "supervisor" ? "supervisor" : "agent";
  } catch {
    return null;
  }
}

export function saveSession(token: string, agentId: string, role: Role): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(AGENT_KEY, agentId);
  localStorage.setItem(ROLE_KEY, role);
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(AGENT_KEY);
  localStorage.removeItem(ROLE_KEY);
}

export function getSession(): Session | null {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return null;
  const agentId = localStorage.getItem(AGENT_KEY) ?? "";
  const rawRole = localStorage.getItem(ROLE_KEY);
  const role: Role = rawRole === "supervisor" ? "supervisor" : "agent";
  return { token, agentId, role };
}
