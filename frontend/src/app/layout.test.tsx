import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import i18n from "@/locales";
import { AppLayout } from "./layout";
import { resetStores, seedAuth, adminUser } from "@/test/helpers";
import { useToastStore } from "@/store/toast";

const { apiMock, connectMock, disconnectMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
  connectMock: vi.fn(),
  disconnectMock: vi.fn(),
}));
vi.mock("@/services/api", () => ({ api: apiMock, setToken: vi.fn(), clearToken: vi.fn() }));
vi.mock("@/services/websocket", () => ({
  notificationSocket: { connect: connectMock, disconnect: disconnectMock },
}));

function renderLayout() {
  return render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<div>page-content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("AppLayout", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    seedAuth(adminUser);
    apiMock.get.mockReset();
    apiMock.get.mockResolvedValue([]);
  });

  it("renders the sidebar brand, header, and outlet content", () => {
    renderLayout();
    expect(screen.getAllByText("Adaptive Credit").length).toBeGreaterThan(0);
    expect(screen.getByRole("navigation", { name: "Navigation principale" })).toBeInTheDocument();
    expect(screen.getByText("Admin Diallo")).toBeInTheDocument();
    expect(screen.getByText("page-content")).toBeInTheDocument();
  });

  it("opens the command palette with Ctrl+K and closes it with Escape", async () => {
    const user = userEvent.setup();
    renderLayout();
    await user.keyboard("{Control>}k{/Control}");
    expect(screen.getByRole("dialog", { name: "Rechercher" })).toBeInTheDocument();
    await user.keyboard("{Control>}k{/Control}");
    expect(screen.queryByRole("dialog", { name: "Rechercher" })).not.toBeInTheDocument();
    await user.keyboard("{Control>}k{/Control}");
    expect(screen.getByRole("dialog", { name: "Rechercher" })).toBeInTheDocument();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog", { name: "Rechercher" })).not.toBeInTheDocument();
  });

  it("renders and dismisses toasts from the toast store", async () => {
    const user = userEvent.setup();
    useToastStore.getState().addToast("success", "Demande créée avec succès");
    renderLayout();
    expect(screen.getByText("Demande créée avec succès")).toBeInTheDocument();
    await user.click(screen.getByText("Demande créée avec succès"));
    expect(screen.queryByText("Demande créée avec succès")).not.toBeInTheDocument();
  });
});
