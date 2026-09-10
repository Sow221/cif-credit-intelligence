import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SearchBar } from "./SearchBar";

describe("SearchBar", () => {
  it("renders search input with role searchbox", () => {
    render(<SearchBar value="" onChange={vi.fn()} />);
    expect(screen.getByRole("searchbox")).toBeInTheDocument();
  });

  it("displays the current value", () => {
    render(<SearchBar value="hello" onChange={vi.fn()} />);
    expect(screen.getByRole("searchbox")).toHaveValue("hello");
  });

  it("calls onChange when typing", () => {
    const onChange = vi.fn();
    render(<SearchBar value="" onChange={onChange} />);
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "test" } });
    expect(onChange).toHaveBeenCalledWith("test");
  });

  it("renders placeholder", () => {
    render(<SearchBar value="" onChange={vi.fn()} placeholder="Search clients..." />);
    expect(screen.getByPlaceholderText("Search clients...")).toBeInTheDocument();
  });

  it("shows clear button when value is non-empty", () => {
    render(<SearchBar value="query" onChange={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Effacer" })).toBeInTheDocument();
  });

  it("hides clear button when value is empty", () => {
    render(<SearchBar value="" onChange={vi.fn()} />);
    expect(screen.queryByRole("button", { name: "Effacer" })).not.toBeInTheDocument();
  });

  it("clears value when clear button clicked", () => {
    const onChange = vi.fn();
    render(<SearchBar value="query" onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: "Effacer" }));
    expect(onChange).toHaveBeenCalledWith("");
  });

  it("passes ariaLabel to input", () => {
    render(<SearchBar value="" onChange={vi.fn()} ariaLabel="Search" />);
    expect(screen.getByRole("searchbox", { name: "Search" })).toBeInTheDocument();
  });
});
