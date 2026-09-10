import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Tabs } from "./Tabs";

const tabs = [
  { id: "a", label: "Tab A", content: <p>Content A</p> },
  { id: "b", label: "Tab B", content: <p>Content B</p> },
];

describe("Tabs", () => {
  it("renders all tab buttons", () => {
    render(<Tabs tabs={tabs} />);
    expect(screen.getByRole("tab", { name: "Tab A" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Tab B" })).toBeInTheDocument();
  });

  it("defaults to first tab selected", () => {
    render(<Tabs tabs={tabs} />);
    expect(screen.getByRole("tab", { name: "Tab A" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: "Tab B" })).toHaveAttribute("aria-selected", "false");
  });

  it("shows content of active tab", () => {
    render(<Tabs tabs={tabs} />);
    expect(screen.getByText("Content A")).toBeInTheDocument();
    expect(screen.queryByText("Content B")).not.toBeInTheDocument();
  });

  it("switches tab on click", async () => {
    const user = userEvent.setup();
    render(<Tabs tabs={tabs} />);
    await user.click(screen.getByRole("tab", { name: "Tab B" }));
    expect(screen.getByRole("tab", { name: "Tab B" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText("Content B")).toBeInTheDocument();
    expect(screen.queryByText("Content A")).not.toBeInTheDocument();
  });

  it("calls onChange when a tab is clicked", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Tabs tabs={tabs} onChange={onChange} />);
    await user.click(screen.getByRole("tab", { name: "Tab B" }));
    expect(onChange).toHaveBeenCalledWith("b");
  });

  it("renders badge count when positive", () => {
    const tabsWithBadge = [
      { id: "a", label: "Pending", badge: 3, content: <p>Pending content</p> },
    ];
    render(<Tabs tabs={tabsWithBadge} />);
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("hides badge when zero", () => {
    const tabsWithBadge = [
      { id: "a", label: "Pending", badge: 0, content: <p>Pending content</p> },
    ];
    render(<Tabs tabs={tabsWithBadge} />);
    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("uses controlled activeId", () => {
    render(<Tabs tabs={tabs} activeId="b" />);
    expect(screen.getByRole("tab", { name: "Tab B" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText("Content B")).toBeInTheDocument();
  });

  it("has tabpanel", () => {
    render(<Tabs tabs={tabs} />);
    expect(screen.getByRole("tabpanel")).toBeInTheDocument();
  });
});
