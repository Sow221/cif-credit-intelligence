import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Modal } from "./Modal";

describe("Modal", () => {
  it("renders nothing when closed", () => {
    render(<Modal open={false} onClose={vi.fn()} title="Dialog" />);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders dialog when open", () => {
    render(<Modal open={true} onClose={vi.fn()} title="My Dialog" />);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("My Dialog")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<Modal open={true} onClose={vi.fn()} title="Title" description="Desc" />);
    expect(screen.getByText("Desc")).toBeInTheDocument();
  });

  it("renders children inside the dialog", () => {
    render(
      <Modal open={true} onClose={vi.fn()} title="Title">
        <p>Body content</p>
      </Modal>,
    );
    expect(screen.getByText("Body content")).toBeInTheDocument();
  });

  it("renders footer when provided", () => {
    render(<Modal open={true} onClose={vi.fn()} title="Title" footer={<button>Save</button>} />);
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument();
  });

  it("calls onClose on close button click", () => {
    const onClose = vi.fn();
    render(<Modal open={true} onClose={onClose} title="Title" />);
    fireEvent.click(screen.getByRole("button", { name: "Fermer" }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose on escape key", () => {
    const onClose = vi.fn();
    render(<Modal open={true} onClose={onClose} title="Title" />);
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose on backdrop click", () => {
    const onClose = vi.fn();
    render(<Modal open={true} onClose={onClose} title="Title" />);
    fireEvent.click(screen.getByText("Title").closest("[role='dialog']")!.previousElementSibling!);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("has aria-modal", () => {
    render(<Modal open={true} onClose={vi.fn()} title="Title" />);
    expect(screen.getByRole("dialog")).toHaveAttribute("aria-modal", "true");
  });
});
