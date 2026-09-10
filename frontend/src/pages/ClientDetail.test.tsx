import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import i18n from "@/locales";
import ClientDetailPage from "./ClientDetail";
import {
  resetStores,
  makeClientDetail,
  makeApplication,
  seedAuth,
  adminUser,
} from "@/test/helpers";
import { useDataStore } from "@/store/data";

const { apiMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
vi.mock("@/services/api", () => ({ api: apiMock }));

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/clients/c1"]}>
      <Routes>
        <Route path="/clients/:id" element={<ClientDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ClientDetailPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    seedAuth(adminUser);
    useDataStore.setState({
      applications: [],
      applicationsStatus: "success",
    });
    apiMock.get.mockReset();
    apiMock.get.mockImplementation((path: string) =>
      path === "/clients/c1" ? Promise.resolve(makeClientDetail()) : Promise.resolve([]),
    );
  });

  it("renders the client identity and status", async () => {
    renderPage();
    expect(await screen.findByText("Awa Diallo")).toBeInTheDocument();
    expect(screen.getByText("Actif")).toBeInTheDocument();
  });

  it("renders the identity and savings details", async () => {
    renderPage();
    expect(await screen.findByText("Identité")).toBeInTheDocument();
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("awa.diallo@example.com")).toBeInTheDocument();
    expect(screen.getByText("Téléphone")).toBeInTheDocument();
    expect(screen.getByText("Épargne")).toBeInTheDocument();
    expect(screen.getByText("Solde")).toBeInTheDocument();
    expect(screen.getByText("Solde moyen")).toBeInTheDocument();
  });

  it("renders the loans table with loan amounts", async () => {
    renderPage();
    expect(await screen.findByText("Prêts")).toBeInTheDocument();
    expect(screen.getByText(/100\s?000/)).toBeInTheDocument();
    expect(screen.getByText("ACTIVE")).toBeInTheDocument();
  });

  it("links applications of this client in the decisions card", async () => {
    useDataStore.setState({
      applications: [makeApplication({ application_id: "app-9" })],
      applicationsStatus: "success",
    });
    renderPage();
    expect(await screen.findByText("Décisions")).toBeInTheDocument();
    expect(screen.getByText(/APP-9 ·/)).toBeInTheDocument();
  });

  it("renders the audit timeline", async () => {
    renderPage();
    expect(await screen.findByText("Audit")).toBeInTheDocument();
    expect(screen.getByText("Client créé")).toBeInTheDocument();
  });

  it("renders the empty state when the client is missing", async () => {
    apiMock.get.mockResolvedValue(null);
    renderPage();
    expect(await screen.findByText("Aucun client")).toBeInTheDocument();
  });
});
