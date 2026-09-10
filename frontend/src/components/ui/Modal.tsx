import { useEffect } from "react";
import type { ReactNode } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { Button } from "./Button";
import { cx } from "@/utils/cx";

export type ModalSize = "sm" | "md" | "lg";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children?: ReactNode;
  footer?: ReactNode;
  size?: ModalSize;
}

const sizeClasses: Record<ModalSize, string> = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-2xl",
};

export function Modal({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  size = "md",
}: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    const previous = document.activeElement as HTMLElement | null;
    const dialog = document.getElementById("focus-dialog-title");
    dialog?.focus();
    return () => {
      document.removeEventListener("keydown", handleKey);
      previous?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        aria-hidden
        onClick={onClose}
        className="absolute inset-0 bg-primary-900/50 animate-fade-in"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="focus-dialog-title"
        tabIndex={-1}
        className={cx(
          "relative w-full rounded-lg bg-surface shadow-lg animate-pop-in",
          sizeClasses[size],
        )}
      >
        <div className="flex items-start justify-between border-b border-border p-4">
          <div>
            <h2 id="focus-dialog-title" className="text-h2 text-primary-900">
              {title}
            </h2>
            {description ? (
              <p className="mt-1 text-body-sm text-primary-500">{description}</p>
            ) : null}
          </div>
          <Button variant="icon" onClick={onClose} aria-label="Fermer" className="h-8 w-8 shrink-0">
            <X aria-hidden className="h-4 w-4" />
          </Button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto p-4">{children}</div>
        {footer ? (
          <div className="flex justify-end gap-2 border-t border-border p-4">{footer}</div>
        ) : null}
      </div>
    </div>,
    document.body,
  );
}
