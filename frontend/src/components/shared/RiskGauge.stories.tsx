import type { Meta, StoryObj } from "@storybook/react";
import { RiskGauge } from "./RiskGauge";
import type { RiskAssessment } from "@/types/risk";

const lowRisk: RiskAssessment = {
  pd_raw: 0.12,
  pd_calibrated: 0.1,
  risk_band: "LOW",
  model_version: "gbm-v1",
  feature_set_id: "CORE_25",
};

const meta = {
  title: "shared/RiskGauge",
  component: RiskGauge,
  args: {
    risk: lowRisk,
  },
} satisfies Meta<typeof RiskGauge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const LowRisk: Story = {};

export const MediumRisk: Story = {
  args: {
    risk: {
      pd_raw: 0.3,
      pd_calibrated: 0.28,
      risk_band: "MEDIUM",
      model_version: "gbm-v1",
      feature_set_id: "CORE_25",
      calibration_version: "cal-v2",
    },
  },
};

export const HighRisk: Story = {
  args: {
    risk: {
      pd_raw: 0.62,
      pd_calibrated: null,
      risk_band: "HIGH",
      model_version: "xgb-v3",
      feature_set_id: "CORE_50",
    },
  },
};

export const UnknownBand: Story = {
  args: {
    risk: {
      ...lowRisk,
      pd_raw: 0.2,
      risk_band: "UNKNOWN",
    },
  },
};
