import type { Meta, StoryObj } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { SearchBar } from "./SearchBar";

const meta = {
  title: "ui/SearchBar",
  component: SearchBar,
  args: {
    onChange: action("Rechercher"),
    ariaLabel: "Rechercher un client",
  },
} satisfies Meta<typeof SearchBar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Empty: Story = {
  args: {
    value: "",
    placeholder: "Rechercher un client…",
  },
};

export const WithValue: Story = {
  args: {
    value: "Awa Diallo",
    placeholder: "Rechercher un client…",
  },
};

export const CustomPlaceholder: Story = {
  args: {
    value: "",
    placeholder: "Rechercher une demande par ID…",
  },
};
