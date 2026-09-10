import { cx } from "@/utils/cx";

export type SkeletonVariant = "text" | "title" | "card" | "avatar" | "button";

interface SkeletonProps {
  variant?: SkeletonVariant;
  className?: string;
}

const variantClasses: Record<SkeletonVariant, string> = {
  text: "h-3 rounded",
  title: "h-5 w-2/3 rounded",
  card: "h-32 rounded-lg",
  avatar: "h-10 w-10 rounded-full",
  button: "h-10 w-28 rounded-md",
};

export function Skeleton({ variant = "text", className }: SkeletonProps) {
  return (
    <div
      aria-hidden
      className={cx("animate-pulse-soft bg-primary-200", variantClasses[variant], className)}
    />
  );
}

interface SkeletonListProps {
  rows?: number;
  variant?: SkeletonVariant;
}

export function SkeletonList({ rows = 5, variant = "text" }: SkeletonListProps) {
  return (
    <div role="status" aria-label="Chargement..." className="flex flex-col gap-3 p-4">
      {Array.from({ length: rows }, (_, index) => (
        <Skeleton key={index} variant={variant} />
      ))}
    </div>
  );
}
