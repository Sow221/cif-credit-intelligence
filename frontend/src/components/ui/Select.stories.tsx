import type { Meta, StoryObj } from "@storybook/react";
import { Select } from "./Select";

const meta = {
  title: "ui/Select",
  component: Select,
  args: {
    label: "Produit",
    options: [
      { value: "SMALL_BUSINESS", label: "Petit commerce" },
      { value: "PERSONAL", label: "Personnel" },
      { value: "AGRICULTURE", label: "Agriculture" },
      { value: "MICRO_FINANCE", label: "Microfinance" },
    ],
  },
} satisfies Meta<typeof Select>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    value: "SMALL_BUSINESS",
  },
};

export const WithPlaceholder: Story = {
  args: {
    value: "",
    placeholder: "Sélectionnez un produit",
  },
};

export const WithError: Story = {
  args: {
    value: "",
    error: "Le produit est obligatoire.",
  },
};

export const WithHelper: Story = {
  args: {
    value: "PERSONAL",
    helper: "Le produit détermine la grille de scoring appliquée.",
  },
};

export const Disabled: Story = {
  args: {
    value: "AGRICULTURE",
    disabled: true,
  },
};
