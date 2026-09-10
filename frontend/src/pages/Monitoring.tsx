import { useTranslation } from "react-i18next";
import { useMonitoring } from "@/hooks/useMonitoring";
import { useApplications } from "@/hooks/useApplications";
import { PageState } from "@/components/shared/PageState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Tabs } from "@/components/ui/Tabs";
import { EmptyState } from "@/components/ui/EmptyState";

export default function MonitoringPage() {
  const { t } = useTranslation();
  const { monitoring, status, reload } = useMonitoring();
  useApplications();

  const dataQuality = monitoring?.dataQuality ?? [];
  const incidents = monitoring?.incidents ?? [];
  const fairness = monitoring?.fairness ?? [];

  const tabs = [
    {
      id: "data",
      label: t("monitoring:tabs.data"),
      content: (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          {dataQuality.length === 0 ? (
            <div className="md:col-span-3">
              <EmptyState title={t("common:empty.applications")} />
            </div>
          ) : (
            dataQuality.map((metric) => (
              <Card key={metric.feature} title={metric.feature} padded>
                <MetricRow label={t("monitoring:dataQuality")} value={metric.completeness} />
                <MetricRow label={t("monitoring:missingRate")} value={100 - metric.completeness} />
                <MetricRow label={t("monitoring:drift")} value={metric.drift} danger />
              </Card>
            ))
          )}
        </div>
      ),
    },
    {
      id: "model",
      label: t("monitoring:tabs.model"),
      content: monitoring?.modelPerformance ? (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Card title={t("monitoring:auc")}>
            <p className="text-h2 font-bold text-primary-900">
              {monitoring.modelPerformance.auc.toFixed(4)}
            </p>
          </Card>
          <Card title={t("monitoring:brier")}>
            <p className="text-h2 font-bold text-primary-900">
              {monitoring.modelPerformance.brier.toFixed(4)}
            </p>
          </Card>
          <Card title={t("monitoring:calibration")}>
            <p className="text-h2 font-bold text-primary-900">
              {monitoring.modelPerformance.calibration_error.toFixed(4)}
            </p>
          </Card>
          <Card title="KS">
            <p className="text-h2 font-bold text-primary-900">
              {monitoring.modelPerformance.ks.toFixed(4)}
            </p>
          </Card>
        </div>
      ) : (
        <EmptyState title={t("common:empty.events")} />
      ),
    },
    {
      id: "decisions",
      label: t("monitoring:tabs.decisions"),
      content: (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Object.entries(monitoring?.decisionStats ?? {}).map(([key, value]) => (
            <Card key={key} title={key}>
              <p className="text-h2 font-bold text-primary-900">{value}</p>
            </Card>
          ))}
        </div>
      ),
    },
    {
      id: "fairness",
      label: t("monitoring:tabs.fairness"),
      content: (
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
          {fairness.length === 0 ? (
            <div className="lg:col-span-2">
              <EmptyState title={t("common:empty.events")} />
            </div>
          ) : (
            fairness.map((group) => (
              <Card key={group.group} title={group.group}>
                <MetricRow
                  label={t("monitoring:fairness.approvalRate")}
                  value={group.approval_rate}
                  color="#2563EB"
                />
                <MetricRow
                  label={t("monitoring:fairness.adverseImpact")}
                  value={group.adverse_impact_ratio}
                  color="#16A34A"
                />
                <p className="mt-2 text-label text-primary-500">
                  {t("monitoring:fairness.size")}: {group.sample_size}
                </p>
              </Card>
            ))
          )}
        </div>
      ),
    },
    {
      id: "incidents",
      label: t("monitoring:tabs.incidents"),
      content:
        incidents.length === 0 ? (
          <EmptyState title={t("monitoring:incidents.empty")} />
        ) : (
          <ul className="flex flex-col gap-2">
            {incidents.map((incident) => (
              <li
                key={incident.incident_id}
                className="flex items-center justify-between gap-3 rounded-md border border-border p-3"
              >
                <div className="min-w-0">
                  <p className="truncate text-body font-medium text-primary-900">
                    {incident.description}
                  </p>
                  <p className="text-label text-primary-500">{incident.type}</p>
                </div>
                <Badge variant={incident.severity === "CRITICAL" ? "danger" : "warning"}>
                  {incident.severity}
                </Badge>
              </li>
            ))}
          </ul>
        ),
    },
  ];

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-h1 text-primary-900">{t("monitoring:title")}</h1>
      <PageState status={status} error={null} onRetry={reload}>
        <Tabs tabs={tabs} />
      </PageState>
    </div>
  );
}

function MetricRow({
  label,
  value,
  color = "#16A34A",
  danger,
}: {
  label: string;
  value: number;
  color?: string;
  danger?: boolean;
}) {
  return (
    <div className="mb-2">
      <div className="mb-1 flex items-center justify-between">
        <span className="text-label text-primary-500">{label}</span>
        <span className="text-label text-primary-700">{value.toFixed(value >= 100 ? 0 : 1)}%</span>
      </div>
      <ProgressBar value={value} max={100} color={danger ? "#DC2626" : color} />
    </div>
  );
}
