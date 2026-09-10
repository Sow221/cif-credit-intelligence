import type { Meta, StoryObj } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { ErrorState } from "./ErrorState";

const meta = {
  title: "ui/ErrorState",
  component: ErrorState,
} satisfies Meta<typeof ErrorState>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithRetry: Story = {
  args: {
    onRetry: action("Réessayer"),
  },
};

export const CustomMessages: Story = {
  args: {
    title: "Connexion impossible",
    description:
      "Le service est temporairement indisponible. Veuillez réessayer dans quelques minutes.",
    retryLabel: "Réessayer plus tard",
    onRetry: action("Réessayer"),
  },
};
