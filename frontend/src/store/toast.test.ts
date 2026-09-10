import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useToastStore } from "./toast";

describe("useToastStore", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    useToastStore.setState({ toasts: [] });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("adds a toast with duration and default id counter", () => {
    useToastStore.getState().addToast("success", "Saved");
    const [toast] = useToastStore.getState().toasts;
    expect(toast?.variant).toBe("success");
    expect(toast?.message).toBe("Saved");
    expect(toast?.duration).toBe(4000);
    expect(toast?.id).toMatch(/^toast-/);
  });

  it("auto-removes the toast after its duration", () => {
    useToastStore.getState().addToast("info", "Heads up", 1000);
    expect(useToastStore.getState().toasts).toHaveLength(1);
    vi.advanceTimersByTime(1000);
    expect(useToastStore.getState().toasts).toHaveLength(0);
  });

  it("removeToast filters by id", () => {
    useToastStore.getState().addToast("error", "Bad");
    const id = useToastStore.getState().toasts[0]!.id;
    useToastStore.getState().removeToast(id);
    expect(useToastStore.getState().toasts).toHaveLength(0);
  });
});