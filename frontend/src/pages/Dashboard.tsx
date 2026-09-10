import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import type { ReactNode } from "react";
import { Plus, Search, TrendingUp, TriangleAlert, Percent } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useApplications } from "@/hooks/useApplications";
import { useReviews } from "@/hooks/useReviews";
import { PageState } from "@/components/shared/PageState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { statusBadgeVariant } from "@/utils/constants";
import { formatCurrency, formatDate } from "@/utils/format";

function activityData(): Array<{ label: string; applications: number; approved: number }> {
  const days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
  return days.map((label, index) => ({
    label,
    applications: 3 + ((index * 5) % 7),
    approved: 1 + ((index * 3) % 5),
  }));
}

export default function DashboardPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { applications, status, error, reload } = useApplications();
  const { pendingCount } = useReviews();

  const kpis = {
    pending: applications.filter((app) =>
      ["SUBMITTED", "DATA_VALIDATION", "PROFILED", "SCORED"].includes(app.status),
    ).length,
    approved: applications.filter((app) => app.status === "APPROVE").length,
    review: pendingCount,
    declined: applications.filter((app) => app.status === "DECLINE").length,
  };

  const kpiCards = [
    { key: "pending", label: t("dashboard:kpis.pending"), color: "text-info-500" },
    { key: "approved", label: t("dashboard:kpis.approved"), color: "text-success-600" },
    { key: "review", label: t("dashboard:kpis.review"), color: "text-warning-600" },
    { key: "declined", label: t("dashboard:kpis.declined"), color: "text-danger-600" },
  ] as const;

  const thinFileCount = applications.filter((app) => app.information_state === "THIN_FILE").length;
  const alerts: Array<{ icon: ReactNode; text: string; tone: string }> = [];
  if (thinFileCount > 0) {
    alerts.push({
      icon: <Percent aria-hidden className="h-4 w-4" />,
      text: `${thinFileCount} ${t("dashboard:alerts.thinFile")}`,
      tone: "warning",
    });
  }
  if (kpis.review > 0) {
    alerts.push({
      icon: <TriangleAlert aria-hidden className="h-4 w-4" />,
      text: t("dashboard:alerts.overrides"),
      tone: "danger",
    });
  }

  const activity = activityData();
  const maxApplications = Math.max(...activity.map((day) => day.applications), 1);

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-h1 text-primary-900">
            {t("dashboard:greeting")}, {user?.full_name.split(" ")[0]}
          </h1>
          <p className="text-body-sm text-primary-500">{formatDate(new Date())}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" leftIcon={<Search aria-hidden className="h-4 w-4" />}>
            {t("common:actions.search")}
          </Button>
          <Link to="/applications/new">
            <Button leftIcon={<Plus aria-hidden className="h-4 w-4" />}>
              {t("common:actions.newApplication")}
            </Button>
          </Link>
        </div>
      </div>

      <PageState status={status} error={error} onRetry={reload}>
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {kpiCards.map((kpi) => (
              <Card key={kpi.key} className="animate-slide-up">
                <div className="flex items-center justify-between">
                  <p className="text-label uppercase text-primary-500">{kpi.label}</p>
                </div>
                <p className={`mt-2 text-h2 font-bold ${kpi.color}`}>{kpis[kpi.key]}</p>
              </Card>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card title={t("dashboard:alerts.title")} padded={alerts.length > 0}>
              {alerts.length === 0 ? (
                <EmptyState title={t("dashboard:alerts.empty")} icon={<CheckMark />} />
              ) : (
                <ul className="flex flex-col gap-2">
                  {alerts.map((alert, index) => (
                    <li
                      key={index}
                      className="flex items-center gap-3 rounded-md border border-border bg-background p-3"
                    >
                      <span className="text-warning-600">{alert.icon}</span>
                      <span className="text-body text-primary-900">{alert.text}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card title={t("dashboard:activity.title")}>
              <div className="flex items-end justify-between gap-2" style={{ height: 140 }}>
                {activity.map((day) => (
                  <div key={day.label} className="flex flex-1 flex-col items-center gap-1">
                    <div
                      className="flex w-full items-end justify-center gap-0.5"
                      style={{ height: 110 }}
                    >
                      <div
                        className="w-2.5 rounded-t-sm bg-accent-600"
                        style={{ height: `${(day.applications / maxApplications) * 100}%` }}
                        role="img"
                        aria-label={`${day.label}: ${day.applications} demandes`}
                      />
                      <div
                        className="w-2.5 rounded-t-sm bg-success-600"
                        style={{ height: `${(day.approved / maxApplications) * 100}%` }}
                      />
                    </div>
                    <span className="text-label text-primary-500">{day.label}</span>
                  </div>
                ))}
              </div>
              <div className="mt-2 flex gap-4 text-label text-primary-500">
                <span className="flex items-center gap-1">
                  <span aria-hidden className="h-2 w-2 rounded-full bg-accent-600" />
                  {t("dashboard:activity.applications")}
                </span>
                <span className="flex items-center gap-1">
                  <span aria-hidden className="h-2 w-2 rounded-full bg-success-600" />
                  {t("dashboard:activity.approved")}
                </span>
              </div>
            </Card>
          </div>

          <Card
            title={t("dashboard:recent.title")}
            padded={applications.length > 0}
            actions={<TrendingUp aria-hidden className="h-4 w-4 text-primary-400" />}
          >
            {applications.length === 0 ? (
              <EmptyState title={t("common:empty.applications")} />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border bg-background">
                      <th scope="col" className="table-header-cell">
                        {t("dashboard:recent.columns.id")}
                      </th>
                      <th scope="col" className="table-header-cell">
                        {t("dashboard:recent.columns.client")}
                      </th>
                      <th scope="col" className="table-header-cell">
                        {t("dashboard:recent.columns.amount")}
                      </th>
                      <th scope="col" className="table-header-cell">
                        {t("dashboard:recent.columns.status")}
                      </th>
                      <th scope="col" className="table-header-cell">
                        {t("dashboard:recent.columns.date")}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {applications.slice(0, 5).map((app) => (
                      <tr
                        key={app.application_id}
                        className="border-b border-border transition-colors duration-fast hover:bg-primary-50"
                      >
                        <td className="table-cell font-medium">
                          {app.application_id.slice(0, 8).toUpperCase()}
                        </td>
                        <td className="table-cell">
                          {app.client_name ?? app.client_id.slice(0, 8)}
                        </td>
                        <td className="table-cell">
                          {formatCurrency(app.requested_amount, app.currency)}
                        </td>
                        <td className="table-cell">
                          <Badge variant={statusBadgeVariant(app.status)}>
                            {t(`common:status.${app.status}`)}
                          </Badge>
                        </td>
                        <td className="table-cell text-primary-500">
                          {formatDate(app.application_timestamp)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </>
      </PageState>
    </div>
  );
}

function CheckMark() {
  return (
    <span aria-hidden className="flex h-10 w-10 items-center justify-center">
      <TrendingUp className="h-10 w-10" />
    </span>
  );
}
