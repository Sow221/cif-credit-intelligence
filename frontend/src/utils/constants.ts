import type { ApplicationStatus, RiskBand } from "@/types/application";
import type { InformationState } from "@/types/information";
import type { ReviewStatus } from "@/types/review";
import type { BadgeVariant } from "@/components/ui/Badge";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const APP_VERSION = "2.0.0";

export const PRODUCT_OPTIONS = [
  { value: "SMALL_BUSINESS", label: "Petit commerce" },
  { value: "PERSONAL", label: "Personnel" },
  { value: "AGRICULTURE", label: "Agriculture" },
  { value: "MICRO_FINANCE", label: "Microfinance" },
];

export const TERM_OPTIONS = [6, 12, 18, 24];

export const PAGE_SIZE_OPTIONS = [10, 25, 50];

export const STATUS_BADGE: Record<ApplicationStatus, BadgeVariant> = {
  DRAFT: "neutral",
  SUBMITTED: "info",
  DATA_VALIDATION: "info",
  PROFILED: "info",
  SCORED: "info",
  REVIEW: "warning",
  DECIDED: "success",
  CANCELLED: "neutral",
  APPROVE: "success",
  DECLINE: "danger",
};

export function statusBadgeVariant(status: ApplicationStatus): BadgeVariant {
  return STATUS_BADGE[status] ?? "neutral";
}

export function informationStateBadge(state: InformationState): BadgeVariant {
  switch (state) {
    case "FULL_FILE":
      return "success";
    case "THIN_FILE":
      return "warning";
    case "NO_FILE":
    case "DATA_POOR":
      return "danger";
    default:
      return "neutral";
  }
}

export function riskBandVariant(band: RiskBand): BadgeVariant {
  switch (band) {
    case "LOW":
      return "success";
    case "MEDIUM":
      return "warning";
    case "HIGH":
      return "danger";
    default:
      return "neutral";
  }
}

export function reviewStatusVariant(status: ReviewStatus): BadgeVariant {
  switch (status) {
    case "PENDING":
      return "warning";
    case "ASSIGNED":
      return "info";
    case "IN_PROGRESS":
      return "info";
    case "COMPLETED":
      return "success";
    default:
      return "neutral";
  }
}

export const RECOMMENDATION_BADGE = {
  APPROVE: "success",
  DECLINE: "danger",
  REVIEW: "warning",
  REFER: "info",
  UNKNOWN: "neutral",
} as const;

export const NAV_ITEMS = [
  { to: "/dashboard", key: "dashboard", labelKey: "nav.dashboard", icon: "LayoutDashboard" },
  { to: "/applications", key: "applications", labelKey: "nav.applications", icon: "FileText" },
  { to: "/clients", key: "clients", labelKey: "nav.clients", icon: "Users" },
  { to: "/review", key: "review", labelKey: "nav.review", icon: "ClipboardCheck", badge: true },
  { to: "/models", key: "models", labelKey: "nav.models", icon: "Cpu" },
  { to: "/monitoring", key: "monitoring", labelKey: "nav.monitoring", icon: "Activity" },
  { to: "/admin", key: "admin", labelKey: "nav.admin", icon: "Settings" },
] as const;

export const GUIDE_COLORS = {
  low: "#16A34A",
  mid: "#D97706",
  high: "#DC2626",
} as const;
