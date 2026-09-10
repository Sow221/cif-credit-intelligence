import { forwardRef } from "react";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { cx } from "@/utils/cx";

export type ButtonVariant = "primary" | "secondary" | "danger" | "ghost" | "icon";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  loading?: boolean;
  leftIcon?: ReactNode;
  children?: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: "bg-accent-600 text-white hover:bg-accent-700 disabled:bg-primary-200",
  secondary:
    "bg-surface text-accent-600 border border-border hover:bg-primary-50 disabled:text-primary-300",
  danger: "bg-danger-600 text-white hover:bg-danger-700 disabled:bg-primary-200",
  ghost: "bg-transparent text-accent-600 hover:bg-accent-50 h-9 px-3 disabled:text-primary-300",
  icon: "bg-transparent text-primary-500 hover:bg-primary-100 h-10 w-10 px-0 disabled:text-primary-300",
};

const baseClasses =
  "inline-flex items-center justify-center gap-2 rounded-md border border-transparent px-4 font-button transition-all duration-fast active:scale-[0.98] focus-ring disabled:cursor-not-allowed disabled:opacity-60";

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = "primary",
    loading = false,
    leftIcon,
    children,
    className,
    disabled,
    type = "button",
    ...rest
  },
  ref,
) {
  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled || loading}
      className={cx(baseClasses, variantClasses[variant], className)}
      {...rest}
    >
      {loading ? <Loader2 aria-hidden className="h-4 w-4 animate-spin" /> : leftIcon}
      {children}
    </button>
  );
});
