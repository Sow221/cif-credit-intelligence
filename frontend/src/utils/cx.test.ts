import { describe, expect, it } from "vitest";
import { cx } from "./cx";

describe("cx", () => {
  it("joins truthy values", () => {
    expect(cx("a", "b")).toBe("a b");
  });

  it("filters falsy values", () => {
    expect(cx("a", false, null, undefined, "")).toBe("a");
  });

  it("returns empty string with no values", () => {
    expect(cx()).toBe("");
    expect(cx(false, null)).toBe("");
  });
});