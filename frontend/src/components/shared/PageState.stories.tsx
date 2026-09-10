import type { Meta, StoryObj } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { Button } from "@/components/ui/Button";
import { PageState } from "./PageState";

const meta = {
  title: "shared/PageState",
  component: PageState,
  args: {
    children: (
      <p className="text-body text-primary-700">
        Contenu du page réussi : liste des demandes à jour.
      </p>
    ),
  },
} satisfies Meta<typeof PageState>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Success: Story = {
  args: {
    status: "success",
  },
};

export const Loading: Story = {
  args: {
    status: "loading",
  },
};

export const Error: Story = {
  args: {
    status: "error",
    error: "Impossible de joindre le service de scoring.",
    onRetry: action("Réessayer"),
  },
};

export const Forbidden: Story = {
  args: {
    status: "forbidden",
  },
};

export const Empty: Story = {
  args: {
    status: "idle",
    defaultEmptyTitle: "Aucune demande",
    defaultEmptyDescription: "Créez votre première demande pour démarrer.",
  },
};

export const CustomEmptyState: Story = {
  args: {
    status: "success",
    emptyState: <Button>Commencer la revue</Button>,
  },
};
