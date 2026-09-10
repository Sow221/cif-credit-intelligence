import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Card } from "./Card";

describe("Card", () => {
  it("renders children", () => {
    render(<Card>Content here</Card>);
    expect(screen.getByText("Content here")).toBeInTheDocument();
  });

  it("renders title and subtitle", () => {
    render(<Card title="My Title" subtitle="My Subtitle" />);
    expect(screen.getByText("My Title")).toBeInTheDocument();
    expect(screen.getByText("My Subtitle")).toBeInTheDocument();
  });

  it("does not render title section when title is absent", () => {
    const { container } = render(<Card>Body</Card>);
    expect(container.querySelector("h3")).not.toBeInTheDocument();
  });

  it("renders actions when provided", () => {
    render(<Card title="Title" actions={<button>Edit</button>} />);
    expect(screen.getByRole("button", { name: "Edit" })).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(<Card className="custom">Body</Card>);
    expect(screen.getByText("Body").closest(".card")).toHaveClass("custom");
  });
});
