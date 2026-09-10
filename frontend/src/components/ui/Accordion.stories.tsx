import type { Meta, StoryObj } from "@storybook/react";
import { Accordion } from "./Accordion";

const meta = {
  title: "ui/Accordion",
  component: Accordion,
  args: {
    items: [
      {
        title: "Qu'est-ce que le crédit adaptatif ?",
        content:
          "Le crédit adaptatif ajuste les conditions de financement en fonction du profil de risque et de la qualité des données du demandeur.",
      },
      {
        title: "Comment la décision est-elle rendue ?",
        content:
          "Un modèle de scoring estime la probabilité de défaut, puis une politique de décision valide ou propose une revue manuelle du dossier.",
      },
    ],
  },
} satisfies Meta<typeof Accordion>;

export default meta;
type Story = StoryObj<typeof meta>;

export const AllClosed: Story = {};

export const FirstOpen: Story = {
  args: {
    items: [
      {
        title: "Que se passe-t-il après la décision ?",
        content: "Le dossier est archivé et les indicateurs de monitoring sont mis à jour.",
        defaultOpen: true,
      },
    ],
  },
};

export const SingleItem: Story = {
  args: {
    items: [
      {
        title: "Politique de crédit v3",
        content:
          "La grille de décision intègre les bandes de risque, la qualité d'information et les règles de dérogation.",
      },
    ],
  },
};
