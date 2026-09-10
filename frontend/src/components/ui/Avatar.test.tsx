import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Avatar } from "./Avatar";

describe("Avatar", () => {
  it("renders initials from name", () => {
    render(<Avatar name="Awa Diallo" />);
    expect(screen.getByText("AD")).toBeInTheDocument();
  });

  it("renders single initial for single name", () => {
    render(<Avatar name="Awa" />);
    expect(screen.getByText("A")).toBeInTheDocument();
  });

  it("limits to first two words", () => {
    render(<Avatar name="Awa Binta Diallo" />);
    expect(screen.getByText("AB")).toBeInTheDocument();
  });

  it("is marked as aria-hidden", () => {
    render(<Avatar name="Awa Diallo" />);
    expect(screen.getByText("AD")).toHaveAttribute("aria-hidden", "true");
  });

  it("applies sm size class", () => {
    render(<Avatar name="Awa Diallo" size="sm" />);
    const el = screen.getByText("AD");
    expect(el.className).toContain("h-8");
  });

  it("applies lg size class", () => {
    render(<Avatar name="Awa Diallo" size="lg" />);
    const el = screen.getByText("AD");
    expect(el.className).toContain("h-16");
  });

  it("applies custom className", () => {
    render(<Avatar name="Awa Diallo" className="my-class" />);
    expect(screen.getByText("AD").className).toContain("my-class");
  });
});
