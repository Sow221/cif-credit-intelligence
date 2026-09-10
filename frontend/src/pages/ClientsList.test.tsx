import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import ClientsListPage from "./ClientsList";
import { resetStores, makeClient } from "@/test/helpers";
import { useDataStore } from "@/store/data";

const { apiMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
vi.mock("@/services/api", () => ({ api: apiMock }));

function renderPage() {
  return render(
    <MemoryRouter>
      <ClientsListPage />
    </MemoryRouter>,
  );
}

describe("ClientsListPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    apiMock.get.mockReset();
  });

  it("renders the title and the new client action", () => {
    useDataStore.setState({ clients: [makeClient()], clientsStatus: "success" });
    renderPage();
    expect(screen.getByRole("heading", { name: "Clients" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Nouveau client" })).toBeInTheDocument();
  });

  it("lists clients with their online status", () => {
    useDataStore.setState({
      clients: [
        makeClient({ client_id: "c1", first_name: "Awa", last_name: "Diallo" }),
        makeClient({
          client_id: "c2",
          first_name: "Moussa",
          last_name: "Sow",
          status: "BLOCKED",
          zone: "Thiès",
        }),
      ],
      clientsStatus: "success",
    });
    renderPage();
    expect(screen.getByText("Awa Diallo")).toBeInTheDocument();
    expect(screen.getByText("Moussa Sow")).toBeInTheDocument();
    expect(screen.getByText("Actif")).toBeInTheDocument();
    expect(screen.getByText("Bloqué")).toBeInTheDocument();
  });

  it("filters clients by search", async () => {
    const user = userEvent.setup();
    useDataStore.setState({
      clients: [
        makeClient({ client_id: "c1", first_name: "Awa", last_name: "Diallo" }),
        makeClient({ client_id: "c2", first_name: "Moussa", last_name: "Sow" }),
      ],
      clientsStatus: "success",
    });
    renderPage();
    await user.type(screen.getByRole("searchbox"), "moussa");
    expect(screen.getByText("Moussa Sow")).toBeInTheDocument();
    expect(screen.queryByText("Awa Diallo")).not.toBeInTheDocument();
  });

  it("shows the empty state when no clients match", () => {
    useDataStore.setState({ clients: [], clientsStatus: "success" });
    renderPage();
    expect(screen.getByText("Aucun client")).toBeInTheDocument();
  });

  it("shows the error state and reloads when retry is clicked", async () => {
    const user = userEvent.setup();
    apiMock.get.mockResolvedValue([]);
    useDataStore.setState({ clients: [], clientsStatus: "error", clientsError: "Kaboom" });
    renderPage();
    expect(screen.getByRole("alert")).toHaveTextContent("Kaboom");
    await user.click(screen.getByRole("button", { name: "error.retry" }));
    await waitFor(() =>
      expect(apiMock.get).toHaveBeenCalledWith(expect.stringMatching(/^\/clients/)),
    );
    expect(await screen.findByText("Aucun client")).toBeInTheDocument();
  });
});
