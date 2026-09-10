import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Select } from "./Select";

const options = [
  { value: "A", label: "Alpha" },
  { value: "B", label: "Beta" },
];

describe("Select", () => {
  it("renders a select element", () => {
    render(<Select options={options} />);
    expect(screen.getByRole("combobox")).toBeInTheDocument();
  });

  it("renders all options", () => {
    render(<Select options={options} />);
    expect(screen.getByRole("option", { name: "Alpha" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Beta" })).toBeInTheDocument();
  });

  it("renders label and links via htmlFor", () => {
    render(<Select label="Product" options={options} />);
    const label = screen.getByText("Product");
    const select = screen.getByRole("combobox");
    expect(label).toHaveAttribute("for", select.id);
  });

  it("renders placeholder option when provided", () => {
    render(<Select options={options} placeholder="Select..." />);
    expect(screen.getByRole("option", { name: "Select..." })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Select..." })).toHaveAttribute("disabled");
  });

  it("renders error with role alert", () => {
    render(<Select options={options} error="Required" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Required");
  });

  it("sets aria-invalid when error is present", () => {
    render(<Select options={options} error="Bad" />);
    expect(screen.getByRole("combobox")).toHaveAttribute("aria-invalid", "true");
  });

  it("renders helper when no error", () => {
    render(<Select options={options} helper="Choose one" />);
    expect(screen.getByText("Choose one")).toBeInTheDocument();
  });

  it("forwards ref", () => {
    const ref = { current: null };
    render(<Select ref={ref as React.RefObject<HTMLSelectElement>} options={options} />);
    expect(ref.current).toBeInstanceOf(HTMLSelectElement);
  });
});
