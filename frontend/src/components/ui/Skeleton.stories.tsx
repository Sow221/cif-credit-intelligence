import type { Meta, StoryObj } from "@storybook/react";
import { Skeleton, SkeletonList } from "./Skeleton";

const meta = {
  title: "ui/Skeleton",
  component: Skeleton,
  args: {
    className: "w-48",
  },
} satisfies Meta<typeof Skeleton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Text: Story = {};

export const Title: Story = {
  args: {
    variant: "title",
  },
};

export const Card: Story = {
  args: {
    variant: "card",
  },
};

export const Avatar: Story = {
  args: {
    variant: "avatar",
  },
};

export const Button: Story = {
  args: {
    variant: "button",
  },
};

export const List: Story = {
  render: (args) => <SkeletonList rows={5} variant={args.variant ?? "text"} />,
  args: {
    variant: "card",
  },
};
