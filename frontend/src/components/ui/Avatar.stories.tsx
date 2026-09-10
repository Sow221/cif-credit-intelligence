import type { Meta, StoryObj } from "@storybook/react";
import { Avatar } from "./Avatar";

const meta = {
  title: "ui/Avatar",
  component: Avatar,
  args: {
    name: "Awa Diallo",
  },
} satisfies Meta<typeof Avatar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Small: Story = {
  args: {
    size: "sm",
    name: "Jean Kouadio",
  },
};

export const Large: Story = {
  args: {
    size: "lg",
    name: "Fatou Ndiaye",
  },
};

export const LongName: Story = {
  args: {
    name: "Marie Claire Benoit Dubois",
  },
};
