import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { AuditTimeline } from "./AuditTimeline";
import type { TimelineItemData } from "@/components/ui/Timeline";

const items: TimelineItemData[] = [
  {
    id: "created",
    title: "Client créé",
    subtitle: "par admin",
    timestamp: "01/03/2024",
    type: "info",
  },
];

describe("AuditTimeline", () => {
  it("renders the default title", () => {
    render(<AuditTimeline items={items} />);
    expect(screen.getByText("Audit")).toBeInTheDocument();
  });

  it("renders a custom title", () => {
    render(<AuditTimeline items={items} title="Journal" />);
    expect(screen.getByText("Journal")).toBeInTheDocument();
  });

  it("renders each timeline item with title and timestamp", () => {
    render(<AuditTimeline items={items} />);
    expect(screen.getByText("Client créé")).toBeInTheDocument();
    expect(screen.getByText("par admin")).toBeInTheDocument();
    expect(screen.getByText("01/03/2024")).toBeInTheDocument();
  });

  it("shows the empty message when there are no items", () => {
    render(<AuditTimeline items={[]} />);
    expect(screen.getByText("Aucun événement")).toBeInTheDocument();
  });
});
