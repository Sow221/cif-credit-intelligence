import type { ReactNode } from "react";
import { cx } from "@/utils/cx";

export type BadgeVariant = "success" | "warning" | "danger" | "info" | "neutral";

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  success: "bg-success-50 text-success-600 border-badge-successBorder",
  warning: "bg-warning-50 text-warning-600 border-badge-warningBorder",
  danger: "bg-danger-50 text-danger-600 border-badge-dangerBorder",
  info: "bg-info-50 text-info-500 border-badge-infoBorder",
  neutral: "bg-background text-badge-neutralText border-badge-neutralBorder",
};

const baseClasses =
  "inline-flex items-center gap-1 rounded-sm border px-2 py-0.5 text-label font-medium";

export function Badge({ variant = "neutral", children, className }: BadgeProps) {
  return <span className={cx(baseClasses, variantClasses[variant], className)}>{children}</span>;
}
