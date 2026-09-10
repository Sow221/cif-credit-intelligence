import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "./Badge";
import { Tabs } from "./Tabs";

const meta = {
  title: "ui/Tabs",
  component: Tabs,
  args: {
    ariaLabel: "Sections du dossier",
    tabs: [
      {
        id: "overview",
        label: "Vue d'ensemble",
        content: (
          <p className="text-body text-primary-700">
            Résumé du dossier : client, montant et statut.
          </p>
        ),
      },
      {
        id: "risk",
        label: "Risque",
        content: (
          <p className="text-body text-primary-700">
            Score, bande de risque et intervalle de confiance.
          </p>
        ),
      },
      {
        id: "documents",
        label: "Documents",
        content: (
          <p className="text-body text-primary-700">
            Pièces justificatives fournies par le client.
          </p>
        ),
      },
    ],
  },
} satisfies Meta<typeof Tabs>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithoutActiveTab: Story = {
  args: {
    activeId: undefined,
  },
};

export const WithBadges: Story = {
  args: {
    tabs: [
      { id: "all", label: "Toutes", badge: 12, content: <p>12 dossiers.</p> },
      { id: "pending", label: "En attente", badge: 3, content: <p>3 dossiers en attente.</p> },
      { id: "done", label: "Traités", badge: 9, content: <p>9 dossiers traités.</p> },
    ],
  },
};

export const ContentAsComponent: Story = {
  args: {
    tabs: [
      {
        id: "review",
        label: "Revue",
        content: (
          <div className="flex items-center gap-2">
            <Badge variant="warning">En revue</Badge>
            <span className="text-body-sm text-primary-500">Décision recommandée : APPROVE</span>
          </div>
        ),
      },
    ],
  },
};
