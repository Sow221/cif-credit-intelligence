import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ToastView, ToastContainer } from "./Toast";

describe("ToastView", () => {
  it("renders message", () => {
    render(<ToastView variant="success" message="Done!" />);
    expect(screen.getByText("Done!")).toBeInTheDocument();
  });

  it("has role status", () => {
    render(<ToastView variant="success" message="Done!" />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("renders custom icon when provided", () => {
    render(
      <ToastView variant="success" message="Done" icon={<span data-testid="custom-icon" />} />,
    );
    expect(screen.getByTestId("custom-icon")).toBeInTheDocument();
  });
});

describe("ToastContainer", () => {
  it("renders nothing when no toasts", () => {
    const { container } = render(<ToastContainer toasts={[]} onDismiss={vi.fn()} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders toasts", () => {
    const toasts = [{ id: "t1", variant: "success" as const, message: "Saved" }];
    render(<ToastContainer toasts={toasts} onDismiss={vi.fn()} />);
    expect(screen.getByText("Saved")).toBeInTheDocument();
  });

  it("calls onDismiss when toast is clicked", () => {
    const onDismiss = vi.fn();
    const toasts = [{ id: "t1", variant: "success" as const, message: "Saved" }];
    render(<ToastContainer toasts={toasts} onDismiss={onDismiss} />);
    fireEvent.click(screen.getByText("Saved").closest("button")!);
    expect(onDismiss).toHaveBeenCalledWith("t1");
  });

  it("has aria-live polite", () => {
    const toasts = [{ id: "t1", variant: "info" as const, message: "Info" }];
    render(<ToastContainer toasts={toasts} onDismiss={vi.fn()} />);
    expect(screen.getByRole("status").parentElement?.parentElement).toHaveAttribute(
      "aria-live",
      "polite",
    );
  });
});
