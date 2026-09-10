import type { Meta, StoryObj } from "@storybook/react";
import { UncertaintyCard } from "./UncertaintyCard";
import type { Uncertainty } from "@/types/risk";

const base: Uncertainty = {
  level: "MODERATE",
  score: 0.5,
  method: "conformal",
  factors: [
    { name: "historical_data", impact: "HIGH", description: "peu d'historique" },
    { name: "new_segment", impact: "LOW" },
  ],
  confidence_interval: { lower: 0.2, upper: 0.8 },
};

const meta = {
  title: "shared/UncertaintyCard",
  component: UncertaintyCard,
  args: {
    uncertainty: base,
  },
} satisfies Meta<typeof UncertaintyCard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Moderate: Story = {};

export const Low: Story = {
  args: {
    uncertainty: {
      level: "LOW",
      score: 0.15,
      method: "dropout",
      factors: [{ name: "application_age", impact: "LOW" }],
      confidence_interval: { lower: 0.02, upper: 0.18 },
    },
  },
};

export const HighWithoutInterval: Story = {
  args: {
    uncertainty: {
      level: "HIGH",
      score: 0.8,
      method: "bagging",
      factors: [
        { name: "missing_income", impact: "HIGH" },
        { name: "stale_documents", impact: "HIGH" },
      ],
      confidence_interval: null,
    },
  },
};

export const WithoutFactors: Story = {
  args: {
    uncertainty: {
      level: "MODERATE",
      score: 0.5,
      method: "conformal",
      factors: [],
      confidence_interval: { lower: 0.25, upper: 0.75 },
    },
  },
};
