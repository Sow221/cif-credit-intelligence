import { cx } from "@/utils/cx";

interface ProgressBarProps {
  value: number;
  max?: number;
  color?: string;
  showLabel?: boolean;
  className?: string;
}

export function ProgressBar({
  value,
  max = 100,
  color = "#2563EB",
  showLabel = false,
  className,
}: ProgressBarProps) {
  const safeMax = max > 0 ? max : 1;
  const clamped = Math.min(Math.max(value, 0), safeMax);
  const percent = (clamped / safeMax) * 100;

  return (
    <div className={cx("flex items-center gap-2", className)}>
      <div
        role="progressbar"
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={safeMax}
        aria-label="Progression"
        className="h-2 w-full overflow-hidden rounded-full bg-primary-200"
      >
        <div
          className="h-full rounded-full"
          style={{
            width: `${percent}%`,
            backgroundColor: color,
            transition: "width 300ms ease-out",
          }}
        />
      </div>
      {showLabel ? (
        <span className="text-label text-primary-600">{percent.toFixed(0)}%</span>
      ) : null}
    </div>
  );
}
