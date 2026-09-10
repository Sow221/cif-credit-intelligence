import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { notificationSocket } from "./websocket";

class FakeWebSocket {
  static instances: FakeWebSocket[] = [];
  url: string;
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: unknown }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  closedTimes = 0;

  constructor(url: string) {
    this.url = url;
    FakeWebSocket.instances.push(this);
  }

  close(): void {
    this.closedTimes += 1;
    this.onclose?.();
  }
}

describe("notificationSocket", () => {
  let onNotification: ReturnType<typeof vi.fn>;
  let onConnected: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    FakeWebSocket.instances = [];
    onNotification = vi.fn();
    onConnected = vi.fn();
  });

  afterEach(() => {
    notificationSocket.disconnect();
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("opens a connection and reports connected", () => {
    vi.stubGlobal("WebSocket", FakeWebSocket);
    notificationSocket.connect({ onNotification, onConnected });
    expect(FakeWebSocket.instances).toHaveLength(1);
    FakeWebSocket.instances[0]!.onopen?.();
    expect(onConnected).toHaveBeenCalledTimes(1);
  });

  it("delivers parsed notifications and ignores malformed payloads", () => {
    vi.stubGlobal("WebSocket", FakeWebSocket);
    notificationSocket.connect({ onNotification, onConnected });
    const socket = FakeWebSocket.instances[0]!;
    socket.onmessage?.({ data: JSON.stringify({ id: "n1", type: "review", title: "T" }) });
    expect(onNotification).toHaveBeenCalledTimes(1);
    socket.onmessage?.({ data: "{broken" });
    expect(onNotification).toHaveBeenCalledTimes(1);
  });

  it("reconnects 3s after close unless disconnected", () => {
    vi.useFakeTimers();
    vi.stubGlobal("WebSocket", FakeWebSocket);
    notificationSocket.connect({ onNotification, onConnected });
    FakeWebSocket.instances[0]!.onclose?.();
    expect(FakeWebSocket.instances).toHaveLength(1);
    vi.advanceTimersByTime(3000);
    expect(FakeWebSocket.instances).toHaveLength(2);
  });

  it("does not reconnect after disconnect", () => {
    vi.useFakeTimers();
    vi.stubGlobal("WebSocket", FakeWebSocket);
    notificationSocket.connect({ onNotification, onConnected });
    notificationSocket.disconnect();
    vi.advanceTimersByTime(10000);
    expect(FakeWebSocket.instances).toHaveLength(1);
    expect(FakeWebSocket.instances[0]!.closedTimes).toBe(1);
  });

  it("closes the socket on error", () => {
    vi.stubGlobal("WebSocket", FakeWebSocket);
    notificationSocket.connect({ onNotification, onConnected });
    const socket = FakeWebSocket.instances[0]!;
    socket.onerror?.();
    expect(socket.closedTimes).toBe(1);
  });

  it("schedules a reconnect when the constructor throws", () => {
    vi.useFakeTimers();
    vi.stubGlobal("WebSocket", () => {
      throw new Error("cannot connect");
    });
    notificationSocket.connect({ onNotification, onConnected });
    vi.advanceTimersByTime(3000);
    expect(onConnected).not.toHaveBeenCalled();
    expect(FakeWebSocket.instances).toHaveLength(0);
  });
});
