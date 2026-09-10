import { api, clearToken, setToken } from "./api";
import { useAuthStore } from "@/store/auth";

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AuthUser {
  user_id: string;
  username: string;
  full_name: string;
  role: string;
  institution_id: string;
  email?: string | null;
}

export interface Session {
  user: AuthUser;
}

const SESSION_KEY = "cif_session";

export function loadStoredSession(): Session | null {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

function storeSession(session: Session): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearStoredSession(): void {
  localStorage.removeItem(SESSION_KEY);
}

export async function login(payload: LoginPayload): Promise<AuthUser> {
  const data = await api.post<LoginResponse>("/auth/login", payload);
  const sessionRaw = await api.get<Session>("/auth/me");
  setToken(data.access_token);
  storeSession(sessionRaw);
  return sessionRaw.user;
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const session = await api.get<Session>("/auth/me");
  storeSession(session);
  return session.user;
}

export function logout(): void {
  clearToken();
  clearStoredSession();
  useAuthStore.getState().logout();
}
