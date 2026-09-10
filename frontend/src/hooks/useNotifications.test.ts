import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useNotifications } from "./useNotifications";
import { useNotificationsStore } from "@/store/notifications";
import type { NotificationItem } from "@/store/notifications";

vi.mock("@/services/websocket", () => ({
  notificationSocket: {
    connect: vi.fn(),
    disconnect: vi.fn(),
  },
}));

const notification: NotificationItem = {
  id: "n1",
  type: "review",
  title: "New review assigned",
  description: "Review for app-1",
  link: "/review/rev-1",
  read: false,
  timestamp: "2024-03-01T10:00:00Z",
};

const readNotification: NotificationItem = {
  id: "n2",
  type: "success",
  title: "Decision made",
  read: true,
  timestamp: "2024-03-02T10:00:00Z",
};

describe("useNotifications", () => {
  beforeEach(() => {
    useNotificationsStore.setState({ items: [], isOpen: false });
    vi.clearAllMocks();
  });

  it("returns items and computes unreadCount", () => {
    useNotificationsStore.setState({ items: [notification, readNotification] });
    const { result } = renderHook(() => useNotifications());
    expect(result.current.items).toHaveLength(2);
    expect(result.current.unreadCount).toBe(1);
  });

  it("returns 0 unreadCount when all read", () => {
    useNotificationsStore.setState({ items: [readNotification] });
    const { result } = renderHook(() => useNotifications());
    expect(result.current.unreadCount).toBe(0);
  });

  it("open sets isOpen to true", () => {
    const { result } = renderHook(() => useNotifications());
    expect(result.current.isOpen).toBe(false);

    act(() => {
      result.current.open();
    });

    expect(useNotificationsStore.getState().isOpen).toBe(true);
  });

  it("close sets isOpen to false", () => {
    useNotificationsStore.setState({ isOpen: true });
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.close();
    });

    expect(useNotificationsStore.getState().isOpen).toBe(false);
  });

  it("markAllRead marks all items as read", () => {
    useNotificationsStore.setState({ items: [notification, readNotification] });
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.markAllRead();
    });

    const items = useNotificationsStore.getState().items;
    expect(items.every((i) => i.read)).toBe(true);
  });

  it("markRead marks single item as read", () => {
    useNotificationsStore.setState({ items: [notification] });
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.markRead("n1");
    });

    expect(useNotificationsStore.getState().items[0]?.read).toBe(true);
  });
});
