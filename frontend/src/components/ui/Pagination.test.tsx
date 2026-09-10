import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Pagination } from "./Pagination";

describe("Pagination", () => {
  it("renders total count", () => {
    render(
      <Pagination
        page={1}
        pageSize={10}
        total={25}
        onPageChange={vi.fn()}
        onPageSizeChange={vi.fn()}
      />,
    );
    expect(screen.getByText((_, element) => element?.textContent === "25 · ")).toBeInTheDocument();
  });

  it("renders page buttons", () => {
    render(
      <Pagination
        page={1}
        pageSize={10}
        total={25}
        onPageChange={vi.fn()}
        onPageSizeChange={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Page 1" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Page 2" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Page 3" })).toBeInTheDocument();
  });

  it("marks current page with aria-current", () => {
    render(
      <Pagination
        page={2}
        pageSize={10}
        total={25}
        onPageChange={vi.fn()}
        onPageSizeChange={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Page 2" })).toHaveAttribute("aria-current", "page");
  });

  it("disables previous button on first page", () => {
    render(
      <Pagination
        page={1}
        pageSize={10}
        total={25}
        onPageChange={vi.fn()}
        onPageSizeChange={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Page précédente" })).toBeDisabled();
  });

  it("disables next button on last page", () => {
    render(
      <Pagination
        page={3}
        pageSize={10}
        total={25}
        onPageChange={vi.fn()}
        onPageSizeChange={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Page suivante" })).toBeDisabled();
  });

  it("calls onPageChange when a page button is clicked", async () => {
    const user = userEvent.setup();
    const onPageChange = vi.fn();
    render(
      <Pagination
        page={1}
        pageSize={10}
        total={25}
        onPageChange={onPageChange}
        onPageSizeChange={vi.fn()}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Page 2" }));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it("calls onPageSizeChange when select changes", async () => {
    const user = userEvent.setup();
    const onPageSizeChange = vi.fn();
    render(
      <Pagination
        page={1}
        pageSize={10}
        total={25}
        onPageChange={vi.fn()}
        onPageSizeChange={onPageSizeChange}
      />,
    );
    await user.selectOptions(screen.getByRole("combobox", { name: "Taille de page" }), "25");
    expect(onPageSizeChange).toHaveBeenCalledWith(25);
  });
});
