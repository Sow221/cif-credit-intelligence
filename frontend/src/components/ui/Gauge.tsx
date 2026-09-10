import { GUIDE_COLORS } from "@/utils/constants";

interface GaugeProps {
  value: number;
  max?: number;
  size?: number;
  label?: string;
  thresholdLow?: number;
  thresholdHigh?: number;
}

function colorFor(value: number, thresholdLow: number, thresholdHigh: number): string {
  if (value < thresholdLow) return GUIDE_COLORS.low;
  if (value <= thresholdHigh) return GUIDE_COLORS.mid;
  return GUIDE_COLORS.high;
}

export function Gauge({
  value,
  max = 1,
  size = 160,
  label,
  thresholdLow = 0.15,
  thresholdHigh = 0.3,
}: GaugeProps) {
  const safeMax = max > 0 ? max : 1;
  const clamped = Math.min(Math.max(value, 0), safeMax);
  const stroke = 8;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - clamped / safeMax);
  const color = colorFor(clamped / safeMax, thresholdLow, thresholdHigh);
  const percent = Math.round((clamped / safeMax) * 100);

  return (
    <div className="inline-flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          role="img"
          aria-label={`${label ?? "Risque"} : ${percent} %`}
          className="-rotate-90"
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#E2E8F0"
            strokeWidth={stroke}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 500ms ease-out" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-h2 font-bold text-primary-900">{percent}%</span>
          {label ? <span className="text-label text-primary-500">{label}</span> : null}
        </div>
      </div>
    </div>
  );
}
