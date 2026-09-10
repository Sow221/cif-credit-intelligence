import { describe, expect, it } from "vitest";
import {
  validateAmount,
  validateEmail,
  validateLogin,
  validateNewApplication,
  validateOverride,
  validatePhone,
  validateRequired,
  validateTerm,
} from "./validation";

describe("validateEmail", () => {
  it("accepts valid emails", () => {
    expect(validateEmail("awa@example.com")).toBe(true);
  });

  it("rejects invalid emails", () => {
    expect(validateEmail("not-an-email")).toBe(false);
    expect(validateEmail("")).toBe(false);
  });
});

describe("validatePhone", () => {
  it("accepts plain and prefixed numbers", () => {
    expect(validatePhone("771234567")).toBe(true);
    expect(validatePhone("+221771234567")).toBe(true);
  });

  it("rejects short or non-numeric values", () => {
    expect(validatePhone("123")).toBe(false);
    expect(validatePhone("abc")).toBe(false);
  });
});

describe("validateAmount / validateTerm / validateRequired", () => {
  it("validates amount positivity", () => {
    expect(validateAmount(100)).toBe(true);
    expect(validateAmount(0)).toBe(false);
    expect(validateAmount(-1)).toBe(false);
    expect(validateAmount(Number.NaN)).toBe(false);
  });

  it("validates allowed terms", () => {
    expect(validateTerm(6)).toBe(true);
    expect(validateTerm(12)).toBe(true);
    expect(validateTerm(18)).toBe(true);
    expect(validateTerm(24)).toBe(true);
    expect(validateTerm(7)).toBe(false);
    expect(validateTerm(0)).toBe(false);
  });

  it("validates required values", () => {
    expect(validateRequired("x")).toBe(true);
    expect(validateRequired(0)).toBe(true);
    expect(validateRequired("")).toBe(false);
    expect(validateRequired("   ")).toBe(false);
    expect(validateRequired(null)).toBe(false);
    expect(validateRequired(undefined)).toBe(false);
  });
});

describe("validateLogin", () => {
  it("is valid with both fields", () => {
    expect(validateLogin({ username: "awa", password: "secret" }).valid).toBe(true);
  });

  it("reports missing username", () => {
    const result = validateLogin({ username: "", password: "secret" });
    expect(result.valid).toBe(false);
    expect(result.errors).toEqual([
      { field: "username", message: "common.errors.required" },
    ]);
  });

  it("reports missing password", () => {
    const result = validateLogin({ username: "awa", password: "" });
    expect(result.valid).toBe(false);
    expect(result.errors[0]?.field).toBe("password");
  });
});

describe("validateNewApplication", () => {
  const valid = {
    client_id: "c1",
    product_id: "SMALL_BUSINESS",
    requested_amount: 100000,
    requested_term: 12,
  };

  it("is valid for a complete application", () => {
    expect(validateNewApplication(valid).valid).toBe(true);
  });

  it("reports missing client and product", () => {
    const result = validateNewApplication({ ...valid, client_id: "", product_id: "" });
    expect(result.valid).toBe(false);
    expect(result.errors.map((e) => e.field)).toEqual(["client_id", "product_id"]);
  });

  it("reports invalid amount", () => {
    const result = validateNewApplication({ ...valid, requested_amount: 0 });
    expect(result.errors.some((e) => e.field === "requested_amount")).toBe(true);
  });

  it("reports invalid term", () => {
    const result = validateNewApplication({ ...valid, requested_term: 7 });
    expect(result.errors.some((e) => e.field === "requested_term")).toBe(true);
  });
});

describe("validateOverride", () => {
  const valid = { final_decision: "APPROVE" as const, override_reason: "Because" };

  it("is valid with decision and reason", () => {
    expect(validateOverride(valid).valid).toBe(true);
  });

  it("reports missing reason", () => {
    const result = validateOverride({ ...valid, override_reason: "" });
    expect(result.valid).toBe(false);
    expect(result.errors[0]?.field).toBe("override_reason");
  });

  it("reports invalid final decision", () => {
    const result = validateOverride({
      final_decision: "REJECT" as never,
      override_reason: "Because",
    });
    expect(result.valid).toBe(false);
    expect(result.errors[0]?.field).toBe("final_decision");
  });
});