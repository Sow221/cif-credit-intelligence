import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import { Header } from "./Header";
import { resetStores, seedAuth, adminUser } from "@/test/helpers";
import { useNotificationsStore } from "@/store/notifications";
import type { NotificationItem } from "@/store/notifications";

vi.mock("@/services/websocket", () => ({
  notificationSocket: { connect: vi.fn(), disconnect: vi.fn() },
}));

function makeNotification(overrides: Partial<NotificationItem> = {}): NotificationItem {
  return {
    id: "n1",
    type: "review",
    title: "Nouvelle demande en revue",
    read: false,
    timestamp: "2024-03-01T10:00:00Z",
    ...overrides,
  };
}

function renderHeader() {
  return render(
    <MemoryRouter>
      <Header onOpenCommandPalette={() => {}} query="" setQuery={() => {}} />
    </MemoryRouter>,
  );
}

describe("Header", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    seedAuth(adminUser);
  });

  it("renders breadcrumb, search bar and keyboard hint", () => {
    renderHeader();
    expect(screen.getByText("Adaptive Credit")).toBeInTheDocument();
    expect(screen.getByRole("searchbox", { name: "Rechercher" })).toBeInTheDocument();
    expect(screen.getByText("⌘K")).toBeInTheDocument();
  });

  it("opens the command palette when the search field is focused", async () => {
    const user = userEvent.setup();
    const onOpen = vi.fn();
    render(
      <MemoryRouter>
        <Header onOpenCommandPalette={onOpen} query="" setQuery={() => {}} />
      </MemoryRouter>,
    );
    await user.click(screen.getByRole("searchbox", { name: "Rechercher" }));
    expect(onOpen).toHaveBeenCalledTimes(1);
  });

  it("shows the unread notification badge", () => {
    useNotificationsStore.setState({
      items: [
        makeNotification({ id: "n1" }),
        makeNotification({ id: "n2", read: true }),
        makeNotification({ id: "n3" }),
      ],
    });
    renderHeader();
    expect(screen.getByLabelText("2 notifications non lues")).toHaveTextContent("2");
  });

  it("lists the user name and role in the profile dropdown", async () => {
    const user = userEvent.setup();
    renderHeader();
    await user.click(screen.getByRole("button", { name: "Profil utilisateur" }));
    expect(screen.getByText("Admin Diallo — Administrateur")).toBeInTheDocument();
    expect(screen.getByText("Déconnexion")).toBeInTheDocument();
  });
});
