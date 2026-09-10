import type { Meta, StoryObj } from "@storybook/react";
import { ProgressBar } from "./ProgressBar";

const meta = {
  title: "ui/ProgressBar",
  component: ProgressBar,
  args: {
    value: 45,
  },
} satisfies Meta<typeof ProgressBar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithLabel: Story = {
  args: {
    value: 72,
    showLabel: true,
  },
};

export const CustomColor: Story = {
  args: {
    value: 80,
    color: "#16A34A",
    showLabel: true,
  },
};

export const Complete: Story = {
  args: {
    value: 100,
    showLabel: true,
  },
};

export const CustomMax: Story = {
  args: {
    value: 450,
    max: 500,
    showLabel: true,
  },
};
