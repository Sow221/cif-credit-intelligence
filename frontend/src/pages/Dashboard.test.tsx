import { beforeEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import DashboardPage from "./Dashboard";
import { resetStores, makeApplication, makeReview, seedAuth, adminUser } from "@/test/helpers";
import { useDataStore } from "@/store/data";

function renderPage() {
  return render(
    <MemoryRouter>
      <DashboardPage />
    </MemoryRouter>,
  );
}

describe("DashboardPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    seedAuth(adminUser);
  });

  it("greets the user and renders the page title actions", () => {
    useDataStore.setState({
      applications: [],
      applicationsStatus: "success",
      reviews: [],
      reviewsStatus: "success",
    });
    renderPage();
    expect(screen.getByText(/Bonjour, Admin/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Nouvelle demande" })).toBeInTheDocument();
  });

  it("computes KPI cards from the seeded applications and reviews", () => {
    useDataStore.setState({
      applications: [
        makeApplication({ application_id: "a1", status: "SUBMITTED" }),
        makeApplication({ application_id: "a2", status: "PROFILED" }),
        makeApplication({ application_id: "a3", status: "APPROVE" }),
        makeApplication({ application_id: "a4", status: "DECLINE" }),
        makeApplication({ application_id: "a5", status: "DECIDED" }),
      ],
      applicationsStatus: "success",
      reviews: [makeReview({ review_id: "r1", status: "PENDING" })],
      reviewsStatus: "success",
    });
    renderPage();
    expect(screen.getByText("En attente").parentElement!.nextElementSibling).toHaveTextContent("2");
    expect(screen.getByText("Approuvés").parentElement!.nextElementSibling).toHaveTextContent("1");
    expect(screen.getByText("En revue").parentElement!.nextElementSibling).toHaveTextContent("1");
    expect(screen.getByText("Refusés").parentElement!.nextElementSibling).toHaveTextContent("1");
  });

  it("shows the thin-file and override alerts", () => {
    useDataStore.setState({
      applications: [
        makeApplication({ application_id: "a1", information_state: "THIN_FILE" }),
        makeApplication({ application_id: "a2", status: "SUBMITTED" }),
      ],
      applicationsStatus: "success",
      reviews: [makeReview({ review_id: "r1", status: "PENDING" })],
      reviewsStatus: "success",
    });
    renderPage();
    expect(screen.getByText(/1 dossiers faibles non traités/)).toBeInTheDocument();
    expect(screen.getByText("dérogations cette semaine")).toBeInTheDocument();
  });

  it("shows no-alert empty state when nothing needs attention", () => {
    useDataStore.setState({
      applications: [],
      applicationsStatus: "success",
      reviews: [],
      reviewsStatus: "success",
    });
    renderPage();
    expect(screen.getByText("Aucune alerte en cours")).toBeInTheDocument();
  });

  it("renders the seven-day activity chart", () => {
    useDataStore.setState({
      applications: [],
      applicationsStatus: "success",
      reviews: [],
      reviewsStatus: "success",
    });
    renderPage();
    for (const label of ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
    expect(screen.getByRole("img", { name: /Lun: \d+ demandes/ })).toBeInTheDocument();
  });

  it("renders recent applications in a table", () => {
    useDataStore.setState({
      applications: [makeApplication({ application_id: "app-1", status: "SUBMITTED" })],
      applicationsStatus: "success",
      reviews: [],
      reviewsStatus: "success",
    });
    renderPage();
    expect(screen.getByText("Dernières demandes")).toBeInTheDocument();
    expect(screen.getByText("APP-1")).toBeInTheDocument();
    expect(screen.getByText("Soumise")).toBeInTheDocument();
  });
});
