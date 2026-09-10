import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import i18n from "@/locales";
import ApplicationNewPage from "./ApplicationNew";
import { resetStores, makeApplication, makeClient } from "@/test/helpers";
import { useDataStore } from "@/store/data";

const { apiMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
vi.mock("@/services/api", () => ({ api: apiMock }));

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/applications/new"]}>
      <Routes>
        <Route path="/applications/new" element={<ApplicationNewPage />} />
        <Route path="/applications/:id" element={<div>application-created</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ApplicationNewPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    apiMock.get.mockReset();
    apiMock.post.mockReset();
    apiMock.get.mockResolvedValue([]);
  });

  it("renders the form title and fields", () => {
    useDataStore.setState({
      clients: [makeClient()],
      clientsStatus: "success",
    });
    renderPage();
    expect(screen.getByRole("heading", { name: "Nouvelle demande" })).toBeInTheDocument();
    expect(screen.getByRole("searchbox")).toBeInTheDocument();
    expect(screen.getByLabelText("Produit")).toBeInTheDocument();
    expect(screen.getByLabelText("Durée")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Soumettre la demande" })).toBeInTheDocument();
  });

  it("suggests matching clients while typing", async () => {
    const user = userEvent.setup();
    useDataStore.setState({
      clients: [
        makeClient({ client_id: "c1", first_name: "Bintou", last_name: "Kane" }),
        makeClient({ client_id: "c2", first_name: "Moussa", last_name: "Sow" }),
      ],
      clientsStatus: "success",
    });
    renderPage();
    await user.type(screen.getByRole("searchbox"), "bin");
    expect(await screen.findByText("Bintou Kane")).toBeInTheDocument();
    expect(screen.queryByText("Moussa Sow")).not.toBeInTheDocument();
  });

  it("shows validation errors when submitting an empty form", async () => {
    const user = userEvent.setup();
    useDataStore.setState({ clients: [], clientsStatus: "success" });
    renderPage();
    await user.click(screen.getByRole("button", { name: "Soumettre la demande" }));
    expect(screen.getAllByText("Champ obligatoire").length).toBeGreaterThan(0);
    expect(screen.getByText("Montant invalide (doit être > 0)")).toBeInTheDocument();
    expect(screen.getByText("Durée invalide (6, 12, 18 ou 24 mois)")).toBeInTheDocument();
  });

  it("submits a valid form and navigates to the created application", async () => {
    const user = userEvent.setup();
    apiMock.post.mockResolvedValue(makeApplication());
    useDataStore.setState({
      clients: [makeClient({ client_id: "c1", first_name: "Bintou", last_name: "Kane" })],
      clientsStatus: "success",
    });
    renderPage();
    await user.type(screen.getByRole("searchbox"), "bintou");
    await user.click(await screen.findByText("Bintou Kane"));
    await user.selectOptions(screen.getByLabelText("Produit"), "SMALL_BUSINESS");
    await user.type(screen.getByLabelText("Montant (XOF)"), "250000");
    await user.selectOptions(screen.getByLabelText("Durée"), "12");
    await user.click(screen.getByRole("button", { name: "Soumettre la demande" }));
    expect(apiMock.post).toHaveBeenCalledWith(
      "/applications",
      expect.objectContaining({
        client_id: "c1",
        product_id: "SMALL_BUSINESS",
        requested_amount: 250000,
        requested_term: 12,
      }),
    );
    expect(await screen.findByText("application-created")).toBeInTheDocument();
  });

  it("provides a shortcut to create a new client", () => {
    useDataStore.setState({ clients: [], clientsStatus: "success" });
    renderPage();
    expect(screen.getByRole("button", { name: "Créer un nouveau client" })).toBeInTheDocument();
  });
});
