import type { NotificationItem } from "@/store/notifications";

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/ws";

export type NotificationHandler = (notification: NotificationItem) => void;
export type ConnectionHandler = () => void;

interface Subscriber {
  onNotification: NotificationHandler;
  onConnected?: ConnectionHandler;
}

class NotificationSocket {
  private socket: WebSocket | null = null;
  private subscriber: Subscriber | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private closed = false;

  connect(subscriber: Subscriber): void {
    this.subscriber = subscriber;
    this.closed = false;
    this.open();
  }

  private open(): void {
    try {
      this.socket = new WebSocket(WS_URL);
      this.socket.onopen = () => {
        this.subscriber?.onConnected?.();
      };
      this.socket.onmessage = (event) => {
        try {
          const notification = JSON.parse(event.data as string) as NotificationItem;
          this.subscriber?.onNotification(notification);
        } catch {
          // malformed payload ignored
        }
      };
      this.socket.onclose = () => {
        if (!this.closed && !this.reconnectTimer) {
          this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.open();
          }, 3000);
        }
      };
      this.socket.onerror = () => {
        this.socket?.close();
      };
    } catch {
      if (!this.closed && !this.reconnectTimer) {
        this.reconnectTimer = setTimeout(() => {
          this.reconnectTimer = null;
          this.open();
        }, 3000);
      }
    }
  }

  disconnect(): void {
    this.closed = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.socket?.close();
    this.socket = null;
  }
}

export const notificationSocket = new NotificationSocket();
