import { describe, expect, it } from "vitest";
import {
  clamp,
  formatCurrency,
  formatDate,
  formatDateTime,
  formatNumber,
  formatPercent,
  formatRelativeTime,
  formatUuid,
} from "./format";

function spaces(value: string): string {
  return value.replace(/\u202f/g, " ").replace(/\u00a0/g, " ");
}

describe("formatCurrency", () => {
  it("formats XOF with 0 decimals", () => {
    expect(spaces(formatCurrency(150000))).toContain("150 000");
  });

  it("formats fractional amounts with 2 decimals", () => {
    expect(spaces(formatCurrency(1234.5, "EUR"))).toContain("1 234,50");
  });

  it("formats USD with en-US locale", () => {
    expect(formatsIntl(formatCurrency(100, "USD"))).toBe("$100");
  });

  it("falls back to fr-FR for unknown currency", () => {
    expect(() => formatCurrency(5, "ZZZ")).not.toThrow();
  });
});

function formatsIntl(value: string): string {
  return value.replace(/\u00a0/g, " ");
}

describe("formatPercent", () => {
  it("formats ratio as percent", () => {
    expect(formatPercent(0.156)).toBe("15.6 %");
  });

  it("honours custom digits", () => {
    expect(formatPercent(0.5, 0)).toBe("50 %");
  });

  it("coerces non-finite values to 0", () => {
    expect(formatPercent(Number.NaN)).toBe("0.0 %");
    expect(formatPercent(Number.POSITIVE_INFINITY, 0)).toBe("0 %");
  });
});

describe("formatNumber", () => {
  it("formats with fr-FR grouping", () => {
    expect(spaces(formatNumber(1234567.89))).toBe("1 234 568");
  });

  it("keeps requested decimals", () => {
    expect(spaces(formatNumber(1234.567, 2))).toBe("1 234,57");
  });
});

describe("formatDate / formatDateTime", () => {
  it("formats ISO string dates", () => {
    expect(formatDate("2024-01-05T10:00:00Z")).toBe("05/01/2024");
  });

  it("formats Date instances", () => {
    expect(formatDate(new Date(2024, 0, 5))).toBe("05/01/2024");
  });

  it("formats date and time", () => {
    expect(formatDateTime("2024-01-05T10:30:00")).toBe("05/01/2024 10:30");
  });
});

describe("formatRelativeTime", () => {
  const now = new Date("2024-03-01T12:00:00Z");

  it("returns instant under 1 minute", () => {
    expect(formatRelativeTime("2024-03-01T11:59:40Z", now)).toBe("à l'instant");
  });

  it("returns minutes", () => {
    expect(formatRelativeTime("2024-03-01T11:55:00Z", now)).toBe("il y a 5 min");
  });

  it("returns hours", () => {
    expect(formatRelativeTime("2024-03-01T09:00:00Z", now)).toBe("il y a 3 h");
  });

  it("returns days", () => {
    expect(formatRelativeTime("2024-02-25T12:00:00Z", now)).toBe("il y a 5 j");
  });

  it("falls back to absolute date after 30 days", () => {
    expect(formatRelativeTime("2024-01-05T10:00:00Z", now)).toBe("05/01/2024");
  });
});

describe("formatUuid", () => {
  it("returns value untouched when not a uuid length", () => {
    expect(formatUuid("abc")).toBe("abc");
  });

  it("uppercases the first segment of a uuid", () => {
    expect(formatUuid("abcdef01-1234-5678-9abc-def012345678")).toBe("ABCDEF01");
  });
});

describe("clamp", () => {
  it("clamps below min", () => {
    expect(clamp(0, 5, 10)).toBe(5);
  });

  it("clamps above max", () => {
    expect(clamp(12, 5, 10)).toBe(10);
  });

  it("keeps in-range values", () => {
    expect(clamp(7, 5, 10)).toBe(7);
  });
});
