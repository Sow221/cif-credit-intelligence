import type { Meta, StoryObj } from "@storybook/react";
import { Gauge } from "./Gauge";

const meta = {
  title: "ui/Gauge",
  component: Gauge,
  args: {
    label: "PD",
  },
} satisfies Meta<typeof Gauge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Low: Story = {
  args: {
    value: 0.08,
  },
};

export const Mid: Story = {
  args: {
    value: 0.2,
  },
};

export const High: Story = {
  args: {
    value: 0.55,
  },
};

export const WithoutLabel: Story = {
  args: {
    label: undefined,
    value: 0.3,
  },
};

export const CustomSize: Story = {
  args: {
    value: 0.45,
    size: 220,
    thresholdLow: 0.4,
    thresholdHigh: 0.7,
  },
};
