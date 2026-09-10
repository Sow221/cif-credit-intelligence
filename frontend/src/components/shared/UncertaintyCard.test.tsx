import { beforeEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import i18n from "@/locales";
import { UncertaintyCard } from "./UncertaintyCard";
import type { Uncertainty } from "@/types/risk";

const uncertainty: Uncertainty = {
  level: "MODERATE",
  score: 0.5,
  method: "conformal",
  factors: [
    { name: "historical_data", impact: "HIGH", description: "peu d'historique" },
    { name: "new_segment", impact: "LOW" },
  ],
  confidence_interval: { lower: 0.2, upper: 0.8 },
};

describe("UncertaintyCard", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
  });

  it("renders the card title", () => {
    render(<UncertaintyCard uncertainty={uncertainty} />);
    expect(screen.getByText("Incertitude")).toBeInTheDocument();
  });

  it("shows the localized level and method", () => {
    render(<UncertaintyCard uncertainty={uncertainty} />);
    expect(screen.getByText("Modérée")).toBeInTheDocument();
    expect(screen.getByText("Méthode: conformal")).toBeInTheDocument();
  });

  it("renders the confidence interval", () => {
    render(<UncertaintyCard uncertainty={uncertainty} />);
    expect(screen.getByText(/\[0\.200, 0\.800\]/)).toBeInTheDocument();
  });

  it("omits the confidence interval when absent", () => {
    render(<UncertaintyCard uncertainty={{ ...uncertainty, confidence_interval: null }} />);
    expect(screen.queryByText(/Intervalle de confiance/)).not.toBeInTheDocument();
  });

  it("renders uncertainty factors with their impact badges", () => {
    render(<UncertaintyCard uncertainty={uncertainty} />);
    expect(screen.getByText("historical_data")).toBeInTheDocument();
    expect(screen.getByText("new_segment")).toBeInTheDocument();
    expect(screen.getByText("HIGH")).toBeInTheDocument();
    expect(screen.getByText("LOW")).toBeInTheDocument();
  });

  it("renders nothing in the factor list when there are no factors", () => {
    render(<UncertaintyCard uncertainty={{ ...uncertainty, factors: [] }} />);
    expect(screen.queryByText("historical_data")).not.toBeInTheDocument();
  });
});
