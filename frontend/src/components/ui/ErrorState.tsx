import { AlertTriangle } from "lucide-react";
import { Button } from "./Button";

interface ErrorStateProps {
  title?: string;
  description?: string;
  retryLabel?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "error.title",
  description = "error.description",
  retryLabel = "error.retry",
  onRetry,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center justify-center gap-2 px-8 py-12 text-center"
    >
      <div aria-hidden className="mb-2 text-danger-600">
        <AlertTriangle className="h-10 w-10" />
      </div>
      <h3 className="text-h3 text-danger-600">{title}</h3>
      <p className="max-w-sm text-body text-primary-500">{description}</p>
      {onRetry ? (
        <Button variant="secondary" onClick={onRetry} className="mt-3">
          {retryLabel}
        </Button>
      ) : null}
    </div>
  );
}
