import type { Meta, StoryObj } from "@storybook/react";
import { AuditTimeline } from "./AuditTimeline";

const historyItems = [
  {
    id: "evt-1",
    title: "Dossier créé",
    subtitle: "Agent crédit · C522",
    timestamp: "01 mars 2024, 09:12",
    type: "info" as const,
  },
  {
    id: "evt-2",
    title: "Scoring automatique",
    subtitle: "Modèle gbm-v1",
    timestamp: "01 mars 2024, 09:14",
    type: "neutral" as const,
  },
  {
    id: "evt-3",
    title: "Décision rendue",
    subtitle: "APPROVE",
    timestamp: "03 mars 2024, 14:02",
    type: "success" as const,
  },
];

const meta = {
  title: "shared/AuditTimeline",
  component: AuditTimeline,
  args: {
    items: historyItems,
  },
} satisfies Meta<typeof AuditTimeline>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const CustomTitle: Story = {
  args: {
    title: "Historique du dossier",
  },
};

export const Empty: Story = {
  args: {
    items: [],
  },
};
