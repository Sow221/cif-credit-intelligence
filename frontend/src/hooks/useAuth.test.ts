import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useAuth } from "./useAuth";
import { useAuthStore } from "@/store/auth";

vi.mock("@/services/api", () => {
  const mock = { get: vi.fn(), post: vi.fn(), patch: vi.fn() };
  return { api: mock };
});

vi.mock("@/services/auth", () => ({
  login: vi.fn(),
  logout: vi.fn(),
}));

const mockedAuthService = vi.mocked(await import("@/services/auth"));

function resetAuthStore() {
  useAuthStore.setState({
    user: null,
    token: null,
    status: "unauthenticated",
    error: null,
  });
}

describe("useAuth", () => {
  beforeEach(() => {
    resetAuthStore();
    vi.clearAllMocks();
  });

  it("returns user and status from the store", () => {
    useAuthStore.setState({
      user: {
        user_id: "u1",
        username: "admin",
        full_name: "Admin User",
        role: "ADMIN",
        institution_id: "i1",
      },
      status: "authenticated",
    });
    const { result } = renderHook(() => useAuth());
    expect(result.current.user?.username).toBe("admin");
    expect(result.current.status).toBe("authenticated");
    expect(result.current.error).toBeNull();
  });

  it("signIn calls authService.login and sets authenticated", async () => {
    const user = {
      user_id: "u1",
      username: "admin",
      full_name: "Admin",
      role: "ADMIN",
      institution_id: "i1",
    };
    mockedAuthService.login.mockResolvedValue(user);
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.signIn("admin", "pass");
    });

    expect(mockedAuthService.login).toHaveBeenCalledWith({ username: "admin", password: "pass" });
    expect(useAuthStore.getState().status).toBe("authenticated");
    expect(useAuthStore.getState().user).toEqual(user);
  });

  it("signIn sets error on failure", async () => {
    mockedAuthService.login.mockRejectedValue(new Error("Invalid credentials"));
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await expect(result.current.signIn("admin", "wrong")).rejects.toThrow("Invalid credentials");
    });

    expect(useAuthStore.getState().status).toBe("unauthenticated");
    expect(useAuthStore.getState().error).toBe("Invalid credentials");
  });

  it("signOut calls authService.logout and clears store", () => {
    useAuthStore.setState({
      user: {
        user_id: "u1",
        username: "admin",
        full_name: "Admin",
        role: "ADMIN",
        institution_id: "i1",
      },
      status: "authenticated",
    });
    const { result } = renderHook(() => useAuth());

    act(() => {
      result.current.signOut();
    });

    expect(mockedAuthService.logout).toHaveBeenCalled();
    expect(useAuthStore.getState().status).toBe("unauthenticated");
    expect(useAuthStore.getState().user).toBeNull();
  });
});
