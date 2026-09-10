import { useEffect } from "react";
import { useNotificationsStore } from "@/store/notifications";
import { notificationSocket } from "@/services/websocket";

export function useNotifications() {
  const items = useNotificationsStore((state) => state.items);
  const isOpen = useNotificationsStore((state) => state.isOpen);
  const addNotification = useNotificationsStore((state) => state.addNotification);
  const markAllRead = useNotificationsStore((state) => state.markAllRead);
  const markRead = useNotificationsStore((state) => state.markRead);
  const setOpen = useNotificationsStore((state) => state.setOpen);

  useEffect(() => {
    notificationSocket.connect({
      onNotification: addNotification,
    });
    return () => notificationSocket.disconnect();
  }, [addNotification]);

  const unreadCount = items.filter((item) => !item.read).length;

  return {
    items,
    unreadCount,
    isOpen,
    open: () => setOpen(true),
    close: () => setOpen(false),
    markAllRead,
    markRead,
  };
}
