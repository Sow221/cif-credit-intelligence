import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Dropdown } from "./Dropdown";

describe("Dropdown", () => {
  it("renders the trigger", () => {
    render(<Dropdown trigger={<button>Open</button>} items={[{ label: "Item 1" }]} />);
    expect(screen.getByRole("button", { name: "Open", expanded: false })).toBeInTheDocument();
  });

  it("shows menu on trigger click", () => {
    render(<Dropdown trigger={<button>Open</button>} items={[{ label: "Item 1" }]} />);
    fireEvent.click(screen.getByRole("button", { name: "Open", expanded: false }));
    expect(screen.getByRole("menu")).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "Item 1" })).toBeInTheDocument();
  });

  it("hides menu on item click and calls onSelect", () => {
    const onSelect = vi.fn();
    render(<Dropdown trigger={<button>Open</button>} items={[{ label: "Action", onSelect }]} />);
    fireEvent.click(screen.getByRole("button", { name: "Open", expanded: false }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Action" }));
    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();
  });

  it("hides menu on escape key", () => {
    render(<Dropdown trigger={<button>Open</button>} items={[{ label: "Item 1" }]} />);
    fireEvent.click(screen.getByRole("button", { name: "Open", expanded: false }));
    expect(screen.getByRole("menu")).toBeInTheDocument();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();
  });

  it("hides menu on outside click", () => {
    render(
      <div>
        <p>Outside</p>
        <Dropdown trigger={<button>Open</button>} items={[{ label: "Item 1" }]} />
      </div>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Open", expanded: false }));
    expect(screen.getByRole("menu")).toBeInTheDocument();
    fireEvent.mouseDown(screen.getByText("Outside"));
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();
  });

  it("applies danger class to danger items", () => {
    render(
      <Dropdown trigger={<button>Open</button>} items={[{ label: "Delete", danger: true }]} />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Open", expanded: false }));
    expect(screen.getByRole("menuitem", { name: "Delete" }).className).toContain("text-danger-600");
  });

  it("passes ariaLabel to trigger button", () => {
    render(
      <Dropdown
        trigger={<button>Open</button>}
        items={[{ label: "Item 1" }]}
        ariaLabel="Options menu"
      />,
    );
    expect(screen.getByRole("button", { name: "Options menu" })).toBeInTheDocument();
  });
});
