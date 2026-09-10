import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import ApplicationsListPage from "./ApplicationsList";
import { resetStores, makeApplication } from "@/test/helpers";
import { useDataStore } from "@/store/data";

const { apiMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
vi.mock("@/services/api", () => ({ api: apiMock }));

function renderPage() {
  return render(
    <MemoryRouter>
      <ApplicationsListPage />
    </MemoryRouter>,
  );
}

describe("ApplicationsListPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    apiMock.get.mockReset();
  });

  it("renders the page title and the new application action", () => {
    useDataStore.setState({ applications: [makeApplication()], applicationsStatus: "success" });
    renderPage();
    expect(screen.getByRole("heading", { name: "Demandes" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Nouvelle demande" })).toBeInTheDocument();
  });

  it("lists applications with id, client, amount and localized status", () => {
    useDataStore.setState({
      applications: [
        makeApplication({
          application_id: "app-1",
          status: "SUBMITTED",
          client_name: "Awa Diallo",
        }),
        makeApplication({
          application_id: "app-2",
          status: "REVIEW",
          client_name: "Moussa Sow",
          requested_amount: 150000,
        }),
      ],
      applicationsStatus: "success",
    });
    renderPage();
    expect(screen.getByText("APP-1")).toBeInTheDocument();
    expect(screen.getByText("Awa Diallo")).toBeInTheDocument();
    expect(screen.getByText("APP-2")).toBeInTheDocument();
    expect(screen.getByText("Moussa Sow")).toBeInTheDocument();
    expect(screen.getAllByText("Soumise").length).toBeGreaterThan(0);
    expect(screen.getAllByText("En revue").length).toBeGreaterThan(0);
    expect(screen.getAllByRole("link", { name: "Voir le détail" })).toHaveLength(2);
  });

  it("filters rows by status", async () => {
    const user = userEvent.setup();
    useDataStore.setState({
      applications: [
        makeApplication({ application_id: "app-1", status: "SUBMITTED" }),
        makeApplication({ application_id: "app-2", status: "REVIEW" }),
      ],
      applicationsStatus: "success",
    });
    renderPage();
    await user.selectOptions(screen.getByLabelText("Statut"), "REVIEW");
    expect(screen.queryByText("APP-1")).not.toBeInTheDocument();
    expect(screen.getByText("APP-2")).toBeInTheDocument();
  });

  it("filters rows by free-text search", async () => {
    const user = userEvent.setup();
    useDataStore.setState({
      applications: [
        makeApplication({ client_name: "Awa Diallo" }),
        makeApplication({ application_id: "app-2", client_name: "Moussa Sow" }),
      ],
      applicationsStatus: "success",
    });
    renderPage();
    await user.type(screen.getByRole("searchbox"), "awa");
    expect(screen.getByText("Awa Diallo")).toBeInTheDocument();
    expect(screen.queryByText("Moussa Sow")).not.toBeInTheDocument();
  });

  it("shows the empty state when no applications match", () => {
    useDataStore.setState({ applications: [], applicationsStatus: "success" });
    renderPage();
    expect(screen.getByText("Aucune demande")).toBeInTheDocument();
  });

  it("shows the error state and reloads when retry is clicked", async () => {
    const user = userEvent.setup();
    apiMock.get.mockResolvedValue([]);
    useDataStore.setState({
      applicationsStatus: "error",
      applicationsError: "Boom",
      applications: [],
    });
    renderPage();
    expect(screen.getByRole("alert")).toHaveTextContent("Boom");
    await user.click(screen.getByRole("button", { name: "error.retry" }));
    await waitFor(() =>
      expect(apiMock.get).toHaveBeenCalledWith(expect.stringMatching(/^\/applications/)),
    );
    expect(await screen.findByText("Aucune demande")).toBeInTheDocument();
  });
});
