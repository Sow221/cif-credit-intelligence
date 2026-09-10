import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import i18n from "@/locales";
import { CommandPalette } from "./CommandPalette";
import { resetStores, makeApplication, makeClient } from "@/test/helpers";
import { useDataStore } from "@/store/data";

function renderPalette(open: boolean, onClose = vi.fn()) {
  return render(
    <MemoryRouter initialEntries={["/applications"]}>
      <Routes>
        <Route path="/applications" element={<CommandPalette open={open} onClose={onClose} />} />
        <Route path="/applications/new" element={<div>new-application-page</div>} />
        <Route path="/clients/c2" element={<div>client-page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("CommandPalette", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
  });

  it("renders nothing when closed", () => {
    renderPalette(false);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("shows the default actions for an empty query", () => {
    renderPalette(true);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByRole("searchbox")).toBeInTheDocument();
    expect(screen.getByText("Nouvelle demande")).toBeInTheDocument();
    expect(screen.getByText("Nouveau client")).toBeInTheDocument();
  });

  it("navigates to the new application route when the first action is selected", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    renderPalette(true, onClose);
    await user.keyboard("{Enter}");
    expect(onClose).toHaveBeenCalledTimes(1);
    expect(await screen.findByText("new-application-page")).toBeInTheDocument();
  });

  it("filters clients by typed name", async () => {
    const user = userEvent.setup();
    useDataStore.setState({
      clients: [makeClient({ client_id: "c2", first_name: "Bintou", last_name: "Kane" })],
    });
    renderPalette(true);
    const input = screen.getByRole("searchbox");
    await user.type(input, "bintou");
    expect(await screen.findByText("Bintou Kane")).toBeInTheDocument();
    expect(screen.getByText("Clients")).toBeInTheDocument();
  });

  it("filters applications by typed id and shows its amount", async () => {
    const user = userEvent.setup();
    useDataStore.setState({
      applications: [makeApplication({ application_id: "app-x-1234", requested_amount: 500000 })],
    });
    renderPalette(true);
    const input = screen.getByRole("searchbox");
    await user.type(input, "app-x");
    expect(await screen.findByText(/APP-X-1/)).toBeInTheDocument();
    expect(screen.getByText(new RegExp("500 000", "i"))).toBeInTheDocument();
  });

  it("shows the empty message when no results match", async () => {
    const user = userEvent.setup();
    renderPalette(true);
    const input = screen.getByRole("searchbox");
    await user.type(input, "zzzzz");
    expect(await screen.findByText("Aucune demande")).toBeInTheDocument();
  });

  it("closes when Escape is pressed", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    renderPalette(true, onClose);
    await user.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("focuses the search input when opened", async () => {
    renderPalette(true);
    await waitFor(() => expect(screen.getByRole("searchbox")).toHaveFocus());
  });
});
