import type { Meta, StoryObj } from "@storybook/react";
import { Input } from "./Input";

const meta = {
  title: "ui/Input",
  component: Input,
  args: {
    label: "Nom du client",
    placeholder: "Ex. Awa Diallo",
  },
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithValue: Story = {
  args: {
    value: "Awa Diallo",
  },
};

export const WithHelper: Story = {
  args: {
    helper: "Saisissez le nom complet tel qu'à l'état civil.",
  },
};

export const WithError: Story = {
  args: {
    value: "Awa",
    error: "Le nom doit comporter au moins 3 caractères.",
  },
};

export const Disabled: Story = {
  args: {
    value: "Awa Diallo",
    disabled: true,
  },
};
