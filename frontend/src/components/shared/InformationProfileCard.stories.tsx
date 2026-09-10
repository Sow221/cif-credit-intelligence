import type { Meta, StoryObj } from "@storybook/react";
import { InformationProfileCard } from "./InformationProfileCard";
import type { InformationProfileCardData } from "@/types/information";

const base: InformationProfileCardData = {
  state: "FULL_FILE",
  score: 85,
  version: 2,
  depths: { IDENTITY: true, FULL: true, EXTENDED: false, UNKNOWN: true },
  gaps: [],
  updated_at: "2024-03-01T10:00:00Z",
};

const meta = {
  title: "shared/InformationProfileCard",
  component: InformationProfileCard,
  args: {
    profile: base,
  },
} satisfies Meta<typeof InformationProfileCard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const FullFile: Story = {};

export const ThinFile: Story = {
  args: {
    profile: {
      ...base,
      state: "THIN_FILE",
      score: 45,
      depths: { IDENTITY: true, FULL: false, EXTENDED: false, UNKNOWN: true },
    },
  },
};

export const DataPoor: Story = {
  args: {
    profile: {
      state: "DATA_POOR",
      score: 18,
      version: 1,
      depths: { IDENTITY: true, FULL: false, EXTENDED: false, UNKNOWN: false },
      gaps: [],
    },
  },
};

export const WithoutTimestamp: Story = {
  args: {
    profile: { ...base, updated_at: undefined },
  },
};
