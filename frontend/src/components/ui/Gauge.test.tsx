import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Gauge } from "./Gauge";

describe("Gauge", () => {
  it("renders percentage text", () => {
    render(<Gauge value={0.5} />);
    expect(screen.getByText("50%")).toBeInTheDocument();
  });

  it("renders label when provided", () => {
    render(<Gauge value={0.8} label="Risk" />);
    expect(screen.getByText("Risk")).toBeInTheDocument();
  });

  it("clamps to 100% when value exceeds max", () => {
    render(<Gauge value={150} max={100} />);
    expect(screen.getByText("100%")).toBeInTheDocument();
  });

  it("clamps to 0% for negative value", () => {
    render(<Gauge value={-0.5} />);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("uses max=1 as default", () => {
    render(<Gauge value={0.75} />);
    expect(screen.getByText("75%")).toBeInTheDocument();
  });

  it("renders SVG with role img and aria-label", () => {
    render(<Gauge value={0.5} label="Risk" />);
    const svg = screen.getByRole("img");
    expect(svg).toHaveAttribute("aria-label", "Risk : 50 %");
  });

  it("renders fallback label 'Risque' in aria-label when no label given", () => {
    render(<Gauge value={0.5} />);
    const svg = screen.getByRole("img");
    expect(svg).toHaveAttribute("aria-label", "Risque : 50 %");
  });
});
