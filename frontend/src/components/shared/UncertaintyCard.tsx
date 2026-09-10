import { useTranslation } from "react-i18next";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { Uncertainty } from "@/types/risk";

interface UncertaintyCardProps {
  uncertainty: Uncertainty;
}

function uncertaintyBadge(level: Uncertainty["level"]): "success" | "warning" | "danger" {
  switch (level) {
    case "LOW":
      return "success";
    case "MODERATE":
      return "warning";
    default:
      return "danger";
  }
}

export function UncertaintyCard({ uncertainty }: UncertaintyCardProps) {
  const { t } = useTranslation();

  return (
    <Card title={t("applications:sections.uncertainty")}>
      <div className="flex items-center gap-3">
        <Badge variant={uncertaintyBadge(uncertainty.level)}>
          {t(`applications:uncertainty.${uncertainty.level}`)}
        </Badge>
        <span className="text-body-sm text-primary-500">
          {t("applications:uncertainty.method")}: {uncertainty.method}
        </span>
      </div>
      {uncertainty.confidence_interval ? (
        <p className="mt-2 text-body-sm text-primary-600">
          {t("applications:uncertainty.confidence")}: [
          {uncertainty.confidence_interval.lower.toFixed(3)},{" "}
          {uncertainty.confidence_interval.upper.toFixed(3)}]
        </p>
      ) : null}
      {uncertainty.factors.length > 0 ? (
        <ul className="mt-3 flex flex-col gap-1.5">
          {uncertainty.factors.map((factor) => (
            <li key={factor.name} className="flex items-center justify-between gap-2">
              <span className="text-body-sm text-primary-700">{factor.name}</span>
              <Badge variant={uncertaintyBadge(factor.impact)}>{factor.impact}</Badge>
            </li>
          ))}
        </ul>
      ) : null}
    </Card>
  );
}
