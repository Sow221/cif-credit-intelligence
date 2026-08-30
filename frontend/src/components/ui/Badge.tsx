import { cn } from "../../utils/cn";

type Tone = "low" | "medium" | "high" | "neutral";

interface BadgeProps {
  tone?: Tone;
  children: React.ReactNode;
  className?: string;
}

const tones: Record<Tone, string> = {
  low: "bg-green-100 text-green-800",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-red-100 text-red-800",
  neutral: "bg-gray-100 text-gray-700",
};

export function Badge({ tone = "neutral", children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
