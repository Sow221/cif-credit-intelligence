import { create } from "zustand";

export type NotificationType = "review" | "model" | "success" | "drift";

export interface NotificationItem {
  id: string;
  type: NotificationType;
  title: string;
  description?: string;
  link?: string;
  read: boolean;
  timestamp: string;
}

interface NotificationsState {
  items: NotificationItem[];
  isOpen: boolean;
  addNotifications: (items: NotificationItem[]) => void;
  addNotification: (item: NotificationItem) => void;
  markAllRead: () => void;
  markRead: (id: string) => void;
  setOpen: (open: boolean) => void;
}

function byNewest(list: NotificationItem[]): NotificationItem[] {
  return [...list].sort((a, b) => b.timestamp.localeCompare(a.timestamp));
}

export const useNotificationsStore = create<NotificationsState>((set) => ({
  items: [],
  isOpen: false,
  addNotifications: (items) => set((state) => ({ items: byNewest([...state.items, ...items]) })),
  addNotification: (item) => set((state) => ({ items: byNewest([item, ...state.items]) })),
  markAllRead: () =>
    set((state) => ({
      items: state.items.map((item) => ({ ...item, read: true })),
    })),
  markRead: (id) =>
    set((state) => ({
      items: state.items.map((item) => (item.id === id ? { ...item, read: true } : item)),
    })),
  setOpen: (open) => set({ isOpen: open }),
}));
