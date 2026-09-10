import { create } from "zustand";

export type ToastVariant = "success" | "error" | "warning" | "info";

export interface ToastItem {
  id: string;
  variant: ToastVariant;
  message: string;
  duration: number;
}

let nextToastId = 0;

interface ToastState {
  toasts: ToastItem[];
  addToast: (variant: ToastVariant, message: string, duration?: number) => void;
  removeToast: (id: string) => void;
}

const DEFAULT_DURATION = 4000;

export const useToastStore = create<ToastState>((set, get) => ({
  toasts: [],
  addToast: (variant, message, duration = DEFAULT_DURATION) => {
    const id = `toast-${++nextToastId}`;
    const toast: ToastItem = { id, variant, message, duration };
    set((state) => ({ toasts: [...state.toasts, toast] }));
    setTimeout(() => get().removeToast(id), duration);
  },
  removeToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((toast) => toast.id !== id) })),
}));
