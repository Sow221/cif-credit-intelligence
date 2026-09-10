import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import i18n from "@/locales";
import LoginPage from "./Login";
import { resetStores, adminUser } from "@/test/helpers";

const { apiMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
vi.mock("@/services/api", () => ({
  api: apiMock,
  setToken: vi.fn(),
  clearToken: vi.fn(),
}));

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<div>dashboard-page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("LoginPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    apiMock.post.mockReset();
    apiMock.get.mockReset();
  });

  it("renders the branding and form fields", () => {
    renderPage();
    expect(screen.getByText("Adaptive Credit")).toBeInTheDocument();
    expect(screen.getByText("Décision de crédit intelligente")).toBeInTheDocument();
    expect(screen.getByLabelText("Identifiant")).toBeInTheDocument();
    expect(screen.getByLabelText("Mot de passe")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Se connecter" })).toBeInTheDocument();
  });

  it("shows required-field errors when submitting empty credentials", async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole("button", { name: "Se connecter" }));
    expect(screen.getAllByText("Champ obligatoire").length).toBeGreaterThanOrEqual(2);
  });

  it("submits the credentials and navigates to the dashboard", async () => {
    const user = userEvent.setup();
    apiMock.post.mockResolvedValue({ access_token: "token", token_type: "bearer" });
    apiMock.get.mockResolvedValue({ user: adminUser });
    renderPage();
    await user.type(screen.getByLabelText("Identifiant"), "admin");
    await user.type(screen.getByLabelText("Mot de passe"), "secret");
    await user.click(screen.getByRole("button", { name: "Se connecter" }));
    await waitFor(() =>
      expect(apiMock.post).toHaveBeenCalledWith("/auth/login", {
        username: "admin",
        password: "secret",
      }),
    );
    expect(apiMock.get).toHaveBeenCalledWith("/auth/me");
    expect(await screen.findByText("dashboard-page")).toBeInTheDocument();
  });

  it("shows the server error returned by the API", async () => {
    const user = userEvent.setup();
    apiMock.post.mockRejectedValue(new Error("Identifiants invalides"));
    renderPage();
    await user.type(screen.getByLabelText("Identifiant"), "admin");
    await user.type(screen.getByLabelText("Mot de passe"), "wrong");
    await user.click(screen.getByRole("button", { name: "Se connecter" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Identifiants invalides");
  });
});
