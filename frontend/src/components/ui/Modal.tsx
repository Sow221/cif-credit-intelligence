import { cn } from "../../utils/cn";
import { Button } from "./Button";

interface ModalProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

export function Modal({ open, title, onClose, children }: ModalProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div
        className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
          <Button variant="secondary" size="sm" onClick={onClose} aria-label="Fermer">
            &times;
          </Button>
        </div>
        <div className={cn("max-h-[70vh] overflow-y-auto")}>{children}</div>
      </div>
    </div>
  );
}
