import { useTranslation } from "react-i18next";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { RECOMMENDATION_BADGE } from "@/utils/constants";
import type { Recommendation } from "@/types/decision";

interface DecisionCardProps {
  recommendation?: Recommendation | string | null;
  policyVersion?: number | null;
  finalDecision?: string | null;
  onApprove?: () => void;
  onReject?: () => void;
  onOverride?: () => void;
  hasOverride?: boolean;
}

function recommendationVariant(
  value: string,
): "success" | "warning" | "danger" | "info" | "neutral" {
  return RECOMMENDATION_BADGE[value as keyof typeof RECOMMENDATION_BADGE] ?? "neutral";
}

export function DecisionCard({
  recommendation,
  policyVersion,
  finalDecision,
  onApprove,
  onReject,
  onOverride,
  hasOverride,
}: DecisionCardProps) {
  const { t } = useTranslation();
  const showRecommendation = Boolean(recommendation && recommendation !== "UNKNOWN");

  return (
    <Card title={t("applications:sections.finalDecision")}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          {showRecommendation ? (
            <Badge variant={recommendationVariant(recommendation ?? "")}>{recommendation}</Badge>
          ) : (
            <Badge variant="neutral">{t("applications:eligibility.notEvaluated")}</Badge>
          )}
          {policyVersion !== null && policyVersion !== undefined ? (
            <span className="text-label text-primary-500">
              {t("applications:recommendation.policyVersion")}: {policyVersion}
            </span>
          ) : null}
          {finalDecision ? (
            <Badge variant={recommendationVariant(finalDecision)}>{finalDecision}</Badge>
          ) : null}
          {hasOverride ? <Badge variant="warning">OVERRIDE</Badge> : null}
        </div>
        {!finalDecision ? (
          <div className="flex flex-wrap gap-2">
            {onApprove ? <Button onClick={onApprove}>{t("common:actions.approve")}</Button> : null}
            {onReject ? (
              <Button variant="danger" onClick={onReject}>
                {t("common:actions.reject")}
              </Button>
            ) : null}
            {onOverride ? (
              <Button variant="secondary" onClick={onOverride}>
                {t("common:actions.override")}
              </Button>
            ) : null}
          </div>
        ) : null}
      </div>
    </Card>
  );
}
