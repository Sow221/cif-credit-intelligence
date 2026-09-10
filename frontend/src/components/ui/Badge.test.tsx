import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Badge } from "./Badge";

describe("Badge", () => {
  it("renders children text", () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("uses neutral variant by default", () => {
    render(<Badge>Neutral</Badge>);
    const el = screen.getByText("Neutral");
    expect(el.className).toContain("bg-background");
  });

  it("applies success variant class", () => {
    render(<Badge variant="success">OK</Badge>);
    expect(screen.getByText("OK").className).toContain("bg-success-50");
  });

  it("applies danger variant class", () => {
    render(<Badge variant="danger">Error</Badge>);
    expect(screen.getByText("Error").className).toContain("bg-danger-50");
  });

  it("applies custom className", () => {
    render(<Badge className="extra">Test</Badge>);
    expect(screen.getByText("Test").className).toContain("extra");
  });
});
