import { api, clearToken, setToken } from "./api";
import { clearStoredSession, loadStoredSession, storeSession } from "./session";
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

export { loadStoredSession, clearStoredSession };

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
