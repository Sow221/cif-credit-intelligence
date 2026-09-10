import type { Meta, StoryObj } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { Button } from "./Button";
import { Modal } from "./Modal";

const meta = {
  title: "ui/Modal",
  component: Modal,
  args: {
    open: true,
    onClose: action("Fermer"),
    title: "Confirmer l'approbation ?",
    description: "La demande sera approuvée et le dossier sera décidé.",
    children: (
      <p className="text-body text-primary-700">
        Cette action est irréversible. Vérifiez les informations du dossier avant de confirmer.
      </p>
    ),
  },
} satisfies Meta<typeof Modal>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithFooter: Story = {
  args: {
    footer: (
      <>
        <Button variant="secondary" onClick={action("Annuler")}>
          Annuler
        </Button>
        <Button onClick={action("Confirmer")}>Confirmer</Button>
      </>
    ),
  },
};

export const Small: Story = {
  args: {
    size: "sm",
    title: "Supprimer le dossier ?",
    children: <p className="text-body text-primary-700">Les données seront supprimées.</p>,
  },
};

export const Large: Story = {
  args: {
    size: "lg",
    title: "Revue complète du dossier",
    children: (
      <div className="flex flex-col gap-3 text-body text-primary-700">
        <p>Informations client, historique de crédit, score modèle et recommandation.</p>
        <p>Le tableau de décision complet s'affiche ici.</p>
      </div>
    ),
  },
};

export const Closed: Story = {
  args: {
    open: false,
  },
};
