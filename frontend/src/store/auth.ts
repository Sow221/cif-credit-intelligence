import { create } from "zustand";
import type { AuthUser } from "@/services/auth";
import { loadStoredSession } from "@/services/auth";

export type AuthStatus = "idle" | "loading" | "authenticated" | "unauthenticated";

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  status: AuthStatus;
  error: string | null;
  setAuthenticated: (user: AuthUser, token: string) => void;
  setLoading: () => void;
  setError: (message: string) => void;
  logout: () => void;
}

function bootstrap(): { user: AuthUser | null; token: string | null } {
  if (typeof window === "undefined") return { user: null, token: null };
  return { user: loadStoredSession()?.user ?? null, token: null };
}

export const useAuthStore = create<AuthState>((set) => {
  const { user, token } = bootstrap();
  return {
    user,
    token,
    status: user ? "authenticated" : "unauthenticated",
    error: null,
    setAuthenticated: (nextUser, nextToken) =>
      set({ user: nextUser, token: nextToken, status: "authenticated", error: null }),
    setLoading: () => set({ status: "loading", error: null }),
    setError: (message) => set({ status: "unauthenticated", error: message }),
    logout: () => set({ user: null, token: null, status: "unauthenticated", error: null }),
  };
});
