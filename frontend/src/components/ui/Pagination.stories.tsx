import type { Meta, StoryObj } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { Pagination } from "./Pagination";

const meta = {
  title: "ui/Pagination",
  component: Pagination,
  args: {
    pageSize: 10,
    onPageChange: action("Changer de page"),
    onPageSizeChange: action("Changer la taille"),
  },
} satisfies Meta<typeof Pagination>;

export default meta;
type Story = StoryObj<typeof meta>;

export const FirstPage: Story = {
  args: {
    page: 1,
    total: 137,
  },
};

export const MiddlePage: Story = {
  args: {
    page: 5,
    total: 100,
  },
};

export const LastPage: Story = {
  args: {
    page: 10,
    total: 100,
  },
};

export const SinglePage: Story = {
  args: {
    page: 1,
    total: 8,
  },
};
