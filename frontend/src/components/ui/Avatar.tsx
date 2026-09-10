import { cx } from "@/utils/cx";

export interface AvatarProps {
  name: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeClasses = {
  sm: "h-8 w-8 text-label",
  md: "h-10 w-10 text-body",
  lg: "h-16 w-16 text-h2",
};

function initials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

function colorFromName(name: string): string {
  const palette = [
    "bg-accent-600",
    "bg-success-600",
    "bg-warning-600",
    "bg-info-500",
    "bg-primary-700",
  ];
  let hash = 0;
  for (const char of name) hash = (hash * 31 + char.charCodeAt(0)) % 997;
  return palette[hash % palette.length] ?? "bg-accent-600";
}

export function Avatar({ name, size = "md", className }: AvatarProps) {
  return (
    <div
      aria-hidden
      className={cx(
        "inline-flex items-center justify-center rounded-full text-white select-none",
        sizeClasses[size],
        colorFromName(name),
        className,
      )}
    >
      {initials(name)}
    </div>
  );
}
