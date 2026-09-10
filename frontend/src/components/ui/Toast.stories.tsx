import type { Meta, StoryObj } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { ToastContainer, ToastView } from "./Toast";

const meta = {
  title: "ui/Toast",
  component: ToastView,
  args: {
    variant: "success",
    message: "Demande créée avec succès.",
  },
} satisfies Meta<typeof ToastView>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Success: Story = {
  args: {
    variant: "success",
  },
};

export const Error: Story = {
  args: {
    variant: "error",
    message: "Impossible d'enregistrer la décision.",
  },
};

export const Warning: Story = {
  args: {
    variant: "warning",
    message: "Le dossier présente un risque élevé.",
  },
};

export const Info: Story = {
  args: {
    variant: "info",
    message: "Un examen manuel vous est assigné.",
  },
};

export const Container: Story = {
  render: () => (
    <ToastContainer
      toasts={[
        { id: "1", variant: "success", message: "Approbation enregistrée." },
        { id: "2", variant: "warning", message: "Données partiellement manquantes." },
        { id: "3", variant: "error", message: "Connexion au service perdue." },
      ]}
      onDismiss={action("Fermer le toast")}
    />
  ),
};
