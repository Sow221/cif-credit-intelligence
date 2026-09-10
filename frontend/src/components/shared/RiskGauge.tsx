import { useTranslation } from "react-i18next";
import { Gauge } from "@/components/ui/Gauge";
import { Badge } from "@/components/ui/Badge";
import { riskBandVariant } from "@/utils/constants";
import type { RiskAssessment } from "@/types/risk";
import { formatPercent } from "@/utils/format";

interface RiskGaugeProps {
  risk: RiskAssessment;
}

export function RiskGauge({ risk }: RiskGaugeProps) {
  const { t } = useTranslation();
  const display = risk.pd_calibrated ?? risk.pd_raw;

  return (
    <div className="flex flex-col items-center gap-3 rounded-md border border-border bg-surface p-4 sm:flex-row sm:justify-center sm:gap-8">
      <Gauge value={display} label="PD" />
      <dl className="flex flex-col gap-1.5">
        <div className="flex items-center justify-between gap-4">
          <dt className="text-label text-primary-500">{t("applications:risk.pd")}</dt>
          <dd className="text-body font-medium text-primary-900">
            {formatPercent(risk.pd_raw, 2)}
          </dd>
        </div>
        {risk.pd_calibrated !== null && risk.pd_calibrated !== undefined ? (
          <div className="flex items-center justify-between gap-4">
            <dt className="text-label text-primary-500">{t("applications:risk.pdCalibrated")}</dt>
            <dd className="text-body font-medium text-primary-900">
              {formatPercent(risk.pd_calibrated, 2)}
            </dd>
          </div>
        ) : null}
        <div className="flex items-center justify-between gap-4">
          <dt className="text-label text-primary-500">{t("applications:risk.band")}</dt>
          <dd>
            <Badge variant={riskBandVariant(risk.risk_band)}>
              {t(`common:riskBand.${risk.risk_band}`)}
            </Badge>
          </dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-label text-primary-500">{t("applications:risk.model")}</dt>
          <dd className="text-body text-primary-900">{risk.model_version}</dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-label text-primary-500">{t("applications:risk.featureSet")}</dt>
          <dd className="text-body text-primary-900">{risk.feature_set_id}</dd>
        </div>
      </dl>
    </div>
  );
}
