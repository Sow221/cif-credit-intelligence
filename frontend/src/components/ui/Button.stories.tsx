import type { Meta, StoryObj } from "@storybook/react";
import { Check, Plus, Trash2 } from "lucide-react";
import { Button } from "./Button";

const meta = {
  title: "ui/Button",
  component: Button,
  args: {
    children: "Approuver",
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {};

export const Secondary: Story = {
  args: {
    variant: "secondary",
    children: "Déroger",
  },
};

export const Danger: Story = {
  args: {
    variant: "danger",
    children: "Rejeter",
  },
};

export const Ghost: Story = {
  args: {
    variant: "ghost",
    children: "Annuler",
  },
};

export const IconButton: Story = {
  args: {
    variant: "icon",
    children: <Check aria-hidden className="h-4 w-4" />,
    "aria-label": "Valider",
  },
};

export const WithLeftIcon: Story = {
  args: {
    leftIcon: <Plus aria-hidden className="h-4 w-4" />,
    children: "Nouvelle demande",
  },
};

export const Loading: Story = {
  args: {
    loading: true,
    children: "Envoi en cours…",
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
    children: "Action indisponible",
    leftIcon: <Trash2 aria-hidden className="h-4 w-4" />,
  },
};
