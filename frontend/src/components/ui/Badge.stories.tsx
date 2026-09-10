import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "./Badge";

const meta = {
  title: "ui/Badge",
  component: Badge,
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Neutral: Story = {
  args: {
    variant: "neutral",
    children: "Brouillon",
  },
};

export const Success: Story = {
  args: {
    variant: "success",
    children: "Approuvée",
  },
};

export const Warning: Story = {
  args: {
    variant: "warning",
    children: "En revue",
  },
};

export const Danger: Story = {
  args: {
    variant: "danger",
    children: "Refusée",
  },
};

export const Info: Story = {
  args: {
    variant: "info",
    children: "Soumise",
  },
};
