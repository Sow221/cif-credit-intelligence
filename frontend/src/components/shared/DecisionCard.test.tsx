import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/locales";
import { DecisionCard } from "./DecisionCard";

describe("DecisionCard", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
  });

  it("renders the card title", () => {
    render(<DecisionCard />);
    expect(screen.getByText("Décision finale")).toBeInTheDocument();
  });

  it("shows not evaluated when no recommendation is provided", () => {
    render(<DecisionCard />);
    expect(screen.getByText("Non évaluée")).toBeInTheDocument();
  });

  it("shows not evaluated for the UNKNOWN recommendation", () => {
    render(<DecisionCard recommendation="UNKNOWN" />);
    expect(screen.getByText("Non évaluée")).toBeInTheDocument();
  });

  it("shows the recommendation badge when provided", () => {
    render(<DecisionCard recommendation="APPROVE" />);
    expect(screen.getByText("APPROVE")).toBeInTheDocument();
  });

  it("shows the policy version when provided", () => {
    render(<DecisionCard recommendation="APPROVE" policyVersion={3} />);
    expect(screen.getByText("Version de politique: 3")).toBeInTheDocument();
  });

  it("hides the policy version when null", () => {
    render(<DecisionCard recommendation="APPROVE" policyVersion={null} />);
    expect(screen.queryByText(/Version de politique/)).not.toBeInTheDocument();
  });

  it("shows final decision and override badges", () => {
    render(<DecisionCard recommendation="DECLINE" finalDecision="APPROVE" hasOverride />);
    expect(screen.getByText("DECLINE")).toBeInTheDocument();
    expect(screen.getByText("APPROVE")).toBeInTheDocument();
    expect(screen.getByText("OVERRIDE")).toBeInTheDocument();
  });

  it("renders action buttons when no final decision exists", () => {
    render(<DecisionCard onApprove={vi.fn()} onReject={vi.fn()} onOverride={vi.fn()} />);
    expect(screen.getByText("Approuver")).toBeInTheDocument();
    expect(screen.getByText("Rejeter")).toBeInTheDocument();
    expect(screen.getByText("Déroger")).toBeInTheDocument();
  });

  it("hides action buttons when a final decision exists", () => {
    render(
      <DecisionCard
        finalDecision="APPROVE"
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onOverride={vi.fn()}
      />,
    );
    expect(screen.queryByText("Approuver")).not.toBeInTheDocument();
    expect(screen.queryByText("Rejeter")).not.toBeInTheDocument();
    expect(screen.queryByText("Déroger")).not.toBeInTheDocument();
  });

  it("only renders the handlers that are provided", () => {
    render(<DecisionCard onApprove={vi.fn()} />);
    expect(screen.getByText("Approuver")).toBeInTheDocument();
    expect(screen.queryByText("Rejeter")).not.toBeInTheDocument();
    expect(screen.queryByText("Déroger")).not.toBeInTheDocument();
  });

  it("triggers the action callbacks when clicked", async () => {
    const user = userEvent.setup();
    const onApprove = vi.fn();
    const onReject = vi.fn();
    const onOverride = vi.fn();
    render(<DecisionCard onApprove={onApprove} onReject={onReject} onOverride={onOverride} />);
    await user.click(screen.getByText("Approuver"));
    await user.click(screen.getByText("Rejeter"));
    await user.click(screen.getByText("Déroger"));
    expect(onApprove).toHaveBeenCalledTimes(1);
    expect(onReject).toHaveBeenCalledTimes(1);
    expect(onOverride).toHaveBeenCalledTimes(1);
  });
});
