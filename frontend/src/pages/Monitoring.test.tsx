import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import MonitoringPage from "./Monitoring";
import { resetStores, makeMonitoring } from "@/test/helpers";
import { useDataStore } from "@/store/data";

const { apiMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
vi.mock("@/services/api", () => ({ api: apiMock }));

function renderPage() {
  return render(
    <MemoryRouter>
      <MonitoringPage />
    </MemoryRouter>,
  );
}

function seed(monitoring = makeMonitoring()) {
  useDataStore.setState({
    monitoring,
    monitoringStatus: "success",
    applications: [],
    applicationsStatus: "success",
  });
}

describe("MonitoringPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    apiMock.get.mockReset();
  });

  it("renders the title and all tabs", () => {
    seed();
    renderPage();
    expect(screen.getByRole("heading", { name: "Monitoring" })).toBeInTheDocument();
    for (const label of ["Data", "Modèle", "Décisions", "Fairness", "Incidents"]) {
      expect(screen.getByRole("tab", { name: label })).toBeInTheDocument();
    }
  });

  it("shows data quality metrics on the default tab", () => {
    seed();
    renderPage();
    expect(screen.getByText("Qualité des données")).toBeInTheDocument();
    expect(screen.getByText("Taux de missing")).toBeInTheDocument();
    expect(screen.getByText("Dérive")).toBeInTheDocument();
  });

  it("shows model performance metrics on the model tab", async () => {
    const user = userEvent.setup();
    seed(
      makeMonitoring({
        modelPerformance: {
          auc: 0.8123,
          brier: 0.1234,
          calibration_error: 0.02,
          ks: 0.35,
          gini: 0.6,
        },
      }),
    );
    renderPage();
    await user.click(screen.getByRole("tab", { name: "Modèle" }));
    expect(screen.getByText("0.8123")).toBeInTheDocument();
    expect(screen.getByText("0.1234")).toBeInTheDocument();
    expect(screen.getByText("KS")).toBeInTheDocument();
  });

  it("shows decision stats on the decisions tab", async () => {
    const user = userEvent.setup();
    seed();
    renderPage();
    await user.click(screen.getByRole("tab", { name: "Décisions" }));
    expect(screen.getByText("APPROVE")).toBeInTheDocument();
    expect(screen.getByText("DECLINE")).toBeInTheDocument();
  });

  it("shows fairness metrics per group", async () => {
    const user = userEvent.setup();
    seed();
    renderPage();
    await user.click(screen.getByRole("tab", { name: "Fairness" }));
    expect(screen.getByText("Taux d'approbation")).toBeInTheDocument();
    expect(screen.getByText("Impact adverse")).toBeInTheDocument();
    expect(screen.getByText(/Taille d'échantillon/)).toBeInTheDocument();
  });

  it("shows the empty incidents message", async () => {
    const user = userEvent.setup();
    seed(makeMonitoring({ incidents: [] }));
    renderPage();
    await user.click(screen.getByRole("tab", { name: "Incidents" }));
    expect(screen.getByText("Aucun incident")).toBeInTheDocument();
  });

  it("lists incidents with their severity", async () => {
    const user = userEvent.setup();
    seed(
      makeMonitoring({
        incidents: [
          {
            incident_id: "inc-1",
            type: "data",
            description: "Écart de valeur manquante",
            severity: "CRITICAL",
            created_at: "2024-03-01T10:00:00Z",
            status: "OPEN",
          },
        ],
      }),
    );
    renderPage();
    await user.click(screen.getByRole("tab", { name: "Incidents" }));
    expect(screen.getByText("Écart de valeur manquante")).toBeInTheDocument();
    expect(screen.getByText("CRITICAL")).toBeInTheDocument();
  });
});
