import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import { AppRouter } from "./router";
import { useAuthStore } from "@/store/auth";
import { useDataStore } from "@/store/data";
import { resetStores, seedAuth, makeApplication, adminUser } from "@/test/helpers";

const { apiMock, connectMock, disconnectMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
  connectMock: vi.fn(),
  disconnectMock: vi.fn(),
}));
vi.mock("@/services/api", () => ({ api: apiMock, setToken: vi.fn(), clearToken: vi.fn() }));
vi.mock("@/services/websocket", () => ({
  notificationSocket: { connect: connectMock, disconnect: disconnectMock },
}));

function renderRouter(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AppRouter />
    </MemoryRouter>,
  );
}

function seedDashboardData() {
  useDataStore.setState({
    applications: [],
    applicationsStatus: "success",
    reviews: [],
    reviewsStatus: "success",
  });
  apiMock.get.mockResolvedValue([]);
}

describe("AppRouter", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    apiMock.get.mockReset();
    apiMock.get.mockResolvedValue([]);
  });

  it("redirects unauthenticated users from a protected page to the login view", async () => {
    renderRouter("/dashboard");
    expect(await screen.findByRole("button", { name: "Se connecter" })).toBeInTheDocument();
  });

  it("shows a loading skeleton while the auth status is pending", () => {
    useAuthStore.setState({ status: "loading", user: null });
    renderRouter("/dashboard");
    expect(screen.getByRole("status", { name: "Chargement..." })).toBeInTheDocument();
  });

  it("redirects authenticated users away from the login page", async () => {
    seedAuth(adminUser);
    seedDashboardData();
    renderRouter("/login");
    expect(await screen.findByText(/Bonjour, Admin/)).toBeInTheDocument();
  });

  it("redirects the root path to the dashboard", async () => {
    seedAuth(adminUser);
    seedDashboardData();
    renderRouter("/");
    expect(await screen.findByText(/Bonjour, Admin/)).toBeInTheDocument();
  });

  it("redirects unknown routes to the dashboard", async () => {
    seedAuth(adminUser);
    seedDashboardData();
    renderRouter("/does-not-exist");
    expect(await screen.findByText(/Bonjour, Admin/)).toBeInTheDocument();
  });

  it("renders a protected page inside the layout for an authenticated user", async () => {
    seedAuth(adminUser);
    useDataStore.setState({
      applications: [makeApplication({ application_id: "app-1" })],
      applicationsStatus: "success",
    });
    renderRouter("/applications");
    const headings = await screen.findAllByRole("heading", { name: "Demandes" });
    expect(headings.length).toBeGreaterThan(0);
    expect(screen.getByText("APP-1")).toBeInTheDocument();
  });
});
