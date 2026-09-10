import { cx } from "@/utils/cx";

export interface TimelineItemData {
  id: string;
  title: string;
  subtitle?: string;
  timestamp: string;
  type?: "success" | "warning" | "danger" | "info" | "neutral";
}

interface TimelineProps {
  items: TimelineItemData[];
}

const dotClasses = {
  success: "bg-success-600",
  warning: "bg-warning-600",
  danger: "bg-danger-600",
  info: "bg-info-500",
  neutral: "bg-primary-400",
};

export function Timeline({ items }: TimelineProps) {
  if (items.length === 0) {
    return <p className="text-body-sm text-primary-500">Aucun événement</p>;
  }
  return (
    <ol className="flex flex-col">
      {items.map((item, index) => (
        <li key={item.id} className="relative flex gap-3 pb-5 last:pb-0">
          {index < items.length - 1 ? (
            <span aria-hidden className="absolute left-[9px] top-5 bottom-0 w-0.5 bg-primary-200" />
          ) : null}
          <span
            aria-hidden
            className={cx(
              "mt-1.5 h-2 w-2 shrink-0 rounded-full",
              dotClasses[item.type ?? "neutral"],
            )}
          />
          <div className="flex flex-col gap-0.5">
            <p className="text-body font-medium text-primary-900">{item.title}</p>
            {item.subtitle ? (
              <p className="text-body-sm text-primary-500">{item.subtitle}</p>
            ) : null}
            <p className="text-label text-primary-500">{item.timestamp}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
