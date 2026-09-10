import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { Tooltip } from "./Tooltip";

describe("Tooltip", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders children", () => {
    render(
      <Tooltip content="Hint">
        <button>Hover me</button>
      </Tooltip>,
    );
    expect(screen.getByText("Hover me")).toBeInTheDocument();
  });

  it("shows tooltip on mouse enter after delay", () => {
    render(
      <Tooltip content="Hint text">
        <button>Hover</button>
      </Tooltip>,
    );
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();

    fireEvent.mouseEnter(screen.getByText("Hover"));
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(300);
    });
    expect(screen.getByRole("tooltip")).toHaveTextContent("Hint text");
  });

  it("hides tooltip on mouse leave", () => {
    render(
      <Tooltip content="Hint">
        <button>Hover</button>
      </Tooltip>,
    );

    act(() => {
      fireEvent.mouseEnter(screen.getByText("Hover"));
      vi.advanceTimersByTime(300);
    });
    expect(screen.getByRole("tooltip")).toBeInTheDocument();

    act(() => {
      fireEvent.mouseLeave(screen.getByText("Hover"));
    });
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });

  it("shows tooltip on focus after delay", () => {
    render(
      <Tooltip content="Focus tip">
        <button>Focusable</button>
      </Tooltip>,
    );

    act(() => {
      fireEvent.focus(screen.getByText("Focusable"));
      vi.advanceTimersByTime(300);
    });
    expect(screen.getByRole("tooltip")).toHaveTextContent("Focus tip");
  });

  it("hides tooltip on blur", () => {
    render(
      <Tooltip content="Focus tip">
        <button>Focusable</button>
      </Tooltip>,
    );

    act(() => {
      fireEvent.focus(screen.getByText("Focusable"));
      vi.advanceTimersByTime(300);
    });

    act(() => {
      fireEvent.blur(screen.getByText("Focusable"));
    });
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });
});
