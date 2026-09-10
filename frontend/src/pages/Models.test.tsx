import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import ModelsPage from "./Models";
import { resetStores, makeModel } from "@/test/helpers";
import { useDataStore } from "@/store/data";

const { apiMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}));
vi.mock("@/services/api", () => ({ api: apiMock }));

function renderPage() {
  return render(
    <MemoryRouter>
      <ModelsPage />
    </MemoryRouter>,
  );
}

describe("ModelsPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    apiMock.get.mockReset();
    apiMock.post.mockReset();
    apiMock.get.mockResolvedValue([]);
  });

  it("renders the models table with localized statuses", () => {
    useDataStore.setState({
      models: [
        makeModel({ status: "STAGING" }),
        makeModel({ model_id: "mod-2", status: "PRODUCTION", name: "LN v1" }),
      ],
      modelsStatus: "success",
    });
    renderPage();
    expect(screen.getByRole("heading", { name: "Modèles" })).toBeInTheDocument();
    expect(screen.getByText("GBM v2")).toBeInTheDocument();
    expect(screen.getByText("LN v1")).toBeInTheDocument();
    expect(screen.getByText("Staging")).toBeInTheDocument();
    expect(screen.getByText("Production")).toBeInTheDocument();
    expect(screen.getAllByText("0.8200").length).toBeGreaterThan(0);
  });

  it("shows the empty state when no models are available", () => {
    useDataStore.setState({ models: [], modelsStatus: "success" });
    renderPage();
    expect(screen.getAllByText("Modèles").length).toBeGreaterThan(0);
    expect(screen.queryByText("GBM v2")).not.toBeInTheDocument();
  });

  it("opens the model detail modal", async () => {
    const user = userEvent.setup();
    useDataStore.setState({
      models: [makeModel({ brier_score: 0.12 })],
      modelsStatus: "success",
    });
    renderPage();
    await user.click(screen.getByRole("button", { name: "Voir le détail" }));
    expect(screen.getByText("Fiche du modèle")).toBeInTheDocument();
    expect(screen.getByText("Caractéristiques")).toBeInTheDocument();
    expect(screen.getByText("0.1200")).toBeInTheDocument();
  });

  it("promotes a staging model when the promote button is clicked", async () => {
    const user = userEvent.setup();
    apiMock.post.mockResolvedValue(undefined);
    const models = [makeModel({ status: "STAGING" })];
    useDataStore.setState({ models, modelsStatus: "success" });
    renderPage();
    await user.click(screen.getByRole("button", { name: "Promouvoir" }));
    await waitFor(() =>
      expect(apiMock.post).toHaveBeenCalledWith("/models/mod-1/status", {
        action: "PROMOTE",
      }),
    );
    await waitFor(() => expect(apiMock.get).toHaveBeenCalledWith("/models"));
  });

  it("shows the archive action for production models", () => {
    useDataStore.setState({
      models: [makeModel({ status: "PRODUCTION" })],
      modelsStatus: "success",
    });
    renderPage();
    expect(screen.getByRole("button", { name: "Archiver" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Promouvoir" })).not.toBeInTheDocument();
  });
});
