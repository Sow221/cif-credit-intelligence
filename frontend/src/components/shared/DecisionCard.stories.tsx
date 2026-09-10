import type { Meta, StoryObj } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { DecisionCard } from "./DecisionCard";

const meta = {
  title: "shared/DecisionCard",
  component: DecisionCard,
} satisfies Meta<typeof DecisionCard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NotEvaluated: Story = {};

export const ApproveRecommendation: Story = {
  args: {
    recommendation: "APPROVE",
    policyVersion: 3,
    onApprove: action("Approuver"),
    onReject: action("Rejeter"),
    onOverride: action("Déroger"),
  },
};

export const ReviewRecommendation: Story = {
  args: {
    recommendation: "REVIEW",
    policyVersion: 2,
    onApprove: action("Approuver"),
  },
};

export const DeclineRecommendation: Story = {
  args: {
    recommendation: "DECLINE",
    policyVersion: 3,
    onApprove: action("Approuver"),
    onReject: action("Rejeter"),
  },
};

export const FinalizedWithOverride: Story = {
  args: {
    recommendation: "DECLINE",
    policyVersion: 3,
    finalDecision: "APPROVE",
    hasOverride: true,
  },
};
