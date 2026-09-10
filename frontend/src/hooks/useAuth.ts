import { useCallback } from "react";
import { useAuthStore } from "@/store/auth";
import * as authService from "@/services/auth";

export function useAuth() {
  const user = useAuthStore((state) => state.user);
  const status = useAuthStore((state) => state.status);
  const error = useAuthStore((state) => state.error);
  const setLoading = useAuthStore((state) => state.setLoading);
  const setError = useAuthStore((state) => state.setError);
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated);
  const logoutLocal = useAuthStore((state) => state.logout);

  const signIn = useCallback(
    async (username: string, password: string) => {
      setLoading();
      try {
        const user = await authService.login({ username, password });
        setAuthenticated(user, "");
        return user;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Authentication failed";
        setError(message);
        throw err;
      }
    },
    [setLoading, setError, setAuthenticated],
  );

  const signOut = useCallback(() => {
    authService.logout();
    logoutLocal();
  }, [logoutLocal]);

  return { user, status, error, signIn, signOut };
}
