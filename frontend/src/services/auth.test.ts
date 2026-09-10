import { beforeEach, describe, expect, it, vi } from "vitest";
import type { AuthUser } from "./auth";
import { clearStoredSession, fetchCurrentUser, loadStoredSession, login, logout } from "./auth";
import { useAuthStore } from "@/store/auth";

vi.mock("@/services/api", () => {
  const post = vi.fn();
  const get = vi.fn();
  return {
    api: { get, post },
    getToken: vi.fn(() => localStorage.getItem("cif_access_token")),
    setToken: vi.fn((token: string) => localStorage.setItem("cif_access_token", token)),
    clearToken: vi.fn(() => localStorage.removeItem("cif_access_token")),
  };
});

const mockedApi = vi.mocked((await import("@/services/api")).api);

const user: AuthUser = {
  user_id: "u1",
  username: "awa",
  full_name: "Awa Diallo",
  role: "ADMIN",
  institution_id: "i1",
  email: "awa@example.com",
};

describe("session storage", () => {
  beforeEach(() => localStorage.clear());

  it("returns null without a stored session", () => {
    expect(loadStoredSession()).toBeNull();
  });

  it("round-trips a stored session", async () => {
    loginMockSuccess();
    await login({ username: "awa", password: "pw" });
    const session = loadStoredSession();
    expect(session?.user.username).toBe("awa");
  });

  it("returns null on corrupted JSON", () => {
    localStorage.setItem("cif_session", "{not json");
    expect(loadStoredSession()).toBeNull();
  });

  it("clears the stored session", () => {
    localStorage.setItem("cif_session", JSON.stringify({ user }));
    clearStoredSession();
    expect(loadStoredSession()).toBeNull();
  });
});

describe("login / fetchCurrentUser", () => {
  beforeEach(() => {
    localStorage.clear();
    mockedApi.post.mockReset();
    mockedApi.get.mockReset();
    useAuthStore.setState({ user: null, token: null, status: "unauthenticated" });
  });

  it("stores token and session and returns the user", async () => {
    loginMockSuccess();
    const returned = await login({ username: "awa", password: "pw" });
    expect(returned.username).toBe("awa");
    expect(mockedApi.post).toHaveBeenCalledWith("/auth/login", {
      username: "awa",
      password: "pw",
    });
    expect(mockedApi.get).toHaveBeenCalledWith("/auth/me");
    expect(localStorage.getItem("cif_access_token")).toBe("token-1");
  });

  it("fetchCurrentUser stores the session", async () => {
    mockedApi.get.mockResolvedValue({ user });
    const returned = await fetchCurrentUser();
    expect(returned.user_id).toBe("u1");
    expect(loadStoredSession()?.user).toEqual(user);
  });
});

describe("logout", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({ user, status: "authenticated" });
    loginMockSuccess();
  });

  it("clears credentials and store state", async () => {
    await login({ username: "awa", password: "pw" });
    logout();
    expect(localStorage.getItem("cif_access_token")).toBeNull();
    expect(loadStoredSession()).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().status).toBe("unauthenticated");
  });
});

function loginMockSuccess(): void {
  mockedApi.post.mockResolvedValue({ access_token: "token-1", token_type: "bearer" });
  mockedApi.get.mockResolvedValue({ user });
}