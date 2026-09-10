import type { Meta, StoryObj } from "@storybook/react";
import { FileSearch } from "lucide-react";
import { Button } from "./Button";
import { EmptyState } from "./EmptyState";

const meta = {
  title: "ui/EmptyState",
  component: EmptyState,
  args: {
    title: "Aucune demande",
    description: "Aucune demande ne correspond à vos critères pour le moment.",
  },
} satisfies Meta<typeof EmptyState>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithAction: Story = {
  args: {
    action: <Button>Nouvelle demande</Button>,
  },
};

export const WithCustomIcon: Story = {
  args: {
    icon: <FileSearch className="h-10 w-10" />,
    title: "Aucun résultat de recherche",
  },
};

export const Minimal: Story = {
  args: {
    description: undefined,
  },
};
