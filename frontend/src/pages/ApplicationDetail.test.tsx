import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import i18n from "@/locales";
import ApplicationDetailPage from "./ApplicationDetail";
import { resetStores, makeDetailApplication } from "@/test/helpers";
import { useDataStore } from "@/store/data";

const { apiMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
vi.mock("@/services/api", () => ({ api: apiMock }));

function renderPage(overrides = {}) {
  useDataStore.setState({
    currentApplication: makeDetailApplication(overrides),
    currentApplicationStatus: "success",
    applicationsStatus: "success",
  });
  return render(
    <MemoryRouter initialEntries={["/applications/app-1"]}>
      <Routes>
        <Route path="/applications/:id" element={<ApplicationDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ApplicationDetailPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    apiMock.get.mockReset();
    apiMock.post.mockReset();
    apiMock.patch.mockReset();
    apiMock.get.mockImplementation((path: string) =>
      path === "/applications/app-1"
        ? Promise.resolve(useDataStore.getState().currentApplication ?? makeDetailApplication())
        : Promise.resolve([]),
    );
  });

  it("shows the missing resource message when there is no id", () => {
    render(
      <MemoryRouter initialEntries={["/applications"]}>
        <Routes>
          <Route path="/applications" element={<ApplicationDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText("Ressource introuvable.")).toBeInTheDocument();
  });

  it("renders the key fact sections of an application", async () => {
    renderPage();
    expect(await screen.findByText("Soumise")).toBeInTheDocument();
    expect(screen.getByText("Montant")).toBeInTheDocument();
    expect(screen.getByText(/250\s?000/)).toBeInTheDocument();
    expect(screen.getAllByText("PD estimée").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Éligible").length).toBeGreaterThan(0);
    expect(screen.getByText("Information Profile")).toBeInTheDocument();
    expect(screen.getByText("Complet")).toBeInTheDocument();
    expect(screen.getByText("Risque")).toBeInTheDocument();
    expect(screen.getByText("Décision finale")).toBeInTheDocument();
  });

  it("renders the client block with a link to the client page", async () => {
    renderPage();
    expect(await screen.findByText("Awa Diallo")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Voir le détail" })).toHaveLength(1);
  });

  it("renders explanation factors and the empty decision reason", async () => {
    renderPage({ explanation_factors: ["savings_balance"], decision_reason: null });
    expect(await screen.findByText("Facteurs du modèle")).toBeInTheDocument();
    expect(screen.getByText("savings_balance")).toBeInTheDocument();
    expect(screen.getByText("Aucune explication disponible.")).toBeInTheDocument();
  });

  it("shows the no-gap message when there are no information gaps", async () => {
    renderPage({ information_gaps: [] });
    expect(await screen.findByText("Aucun écart d'information.")).toBeInTheDocument();
  });

  it("opens the approve modal and confirms the decision", async () => {
    const user = userEvent.setup();
    apiMock.post.mockResolvedValue({
      decision_id: "d1",
      application_id: "app-1",
      recommendation: "APPROVE",
      final_decision: null,
      proposed_amount: null,
      proposed_term: null,
      decision_reason: null,
      policy_version: 3,
      override: null,
    });
    apiMock.patch.mockResolvedValue(undefined);
    renderPage();
    await user.click(await screen.findByRole("button", { name: "Approuver" }));
    expect(screen.getByText("Confirmer l'approbation ?")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Confirmer" }));
    await waitFor(() =>
      expect(apiMock.post).toHaveBeenCalledWith("/decisions", {
        application_id: "app-1",
      }),
    );
    await waitFor(() =>
      expect(apiMock.patch).toHaveBeenCalledWith("/applications/app-1/status", {
        status: "APPROVE",
      }),
    );
    expect(screen.queryByText("Confirmer l'approbation ?")).not.toBeInTheDocument();
  });

  it("requires a justification when overriding a recommendation", async () => {
    const user = userEvent.setup();
    apiMock.post.mockResolvedValue({
      decision_id: "d1",
      application_id: "app-1",
      recommendation: "DECLINE",
      final_decision: null,
      proposed_amount: null,
      proposed_term: null,
      decision_reason: null,
      policy_version: 3,
      override: null,
    });
    renderPage({ recommendation: "DECLINE" });
    await user.click(await screen.findByRole("button", { name: "Déroger" }));
    expect(screen.getByText("Déroger à la recommandation ?")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Confirmer" }));
    expect(
      await screen.findByText(
        "Une justification est obligatoire pour déroger à la recommandation.",
      ),
    ).toBeInTheDocument();
  });

  it("renders the empty state when no application is loaded", async () => {
    apiMock.get.mockResolvedValue(null);
    useDataStore.setState({
      currentApplication: null,
      currentApplicationStatus: "success",
      applicationsStatus: "success",
    });
    render(
      <MemoryRouter initialEntries={["/applications/app-1"]}>
        <Routes>
          <Route path="/applications/:id" element={<ApplicationDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(await screen.findByText("Aucune demande")).toBeInTheDocument();
  });
});
