import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";
import { Tooltip } from "./Tooltip";

const meta = {
  title: "ui/Tooltip",
  component: Tooltip,
  args: {
    content: "Voir les informations du client",
    children: <Button variant="secondary">Awa Diallo</Button>,
  },
} satisfies Meta<typeof Tooltip>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Top: Story = {};

export const Bottom: Story = {
  args: {
    position: "bottom",
  },
};

export const Left: Story = {
  args: {
    position: "left",
  },
};

export const Right: Story = {
  args: {
    position: "right",
  },
};

export const Focused: Story = {
  play: async ({ canvasElement }: { canvasElement: HTMLElement }) => {
    const button = canvasElement.querySelector("button");
    button?.focus();
  },
};
