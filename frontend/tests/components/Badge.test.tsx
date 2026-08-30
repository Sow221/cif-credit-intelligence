import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { DecisionBadge } from "../../src/components/dashboard/DecisionBadge";
import { Badge } from "../../src/components/ui/Badge";

describe("DecisionBadge", () => {
  it("affiche le libelle d'une decision APPROBATION", () => {
    render(<DecisionBadge decision="APPROBATION" />);
    expect(screen.getByText("Approbation")).toBeTruthy();
  });

  it("affiche le libelle d'une decision REFUS", () => {
    render(<DecisionBadge decision="REFUS" />);
    expect(screen.getByText("Refus")).toBeTruthy();
  });
});

describe("Badge", () => {
  it("affiche ses enfants", () => {
    render(<Badge>Risque faible</Badge>);
    expect(screen.getByText("Risque faible")).toBeTruthy();
  });
});
