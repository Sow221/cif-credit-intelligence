import { beforeEach, describe, expect, it, vi } from "vitest";
import { render } from "@testing-library/react";
import { Providers } from "./providers";
import { useAuthStore } from "@/store/auth";
import { adminUser } from "@/test/helpers";

const { loadStoredSessionMock } = vi.hoisted(() => ({
  loadStoredSessionMock: vi.fn(),
}));
vi.mock("@/services/auth", () => ({ loadStoredSession: loadStoredSessionMock }));

describe("Providers", () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, token: null, status: "unauthenticated", error: null });
    loadStoredSessionMock.mockReset();
  });

  it("restores an authenticated session when one is stored", () => {
    loadStoredSessionMock.mockReturnValue({ user: adminUser });
    render(
      <Providers>
        <div>child-content</div>
      </Providers>,
    );
    const state = useAuthStore.getState();
    expect(state.status).toBe("authenticated");
    expect(state.user?.full_name).toBe("Admin Diallo");
  });

  it("keeps the store unauthenticated when no session is stored", () => {
    loadStoredSessionMock.mockReturnValue(null);
    render(
      <Providers>
        <div>child-content</div>
      </Providers>,
    );
    expect(useAuthStore.getState().status).toBe("unauthenticated");
  });
});
