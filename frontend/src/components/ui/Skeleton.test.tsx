import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Skeleton, SkeletonList } from "./Skeleton";

describe("Skeleton", () => {
  it("renders an aria-hidden element", () => {
    const { container } = render(<Skeleton />);
    expect(container.firstChild).toHaveAttribute("aria-hidden", "true");
  });

  it("applies default text variant class", () => {
    const { container } = render(<Skeleton />);
    expect(container.firstChild).toHaveClass("h-3");
  });

  it("applies avatar variant class", () => {
    const { container } = render(<Skeleton variant="avatar" />);
    expect(container.firstChild).toHaveClass("rounded-full");
  });

  it("applies custom className", () => {
    const { container } = render(<Skeleton className="extra" />);
    expect(container.firstChild).toHaveClass("extra");
  });
});

describe("SkeletonList", () => {
  it("renders role status with label", () => {
    render(<SkeletonList />);
    expect(screen.getByRole("status", { name: "Chargement..." })).toBeInTheDocument();
  });

  it("renders 5 rows by default", () => {
    const { container } = render(<SkeletonList />);
    const skeletons = container.querySelectorAll("[aria-hidden='true']");
    expect(skeletons.length).toBe(5);
  });

  it("renders custom row count", () => {
    const { container } = render(<SkeletonList rows={3} />);
    const skeletons = container.querySelectorAll("[aria-hidden='true']");
    expect(skeletons.length).toBe(3);
  });
});
