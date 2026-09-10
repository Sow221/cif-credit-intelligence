import { describe, expect, it } from "vitest";
import {
  API_BASE_URL,
  APP_VERSION,
  GUIDE_COLORS,
  NAV_ITEMS,
  PAGE_SIZE_OPTIONS,
  PRODUCT_OPTIONS,
  RECOMMENDATION_BADGE,
  STATUS_BADGE,
  TERM_OPTIONS,
  informationStateBadge,
  reviewStatusVariant,
  riskBandVariant,
  statusBadgeVariant,
} from "./constants";

describe("constants", () => {
  it("uses /api/v1 as default API base", () => {
    expect(API_BASE_URL).toBe("/api/v1");
  });

  it("exposes a semver app version", () => {
    expect(APP_VERSION).toMatch(/^\d+\.\d+\.\d+$/);
  });

  it("exposes product and term options", () => {
    expect(PRODUCT_OPTIONS).toHaveLength(4);
    expect(TERM_OPTIONS).toEqual([6, 12, 18, 24]);
    expect(PAGE_SIZE_OPTIONS).toEqual([10, 25, 50]);
  });

  it("exposes 7 navigation items with review badge flag", () => {
    expect(NAV_ITEMS).toHaveLength(7);
    const review = NAV_ITEMS.find((item) => item.to === "/review");
    expect(review?.badge).toBe(true);
  });

  it("exposes guide colors", () => {
    expect(GUIDE_COLORS).toEqual({
      low: "#16A34A",
      mid: "#D97706",
      high: "#DC2626",
    });
  });
});

describe("statusBadgeVariant", () => {
  it("maps every application status", () => {
    expect(Object.keys(STATUS_BADGE)).toHaveLength(10);
    expect(statusBadgeVariant("SUBMITTED")).toBe("info");
    expect(statusBadgeVariant("REVIEW")).toBe("warning");
    expect(statusBadgeVariant("DECIDED")).toBe("success");
    expect(statusBadgeVariant("APPROVE")).toBe("success");
    expect(statusBadgeVariant("DECLINE")).toBe("danger");
  });

  it("falls back to neutral for unknown status", () => {
    expect(statusBadgeVariant("UNKNOWN" as never)).toBe("neutral");
  });
});

describe("informationStateBadge", () => {
  it("maps full, thin and poor files", () => {
    expect(informationStateBadge("FULL_FILE")).toBe("success");
    expect(informationStateBadge("THIN_FILE")).toBe("warning");
    expect(informationStateBadge("NO_FILE")).toBe("danger");
    expect(informationStateBadge("DATA_POOR")).toBe("danger");
  });

  it("falls back to neutral", () => {
    expect(informationStateBadge("UNKNOWN" as never)).toBe("neutral");
  });
});

describe("riskBandVariant", () => {
  it("maps risk bands", () => {
    expect(riskBandVariant("LOW")).toBe("success");
    expect(riskBandVariant("MEDIUM")).toBe("warning");
    expect(riskBandVariant("HIGH")).toBe("danger");
    expect(riskBandVariant("UNKNOWN" as never)).toBe("neutral");
  });
});

describe("reviewStatusVariant", () => {
  it("maps review statuses", () => {
    expect(reviewStatusVariant("PENDING")).toBe("warning");
    expect(reviewStatusVariant("ASSIGNED")).toBe("info");
    expect(reviewStatusVariant("IN_PROGRESS")).toBe("info");
    expect(reviewStatusVariant("COMPLETED")).toBe("success");
    expect(reviewStatusVariant("CANCELLED" as never)).toBe("neutral");
  });
});

describe("RECOMMENDATION_BADGE", () => {
  it("maps recommendations", () => {
    expect(RECOMMENDATION_BADGE.APPROVE).toBe("success");
    expect(RECOMMENDATION_BADGE.DECLINE).toBe("danger");
    expect(RECOMMENDATION_BADGE.REFER).toBe("info");
  });
});