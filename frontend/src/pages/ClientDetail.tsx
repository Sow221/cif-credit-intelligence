import { useCallback, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import { useDataStore } from "@/store/data";
import { useApplications } from "@/hooks/useApplications";
import { PageState } from "@/components/shared/PageState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Avatar } from "@/components/ui/Avatar";
import { EmptyState } from "@/components/ui/EmptyState";
import { AuditTimeline } from "@/components/shared/AuditTimeline";
import { formatCurrency, formatDate } from "@/utils/format";
import type { TimelineItemData } from "@/components/ui/Timeline";

const statusBadge = { ACTIVE: "success", BLOCKED: "danger", PENDING: "warning" } as const;

export default function ClientDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const client = useDataStore((state) => state.currentClient);
  const status = useDataStore((state) => state.currentClientStatus);
  const error = useDataStore((state) => state.currentClientError);
  const fetchClient = useDataStore((state) => state.fetchClient);
  const applications = useDataStore((state) => state.applications);
  useApplications();

  const reload = useCallback(() => {
    if (id) void fetchClient(id);
  }, [id, fetchClient]);

  useEffect(reload, [reload]);

  if (!id) return <p className="text-body text-danger-600">{t("common:errors.missing")}</p>;

  const clientApplications = client
    ? applications.filter((app) => app.client_id === client.client_id)
    : [];

  const auditItems: TimelineItemData[] = client
    ? [
        {
          id: "created",
          title: t("common:nav.clients"),
          subtitle: "Client créé",
          timestamp: formatDate(client.created_at),
          type: "info",
        },
      ]
    : [];

  return (
    <div className="flex flex-col gap-4">
      <PageState
        status={status as "loading" | "error" | "success" | "idle"}
        error={error}
        onRetry={reload}
      >
        {!client ? (
          <EmptyState title={t("common:empty.clients")} />
        ) : (
          <>
            <Card>
              <div className="flex flex-wrap items-center gap-4">
                <Avatar name={`${client.first_name} ${client.last_name}`} size="lg" />
                <div className="min-w-0 flex-1">
                  <h1 className="text-h1 text-primary-900">
                    {client.first_name} {client.last_name}
                  </h1>
                  <p className="text-body-sm text-primary-500">
                    {client.client_id} · {t(`clients:statusLabel.${client.status}`)}
                  </p>
                </div>
                <Badge variant={statusBadge[client.status]}>
                  {t(`clients:statusLabel.${client.status}`)}
                </Badge>
              </div>
            </Card>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <Card title={t("clients:detail.identity")}>
                <dl className="flex flex-col gap-2">
                  <Row label="Email" value={client.email ?? "–"} />
                  <Row label="Téléphone" value={client.phone ?? "–"} />
                  <Row label="Zone" value={client.zone ?? "–"} />
                  <Row label="Secteur" value={client.sector ?? "–"} />
                  <Row
                    label="Né(e) le"
                    value={client.date_of_birth ? formatDate(client.date_of_birth) : "–"}
                  />
                </dl>
              </Card>

              <Card title={t("clients:detail.savings")}>
                {client.savings ? (
                  <dl className="flex flex-col gap-2">
                    <Row
                      label={t("clients:detail.balance")}
                      value={formatCurrency(client.savings.balance, client.savings.currency)}
                    />
                    <Row
                      label={t("clients:detail.average")}
                      value={formatCurrency(
                        client.savings.average_balance,
                        client.savings.currency,
                      )}
                    />
                    <Row
                      label={t("clients:detail.stability")}
                      value={`${client.savings.stability_score.toFixed(0)}%`}
                    />
                  </dl>
                ) : (
                  <EmptyState title={t("clients:detail.noConsents")} />
                )}
              </Card>
            </div>

            <Card title={t("clients:detail.loans")} padded={(client.loans ?? []).length > 0}>
              {!client.loans || client.loans.length === 0 ? (
                <EmptyState title={t("clients:detail.noLoans")} />
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border bg-background">
                        <th scope="col" className="table-header-cell">
                          ID
                        </th>
                        <th scope="col" className="table-header-cell">
                          Montant
                        </th>
                        <th scope="col" className="table-header-cell">
                          Statut
                        </th>
                        <th scope="col" className="table-header-cell">
                          Début
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {client.loans.map((loan) => (
                        <tr key={loan.loan_id} className="border-b border-border">
                          <td className="table-cell font-medium">
                            {loan.loan_id.slice(0, 8).toUpperCase()}
                          </td>
                          <td className="table-cell">
                            {formatCurrency(loan.amount, loan.currency)}
                          </td>
                          <td className="table-cell">
                            <Badge variant="info">{loan.status}</Badge>
                          </td>
                          <td className="table-cell text-primary-500">
                            {formatDate(loan.started_at)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            <Card title={t("clients:detail.decisions")}>
              <ul className="flex flex-col divide-y divide-border">
                {clientApplications.slice(0, 5).map((app) => (
                  <li key={app.application_id}>
                    <a
                      href={`#/applications/${app.application_id}`}
                      onClick={(event) => event.preventDefault()}
                      className="flex items-center justify-between px-1 py-2 text-body-sm text-primary-700 hover:text-accent-600"
                    >
                      <span>
                        {app.application_id.slice(0, 8).toUpperCase()} ·{" "}
                        {formatCurrency(app.requested_amount, app.currency)}
                      </span>
                      <ChevronRight aria-hidden className="h-4 w-4" />
                    </a>
                  </li>
                ))}
                {clientApplications.length === 0 ? (
                  <EmptyState title={t("clients:detail.noApplications")} />
                ) : null}
              </ul>
            </Card>

            <AuditTimeline items={auditItems} title={t("clients:detail.audit")} />
          </>
        )}
      </PageState>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-label text-primary-500">{label}</dt>
      <dd className="text-body text-primary-900">{value}</dd>
    </div>
  );
}
