import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import ReviewQueuePage from "./ReviewQueue";
import { resetStores, makeReview, seedAuth, managerUser, officerUser } from "@/test/helpers";
import { useDataStore } from "@/store/data";

const { apiMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
vi.mock("@/services/api", () => ({ api: apiMock }));

const reviews = [
  makeReview({ review_id: "rev-1", status: "PENDING" }),
  makeReview({ review_id: "rev-2", status: "ASSIGNED", assigned_to: "u2" }),
  makeReview({
    review_id: "rev-3",
    status: "IN_PROGRESS",
    assigned_to: "u2",
    started_at: "2024-03-02T10:00:00Z",
  }),
];

function renderPage() {
  return render(
    <MemoryRouter>
      <ReviewQueuePage />
    </MemoryRouter>,
  );
}

function seed() {
  useDataStore.setState({ reviews, reviewsStatus: "success" });
}

describe("ReviewQueuePage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    seedAuth(managerUser);
    apiMock.get.mockReset();
    apiMock.patch.mockReset();
  });

  it("renders the title and the review rows", () => {
    seed();
    renderPage();
    expect(screen.getByRole("heading", { name: "File de revue" })).toBeInTheDocument();
    expect(screen.getByText("REV-1")).toBeInTheDocument();
    expect(screen.getByText("REV-2")).toBeInTheDocument();
    expect(screen.getAllByText("Awa Diallo").length).toBe(3);
    expect(screen.getAllByText("0.250").length).toBeGreaterThan(0);
    expect(screen.getAllByText("En attente").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Assignée").length).toBeGreaterThan(0);
    expect(screen.getAllByText("En cours").length).toBeGreaterThan(0);
  });

  it("shows context actions for a manager", () => {
    seed();
    renderPage();
    expect(screen.getAllByRole("button", { name: "Assigner" })).toHaveLength(1);
    expect(screen.getAllByRole("button", { name: "Démarrer" })).toHaveLength(1);
    expect(screen.getAllByRole("button", { name: "Compléter" })).toHaveLength(1);
  });

  it("hides management actions for a non-manager role", () => {
    seedAuth(officerUser);
    seed();
    renderPage();
    expect(screen.queryByRole("button", { name: "Assigner" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Démarrer" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Compléter" })).not.toBeInTheDocument();
  });

  it("filters reviews by status", async () => {
    const user = userEvent.setup();
    seed();
    renderPage();
    await user.selectOptions(screen.getByLabelText("Statut"), "IN_PROGRESS");
    expect(screen.getByText("REV-3")).toBeInTheDocument();
    expect(screen.queryByText("REV-1")).not.toBeInTheDocument();
  });

  it("completes a review from the modal", async () => {
    const user = userEvent.setup();
    apiMock.patch.mockResolvedValue(makeReview({ review_id: "rev-3", status: "COMPLETED" }));
    seed();
    renderPage();
    await user.click(screen.getByRole("button", { name: "Compléter" }));
    expect(screen.getByText("Décision finale")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Approuver" }));
    await waitFor(() =>
      expect(apiMock.patch).toHaveBeenCalledWith("/reviews/rev-3/complete", {
        final_action: "APPROVE",
      }),
    );
    expect(screen.queryByText("Décision finale")).not.toBeInTheDocument();
  });

  it("shows the empty state when there are no reviews", () => {
    useDataStore.setState({ reviews: [], reviewsStatus: "success" });
    renderPage();
    expect(screen.getByText("Aucune revue")).toBeInTheDocument();
  });
});
