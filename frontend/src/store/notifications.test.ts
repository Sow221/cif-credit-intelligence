import { beforeEach, describe, expect, it } from "vitest";
import { useNotificationsStore } from "./notifications";
import type { NotificationItem } from "./notifications";

function notification(id: string, timestamp: string): NotificationItem {
  return {
    id,
    type: "review",
    title: `Title ${id}`,
    read: false,
    timestamp,
  };
}

describe("useNotificationsStore", () => {
  beforeEach(() => {
    useNotificationsStore.setState({ items: [], isOpen: false });
  });

  it("addNotifications merges and sorts by newest", () => {
    useNotificationsStore.setState({ items: [notification("a", "2024-03-01T10:00:00Z")] });
    useNotificationsStore.getState().addNotifications([notification("b", "2024-03-02T10:00:00Z")]);
    const ids = useNotificationsStore.getState().items.map((item) => item.id);
    expect(ids).toEqual(["b", "a"]);
  });

  it("addNotification prepends sorted", () => {
    useNotificationsStore.setState({ items: [notification("a", "2024-03-01T10:00:00Z")] });
    useNotificationsStore.getState().addNotification(notification("b", "2024-02-01T10:00:00Z"));
    const ids = useNotificationsStore.getState().items.map((item) => item.id);
    expect(ids).toEqual(["a", "b"]);
  });

  it("markAllRead updates every item", () => {
    useNotificationsStore.setState({
      items: [notification("a", "2024-03-01"), notification("b", "2024-03-02")],
    });
    useNotificationsStore.getState().markAllRead();
    expect(useNotificationsStore.getState().items.every((item) => item.read)).toBe(true);
  });

  it("markRead updates a single item", () => {
    useNotificationsStore.setState({
      items: [notification("a", "2024-03-01"), notification("b", "2024-03-02")],
    });
    useNotificationsStore.getState().markRead("b");
    const [a, b] = useNotificationsStore.getState().items;
    expect(a?.read).toBe(false);
    expect(b?.read).toBe(true);
  });

  it("setOpen toggles the dropdown", () => {
    useNotificationsStore.getState().setOpen(true);
    expect(useNotificationsStore.getState().isOpen).toBe(true);
  });
});
