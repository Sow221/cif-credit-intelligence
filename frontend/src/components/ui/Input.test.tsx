import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Input } from "./Input";

describe("Input", () => {
  it("renders an input element", () => {
    render(<Input />);
    expect(screen.getByRole("textbox")).toBeInTheDocument();
  });

  it("renders label and links via htmlFor", () => {
    render(<Input label="Email" />);
    const label = screen.getByText("Email");
    const input = screen.getByRole("textbox");
    expect(label).toHaveAttribute("for", input.id);
  });

  it("renders error message with role alert", () => {
    render(<Input error="Required field" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Required field");
  });

  it("sets aria-invalid when error is present", () => {
    render(<Input error="Bad" />);
    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
  });

  it("sets aria-describedby to error id", () => {
    render(<Input error="Bad" />);
    const input = screen.getByRole("textbox");
    const describedBy = input.getAttribute("aria-describedby");
    expect(describedBy).toBeDefined();
    expect(document.getElementById(describedBy!)).toHaveTextContent("Bad");
  });

  it("renders helper text when no error", () => {
    render(<Input helper="Optional" />);
    expect(screen.getByText("Optional")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("hides helper when error is present", () => {
    render(<Input error="Bad" helper="Don't show" />);
    expect(screen.queryByText("Don't show")).not.toBeInTheDocument();
  });

  it("forwards ref", () => {
    const ref = { current: null };
    render(<Input ref={ref as React.RefObject<HTMLInputElement>} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });
});
