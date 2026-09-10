import { beforeEach, describe, expect, it } from "vitest";
import { useAuthStore } from "./auth";
import type { AuthUser } from "@/services/auth";

const user: AuthUser = {
  user_id: "u1",
  username: "awa",
  full_name: "Awa Diallo",
  role: "ADMIN",
  institution_id: "i1",
};

describe("useAuthStore", () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
      status: "unauthenticated",
      error: null,
    });
  });

  it("starts unauthenticated", () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.status).toBe("unauthenticated");
  });

  it("setAuthenticated stores user and token", () => {
    useAuthStore.getState().setAuthenticated(user, "tok");
    const state = useAuthStore.getState();
    expect(state.user?.username).toBe("awa");
    expect(state.token).toBe("tok");
    expect(state.status).toBe("authenticated");
    expect(state.error).toBeNull();
  });

  it("setLoading transitions and clears error", () => {
    useAuthStore.getState().setError("previous");
    useAuthStore.getState().setLoading();
    const state = useAuthStore.getState();
    expect(state.status).toBe("loading");
    expect(state.error).toBeNull();
  });

  it("setError marks unauthenticated with a message", () => {
    useAuthStore.getState().setError("invalid credentials");
    const state = useAuthStore.getState();
    expect(state.status).toBe("unauthenticated");
    expect(state.error).toBe("invalid credentials");
  });

  it("logout resets state", () => {
    useAuthStore.getState().setAuthenticated(user, "tok");
    useAuthStore.getState().logout();
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.status).toBe("unauthenticated");
    expect(state.error).toBeNull();
  });
});
