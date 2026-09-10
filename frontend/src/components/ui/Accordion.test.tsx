import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Accordion, AccordionItem } from "./Accordion";

describe("AccordionItem", () => {
  it("renders the title", () => {
    render(
      <AccordionItem title="Section 1">
        <p>Content 1</p>
      </AccordionItem>,
    );
    expect(screen.getByText("Section 1")).toBeInTheDocument();
  });

  it("does not render children when closed by default", () => {
    render(
      <AccordionItem title="Section 1">
        <p>Content 1</p>
      </AccordionItem>,
    );
    expect(screen.queryByText("Content 1")).not.toBeInTheDocument();
  });

  it("renders children when defaultOpen is true", () => {
    render(
      <AccordionItem title="Section 1" defaultOpen>
        <p>Content 1</p>
      </AccordionItem>,
    );
    expect(screen.getByText("Content 1")).toBeInTheDocument();
  });

  it("toggles children on click", () => {
    render(
      <AccordionItem title="Section 1">
        <p>Content 1</p>
      </AccordionItem>,
    );
    const button = screen.getByRole("button", { expanded: false });
    expect(screen.queryByText("Content 1")).not.toBeInTheDocument();

    fireEvent.click(button);
    expect(screen.getByText("Content 1")).toBeInTheDocument();
    expect(button).toHaveAttribute("aria-expanded", "true");

    fireEvent.click(button);
    expect(screen.queryByText("Content 1")).not.toBeInTheDocument();
    expect(button).toHaveAttribute("aria-expanded", "false");
  });
});

describe("Accordion", () => {
  it("renders all items", () => {
    render(
      <Accordion
        items={[
          { title: "First", content: <p>First content</p> },
          { title: "Second", content: <p>Second content</p> },
        ]}
      />,
    );
    expect(screen.getByText("First")).toBeInTheDocument();
    expect(screen.getByText("Second")).toBeInTheDocument();
  });

  it("supports defaultOpen on individual items", () => {
    render(
      <Accordion
        items={[
          { title: "Closed", content: <p>Closed content</p> },
          { title: "Open", content: <p>Open content</p>, defaultOpen: true },
        ]}
      />,
    );
    expect(screen.queryByText("Closed content")).not.toBeInTheDocument();
    expect(screen.getByText("Open content")).toBeInTheDocument();
  });
});
