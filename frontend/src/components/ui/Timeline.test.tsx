import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Timeline } from "./Timeline";
import type { TimelineItemData } from "./Timeline";

const items: TimelineItemData[] = [
  {
    id: "1",
    title: "Event 1",
    subtitle: "First event",
    timestamp: "2024-03-01 10:00",
    type: "success",
  },
  { id: "2", title: "Event 2", timestamp: "2024-03-02 12:00", type: "warning" },
];

describe("Timeline", () => {
  it("renders empty message when no items", () => {
    render(<Timeline items={[]} />);
    expect(screen.getByText("Aucun \u00e9v\u00e9nement")).toBeInTheDocument();
  });

  it("renders all items", () => {
    render(<Timeline items={items} />);
    expect(screen.getByText("Event 1")).toBeInTheDocument();
    expect(screen.getByText("Event 2")).toBeInTheDocument();
  });

  it("renders subtitle when present", () => {
    render(<Timeline items={items} />);
    expect(screen.getByText("First event")).toBeInTheDocument();
  });

  it("does not render subtitle when absent", () => {
    render(<Timeline items={items} />);
    const event2Li = screen.getByText("Event 2").closest("li");
    const event2Paragraphs = event2Li!.querySelectorAll("p");
    expect(event2Paragraphs.length).toBe(2);
    expect(event2Paragraphs[0]).toHaveTextContent("Event 2");
    expect(event2Paragraphs[1]).toHaveTextContent("2024-03-02 12:00");
  });

  it("renders timestamp", () => {
    render(<Timeline items={items} />);
    expect(screen.getByText("2024-03-01 10:00")).toBeInTheDocument();
    expect(screen.getByText("2024-03-02 12:00")).toBeInTheDocument();
  });

  it("uses neutral type by default", () => {
    const neutralItems: TimelineItemData[] = [
      { id: "1", title: "Neutral", timestamp: "2024-03-01" },
    ];
    const { container } = render(<Timeline items={neutralItems} />);
    const dot = container.querySelector("[aria-hidden]");
    expect(dot).toHaveClass("bg-primary-400");
  });

  it("renders as ordered list", () => {
    render(<Timeline items={items} />);
    expect(screen.getByRole("list")).toBeInTheDocument();
  });
});
