import type { Meta, StoryObj } from "@storybook/react";
import { userEvent, within } from "@storybook/test";
import { Download, MoreVertical } from "lucide-react";
import { Dropdown } from "./Dropdown";

const meta = {
  title: "ui/Dropdown",
  component: Dropdown,
  args: {
    trigger: <MoreVertical aria-hidden className="h-5 w-5" />,
    ariaLabel: "Actions du dossier",
    items: [
      { label: "Voir le détail" },
      { label: "Exporter" },
      { label: "Archiver", danger: true },
    ],
  },
} satisfies Meta<typeof Dropdown>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Closed: Story = {};

export const RightAligned: Story = {
  args: {
    align: "right",
  },
};

export const WithIcons: Story = {
  args: {
    items: [
      { label: "Voir le détail", icon: <Download aria-hidden className="h-4 w-4" /> },
      { label: "Exporter", icon: <Download aria-hidden className="h-4 w-4" /> },
      { label: "Archiver", icon: <Download aria-hidden className="h-4 w-4" />, danger: true },
    ],
  },
};

export const Open: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("button"));
  },
};
