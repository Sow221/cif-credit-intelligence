import type { ReactNode } from "react";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
  icon?: ReactNode;
}

export function EmptyState({ title, description, action, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 px-8 py-12 text-center">
      <div aria-hidden className="mb-2 text-primary-300">
        {icon ?? <Inbox className="h-10 w-10" />}
      </div>
      <h3 className="text-h3 text-primary-900">{title}</h3>
      {description ? <p className="max-w-sm text-body text-primary-500">{description}</p> : null}
      {action ? <div className="mt-3">{action}</div> : null}
    </div>
  );
}
