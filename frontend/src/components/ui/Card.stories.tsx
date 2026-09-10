import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "./Badge";
import { Button } from "./Button";
import { Card } from "./Card";

const meta = {
  title: "ui/Card",
  component: Card,
  args: {
    title: "Résumé du dossier",
    subtitle: "Awa Diallo · Petit commerce",
    children: (
      <p className="text-body text-primary-700">
        Montant demandé : 500 000 FCFA sur 12 mois, à risque faible.
      </p>
    ),
  },
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithActions: Story = {
  args: {
    actions: (
      <div className="flex items-center gap-2">
        <Badge variant="success">Éligible</Badge>
        <Button variant="ghost">Détail</Button>
      </div>
    ),
  },
};

export const WithoutTitle: Story = {
  args: {
    title: undefined,
    subtitle: undefined,
    children: (
      <div className="flex items-center justify-between">
        <span className="text-body text-primary-900">Contenu autonome</span>
        <Badge variant="info">Soumise</Badge>
      </div>
    ),
  },
};

export const Unpadded: Story = {
  args: {
    padded: false,
    children: (
      <div className="p-4 text-body text-primary-500">
        Paragraphe qui contrôle son propre espacement.
      </div>
    ),
  },
};
