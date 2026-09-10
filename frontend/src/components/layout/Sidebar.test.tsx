import { beforeEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import { Sidebar } from "./Sidebar";
import { resetStores, seedAuth, adminUser, makeReview } from "@/test/helpers";
import { useDataStore } from "@/store/data";
import { useAuthStore } from "@/store/auth";

function renderSidebar() {
  return render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <Sidebar />
    </MemoryRouter>,
  );
}

describe("Sidebar", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    seedAuth(adminUser);
  });

  it("renders the app name and all navigation items", () => {
    renderSidebar();
    expect(screen.getByText("Adaptive Credit")).toBeInTheDocument();
    for (const label of [
      "Tableau de bord",
      "Demandes",
      "Clients",
      "Revue",
      "Modèles",
      "Monitoring",
      "Administration",
    ]) {
      expect(screen.getByRole("link", { name: label })).toBeInTheDocument();
    }
  });

  it("shows the logged-in user and role", () => {
    renderSidebar();
    expect(screen.getByText("Admin Diallo")).toBeInTheDocument();
    expect(screen.getByText("Administrateur")).toBeInTheDocument();
  });

  it("shows the pending review badge with the pending count", () => {
    useDataStore.setState({
      reviews: [
        makeReview({ review_id: "r1", status: "PENDING" }),
        makeReview({ review_id: "r2", status: "ASSIGNED" }),
        makeReview({ review_id: "r3", status: "PENDING" }),
      ],
      reviewsStatus: "success",
    });
    renderSidebar();
    const reviewLink = screen.getByRole("link", { name: /Revue/ });
    expect(reviewLink).toHaveTextContent("2");
    expect(screen.getByLabelText("2 en attente")).toBeInTheDocument();
  });

  it("omits the pending badge when there are no pending reviews", () => {
    useDataStore.setState({ reviews: [], reviewsStatus: "success" });
    renderSidebar();
    expect(screen.queryByLabelText(/en attente/)).not.toBeInTheDocument();
  });

  it("renders no user block when logged out", () => {
    resetStores();
    renderSidebar();
    expect(screen.queryByText("Admin Diallo")).not.toBeInTheDocument();
  });

  it("signs the user out when the logout button is clicked", async () => {
    const user = userEvent.setup();
    renderSidebar();
    await user.click(screen.getByRole("button", { name: "Déconnexion" }));
    expect(useAuthStore.getState().user).toBeNull();
  });
});
