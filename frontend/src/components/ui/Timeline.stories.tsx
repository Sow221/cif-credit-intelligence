import type { Meta, StoryObj } from "@storybook/react";
import { Timeline } from "./Timeline";

const mixedItems = [
  {
    id: "1",
    title: "Demande soumise",
    subtitle: "Awa Diallo",
    timestamp: "01 mars 2024",
    type: "info" as const,
  },
  {
    id: "2",
    title: "Scoring terminé",
    subtitle: "Modèle gbm-v1",
    timestamp: "01 mars 2024",
    type: "neutral" as const,
  },
  {
    id: "3",
    title: "Revue manuelle requise",
    subtitle: "Données incomplètes",
    timestamp: "02 mars 2024",
    type: "warning" as const,
  },
  {
    id: "4",
    title: "Approuvée",
    subtitle: "Décision finale",
    timestamp: "03 mars 2024",
    type: "success" as const,
  },
];

const meta = {
  title: "ui/Timeline",
  component: Timeline,
  args: {
    items: mixedItems,
  },
} satisfies Meta<typeof Timeline>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Mixed: Story = {};

export const AllSuccess: Story = {
  args: {
    items: mixedItems.map((item) => ({ ...item, type: "success" as const })),
  },
};

export const WithDanger: Story = {
  args: {
    items: [
      { id: "1", title: "Demande soumise", timestamp: "01 mars 2024", type: "info" },
      {
        id: "2",
        title: "Refusée",
        subtitle: "Risque élevé",
        timestamp: "02 mars 2024",
        type: "danger",
      },
    ],
  },
};

export const SingleItem: Story = {
  args: {
    items: [{ id: "1", title: "Dossier créé", timestamp: "29 févr. 2024", type: "neutral" }],
  },
};

export const Empty: Story = {
  args: {
    items: [],
  },
};
