import { describe, expect, it } from "vitest";
import { formatCurrency, formatDate, formatPd } from "../../src/utils/format";

describe("formatPd", () => {
  it("formate une probabilite en pourcentage", () => {
    expect(formatPd(0.056)).toBe("5.6%");
  });

  it("retourne un em-dash pour null", () => {
    expect(formatPd(null)).toBe("—");
  });

  it("retourne un em-dash pour NaN", () => {
    expect(formatPd(Number.NaN)).toBe("—");
  });
});

describe("formatCurrency", () => {
  it("formate un montant FCFA", () => {
    expect(formatCurrency(125000)).toEqual(expect.stringMatching(/125\s?000/));
    expect(formatCurrency(125000)).toContain("F");
  });
});

describe("formatDate", () => {
  it("formate une date ISO", () => {
    const iso = "2026-08-30T10:15:00Z";
    expect(formatDate(iso)).not.toBe("—");
  });

  it("retourne un em-dash pour une date invalide", () => {
    expect(formatDate("pas-une-date")).toBe("—");
  });
});
