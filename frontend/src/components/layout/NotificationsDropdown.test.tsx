import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import i18n from "@/locales";
import { NotificationsDropdown } from "./NotificationsDropdown";
import { resetStores } from "@/test/helpers";
import { useNotificationsStore } from "@/store/notifications";
import type { NotificationItem } from "@/store/notifications";

const { connectMock, disconnectMock } = vi.hoisted(() => ({
  connectMock: vi.fn(),
  disconnectMock: vi.fn(),
}));
vi.mock("@/services/websocket", () => ({
  notificationSocket: { connect: connectMock, disconnect: disconnectMock },
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

function renderDropdown() {
  return render(
    <MemoryRouter initialEntries={["/review"]}>
      <Routes>
        <Route path="/review" element={<NotificationsDropdown />} />
        <Route path="/applications/app-1" element={<div>application-detail-page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("NotificationsDropdown", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    connectMock.mockClear();
    disconnectMock.mockClear();
  });

  it("connects the notification socket on mount and disconnects on unmount", () => {
    const { unmount } = renderDropdown();
    expect(connectMock).toHaveBeenCalledTimes(1);
    unmount();
    expect(disconnectMock).toHaveBeenCalledTimes(1);
  });

  it("shows an empty message when there are no notifications", async () => {
    const user = userEvent.setup();
    renderDropdown();
    await user.click(screen.getByRole("button", { name: "Voir tout" }));
    expect(screen.getByText("Aucun événement")).toBeInTheDocument();
  });

  it("shows the unread badge and lists the notification titles", async () => {
    const user = userEvent.setup();
    useNotificationsStore.setState({
      items: [
        makeNotification({ id: "n1", title: "Dérive détectée" }),
        makeNotification({ id: "n2", title: "Modèle promu", read: true }),
      ],
    });
    renderDropdown();
    expect(screen.getByLabelText("1 notifications non lues")).toHaveTextContent("1");
    await user.click(screen.getByRole("button", { name: "Voir tout" }));
    expect(screen.getByText("Dérive détectée")).toBeInTheDocument();
    expect(screen.getByText("Modèle promu")).toBeInTheDocument();
  });

  it("marks a notification read and navigates to its link when selected", async () => {
    const user = userEvent.setup();
    useNotificationsStore.setState({
      items: [
        makeNotification({ id: "n1", title: "Nouvelle demande", link: "/applications/app-1" }),
      ],
    });
    renderDropdown();
    await user.click(screen.getByRole("button", { name: "Voir tout" }));
    await user.click(screen.getByRole("menuitem", { name: "Nouvelle demande" }));
    const { items } = useNotificationsStore.getState();
    expect(items[0]?.read).toBe(true);
    expect(await screen.findByText("application-detail-page")).toBeInTheDocument();
  });

  it("marks all notifications read when requested", async () => {
    const user = userEvent.setup();
    useNotificationsStore.setState({
      items: [makeNotification({ id: "n1" }), makeNotification({ id: "n2", read: true })],
    });
    renderDropdown();
    await user.click(screen.getByRole("button", { name: "Voir tout" }));
    await user.click(screen.getByRole("menuitem", { name: "Tout marquer comme lu" }));
    const items = useNotificationsStore.getState().items;
    expect(items.every((item) => item.read)).toBe(true);
    expect(screen.queryByLabelText(/notifications non lues/)).not.toBeInTheDocument();
  });
});
