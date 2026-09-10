import type { ReactNode } from "react";
import { createPortal } from "react-dom";
import { CheckCircle2, AlertTriangle, XCircle, Info } from "lucide-react";
import type { ToastVariant } from "@/store/toast";
import { cx } from "@/utils/cx";

export interface ToastViewProps {
  variant: ToastVariant;
  message: string;
  icon?: ReactNode;
}

const variantIcons: Record<ToastVariant, ReactNode> = {
  success: <CheckCircle2 aria-hidden className="h-5 w-5 text-success-600" />,
  warning: <AlertTriangle aria-hidden className="h-5 w-5 text-warning-600" />,
  error: <XCircle aria-hidden className="h-5 w-5 text-danger-600" />,
  info: <Info aria-hidden className="h-5 w-5 text-info-500" />,
};

const variantClasses: Record<ToastVariant, string> = {
  success: "border-badge-successBorder",
  warning: "border-badge-warningBorder",
  error: "border-badge-dangerBorder",
  info: "border-badge-infoBorder",
};

export function ToastView({ variant, message, icon }: ToastViewProps) {
  return (
    <div
      role="status"
      className={cx(
        "pointer-events-auto flex min-w-[280px] items-center gap-3 rounded-md border bg-surface p-3 shadow-md animate-slide-in-right",
        variantClasses[variant],
      )}
    >
      {icon ?? variantIcons[variant]}
      <p className="text-body text-primary-900">{message}</p>
    </div>
  );
}

interface ToastContainerProps {
  toasts: Array<{ id: string; variant: ToastVariant; message: ReactNode }>;
  onDismiss: (id: string) => void;
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (typeof document === "undefined") return null;
  return createPortal(
    <div
      aria-live="polite"
      aria-atomic="false"
      className="pointer-events-none fixed right-4 top-4 z-[60] flex flex-col gap-2"
    >
      {toasts.map((toast) => (
        <button
          key={toast.id}
          type="button"
          onClick={() => onDismiss(toast.id)}
          className="pointer-events-auto text-left"
        >
          <ToastView variant={toast.variant} message={String(toast.message)} />
        </button>
      ))}
    </div>,
    document.body,
  );
}
