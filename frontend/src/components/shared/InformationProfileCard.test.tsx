import { beforeEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import i18n from "@/locales";
import { InformationProfileCard } from "./InformationProfileCard";
import type { InformationProfileCardData } from "@/types/information";

const profile: InformationProfileCardData = {
  state: "FULL_FILE",
  score: 85,
  version: 2,
  depths: { IDENTITY: true, FULL: true, EXTENDED: false, UNKNOWN: true },
  gaps: [],
  updated_at: "2024-03-01T10:00:00Z",
};

describe("InformationProfileCard", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
  });

  it("renders the card title", () => {
    render(<InformationProfileCard profile={profile} />);
    expect(screen.getByText("Information Profile")).toBeInTheDocument();
  });

  it("shows the state badge", () => {
    render(<InformationProfileCard profile={profile} />);
    expect(screen.getByText("Complet")).toBeInTheDocument();
  });

  it("shows version and normalized score", () => {
    render(<InformationProfileCard profile={profile} />);
    expect(screen.getByText("v2 · 85")).toBeInTheDocument();
  });

  it("omits the score when it is not a number", () => {
    render(
      <InformationProfileCard profile={{ ...profile, score: undefined as unknown as number }} />,
    );
    expect(screen.getByText("v2")).toBeInTheDocument();
  });

  it("renders a progress bar for every depth label", () => {
    render(<InformationProfileCard profile={profile} />);
    for (const depth of ["IDENTITY", "FULL", "EXTENDED", "UNKNOWN"]) {
      expect(screen.getByText(depth)).toBeInTheDocument();
    }
    expect(screen.getAllByRole("progressbar")).toHaveLength(4);
  });

  it("renders the updated_at timestamp when present", () => {
    render(<InformationProfileCard profile={profile} />);
    expect(screen.getByText("2024-03-01T10:00:00Z")).toBeInTheDocument();
  });

  it("does not render a timestamp when updated_at is missing", () => {
    render(<InformationProfileCard profile={{ ...profile, updated_at: undefined }} />);
    expect(screen.queryByText("2024-03-01T10:00:00Z")).not.toBeInTheDocument();
  });
});
