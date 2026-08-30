import { formatPd } from "../../utils/format";

interface RiskGaugeProps {
  pd: number | null;
}

/** Jauge visuelle du risque de defaut (0-100%). */
export function RiskGauge({ pd }: RiskGaugeProps) {
  if (pd === null) {
    return (
      <div className="text-center text-sm text-gray-500">
        Aucune probabilite (client Thin-File)
      </div>
    );
  }

  const pct = Math.round(pd * 100);
  let color = "bg-risk-low";
  let label = "Risque faible";
  if (pd > 0.45) {
    color = "bg-risk-high";
    label = "Risque critique";
  } else if (pd > 0.25) {
    color = "bg-risk-medium";
    label = "Risque eleve";
  } else if (pd > 0.1) {
    color = "bg-risk-medium";
    label = "Risque modere";
  }

  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between">
        <span className="text-2xl font-bold text-gray-900">{formatPd(pd)}</span>
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${Math.max(pct, 3)}%` }}
        />
      </div>
    </div>
  );
}
