import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router-dom";
import { CircleAlert, EyeOff, History, User as UserIcon } from "lucide-react";
import { useApplications } from "@/hooks/useApplications";
import { useDataStore } from "@/store/data";
import { useToastStore } from "@/store/toast";
import { PageState } from "@/components/shared/PageState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { RiskGauge } from "@/components/shared/RiskGauge";
import { UncertaintyCard } from "@/components/shared/UncertaintyCard";
import { DecisionCard } from "@/components/shared/DecisionCard";
import { statusBadgeVariant, informationStateBadge } from "@/utils/constants";
import { formatCurrency, formatDateTime, formatPercent } from "@/utils/format";
import type { Uncertainty } from "@/types/risk";
import type { InformationState } from "@/types/information";

type DecisionAction = "APPROVE" | "DECLINE" | "OVERRIDE" | null;

export default function ApplicationDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const { updateStatus } = useApplications();
  const currentApplication = useDataStore((state) => state.currentApplication);
  const status = useDataStore((state) => state.currentApplicationStatus);
  const error = useDataStore((state) => state.currentApplicationError);
  const fetchApplication = useDataStore((state) => state.fetchApplication);
  const createDecision = useDataStore((state) => state.createDecision);
  const createOverride = useDataStore((state) => state.createOverride);
  const addToast = useToastStore((state) => state.addToast);

  const [decisionModal, setDecisionModal] = useState<DecisionAction>(null);
  const [reason, setReason] = useState("");
  const [overrideDecision, setOverrideDecision] = useState<"APPROVE" | "DECLINE">("APPROVE");
  const [submitting, setSubmitting] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const reload = useCallback(() => {
    if (id) void fetchApplication(id);
  }, [id, fetchApplication]);

  useEffect(reload, [reload]);

  if (!id) return <ErrorMissing />;
  if (status === "idle") return null;

  const app = currentApplication;

  function openModal(action: Exclude<DecisionAction, null>) {
    setDecisionModal(action);
    setReason("");
    setOverrideDecision("APPROVE");
    setValidationError(null);
  }

  async function executeDecision(action: Exclude<DecisionAction, null>) {
    if (!app) return;
    setSubmitting(true);
    setValidationError(null);
    try {
      const decision = await createDecision(app.application_id);
      if (
        action === "OVERRIDE" ||
        (decision.recommendation && decision.recommendation !== action)
      ) {
        if (!reason.trim()) {
          setValidationError(t("applications:errors.overrideReason"));
          setSubmitting(false);
          return;
        }
        await createOverride(decision.decision_id, {
          final_decision:
            action === "OVERRIDE" ? overrideDecision : (action as "APPROVE" | "DECLINE"),
          override_reason: reason,
        });
        addToast("success", t("applications:finalDecision.overrideSaved"));
      } else {
        await updateStatus(app.application_id, action);
        addToast("success", t("applications:finalDecision.decisionSaved"));
      }
      setDecisionModal(null);
      await fetchApplication(app.application_id);
    } catch (err) {
      const message = err instanceof Error ? err.message : t("common:errors.internal");
      setValidationError(message);
    } finally {
      setSubmitting(false);
    }
  }

  const kpis = app
    ? [
        {
          label: t("applications:new.amount"),
          value: formatCurrency(app.requested_amount, app.currency),
        },
        {
          label: t("applications:risk.pd"),
          value: app.risk ? formatPercent(app.risk.pd_raw, 2) : "–",
        },
        { label: t("applications:columns.status"), value: t(`common:status.${app.status}`) },
        {
          label: t("applications:eligibility.eligible"),
          value: app.eligibility ? (app.eligibility.eligible ? "Oui" : "Non") : "–",
        },
      ]
    : [];

  const uncertainty: Uncertainty | null = app?.uncertainty_level
    ? {
        level: (app.uncertainty_level as Uncertainty["level"]) ?? "MODERATE",
        score: 0.5,
        method: "conformal",
        factors: [],
      }
    : null;

  return (
    <div className="flex flex-col gap-4">
      {app ? (
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Badge variant={statusBadgeVariant(app.status)}>
              {t(`common:status.${app.status}`)}
            </Badge>
            <span className="text-body-sm text-primary-500">
              {formatDateTime(app.application_timestamp)}
            </span>
          </div>
        </div>
      ) : null}

      <PageState
        status={status as "loading" | "error" | "success" | "idle"}
        error={error}
        onRetry={reload}
      >
        {!app ? (
          <div className="py-12 text-center text-body text-primary-500">
            {t("common:empty.applications")}
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {kpis.map((kpi) => (
                <Card key={kpi.label}>
                  <p className="text-label uppercase text-primary-500">{kpi.label}</p>
                  <p className="mt-1 text-h2 font-semibold text-primary-900">{kpi.value}</p>
                </Card>
              ))}
            </div>

            <Card title={t("applications:sections.client")}>
              <div className="flex items-center gap-3">
                <UserIcon aria-hidden className="h-8 w-8 text-primary-400" />
                <div className="flex-1">
                  <p className="text-body font-medium text-primary-900">
                    {app.client_name ?? app.client_id}
                  </p>
                  <p className="text-body-sm text-primary-500">
                    {app.currency} · {app.product_id}
                  </p>
                </div>
                <Link
                  to={`/clients/${app.client_id}`}
                  className="text-body-sm font-medium text-accent-600 hover:text-accent-700 focus-ring"
                >
                  {t("applications:detail")}
                </Link>
              </div>
            </Card>

            <Card title={t("applications:sections.eligibility")}>
              {app.eligibility ? (
                <div className="flex flex-col gap-2">
                  <Badge variant={app.eligibility.eligible ? "success" : "danger"}>
                    {app.eligibility.eligible
                      ? t("applications:eligibility.eligible")
                      : t("applications:eligibility.notEligible")}
                  </Badge>
                  {app.eligibility.reasons.length > 0 ? (
                    <ul className="flex flex-col gap-1">
                      {app.eligibility.reasons.map((reason, index) => (
                        <li key={index} className="text-body-sm text-primary-700">
                          • {reason}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              ) : (
                <Badge variant="neutral">{t("applications:eligibility.notEvaluated")}</Badge>
              )}
            </Card>

            <Card title={t("applications:sections.informationProfile")}>
              <div className="flex items-center justify-between">
                <Badge
                  variant={informationStateBadge(
                    (app.information_state ?? "UNKNOWN") as InformationState,
                  )}
                >
                  {t(
                    `common:informationState.${(app.information_state ?? "UNKNOWN") as InformationState}`,
                  )}
                </Badge>
                {app.information_profile ? (
                  <span className="text-label text-primary-500">
                    v{app.information_profile.version}
                  </span>
                ) : (
                  <span className="text-label text-primary-500">—</span>
                )}
              </div>
            </Card>

            {app.risk ? (
              <>
                <Card title={t("applications:sections.risk")} padded={false}>
                  <div className="p-4">
                    <RiskGauge risk={app.risk} />
                  </div>
                </Card>
                {uncertainty ? <UncertaintyCard uncertainty={uncertainty} /> : null}
              </>
            ) : null}

            <Card title={t("applications:sections.explanation")}>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <h4 className="mb-2 text-label uppercase text-primary-500">
                    {t("applications:explanation.model")}
                  </h4>
                  <ul className="flex flex-col gap-1">
                    {(
                      app.explanation_factors ?? [
                        "savings_balance",
                        "repayment_history",
                        "monthly_income",
                      ]
                    ).map((factor) => (
                      <li
                        key={factor}
                        className="flex items-center gap-2 text-body-sm text-primary-700"
                      >
                        <CircleAlert aria-hidden className="h-3.5 w-3.5 text-accent-600" />
                        {factor}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="mb-2 text-label uppercase text-primary-500">
                    {t("applications:explanation.decision")}
                  </h4>
                  {app.decision_reason ? (
                    <p className="text-body-sm text-primary-700">{app.decision_reason}</p>
                  ) : (
                    <p className="text-body-sm text-primary-400">
                      {t("applications:explanation.empty")}
                    </p>
                  )}
                </div>
              </div>
            </Card>

            <Card title={t("applications:sections.informationGap")}>
              {(app.information_gaps ?? []).length === 0 ? (
                <p className="flex items-center gap-2 text-body-sm text-primary-400">
                  <History aria-hidden className="h-4 w-4" />
                  {t("applications:gap.empty")}
                </p>
              ) : (
                <ul className="flex flex-col gap-1.5">
                  {(app.information_gaps ?? []).map((gap, index) => (
                    <li
                      key={index}
                      className="flex items-center gap-2 text-body-sm text-primary-700"
                    >
                      {gap.type === "missing" ? (
                        <EyeOff aria-hidden className="h-3.5 w-3.5 text-danger-600" />
                      ) : (
                        <History aria-hidden className="h-3.5 w-3.5 text-warning-600" />
                      )}
                      <span>{gap.item}</span>
                      <Badge variant={gap.type === "missing" ? "danger" : "warning"}>
                        {t(`applications:gap.${gap.type}`)}
                      </Badge>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <DecisionCard
              recommendation={app.recommendation}
              policyVersion={app.policy_version}
              finalDecision={app.final_decision}
              hasOverride={Boolean(
                app.final_decision &&
                app.recommendation &&
                app.final_decision !== app.recommendation,
              )}
              onApprove={app.final_decision ? undefined : () => openModal("APPROVE")}
              onReject={app.final_decision ? undefined : () => openModal("DECLINE")}
              onOverride={app.final_decision ? undefined : () => openModal("OVERRIDE")}
            />
          </div>
        )}
      </PageState>

      <Modal
        open={decisionModal !== null}
        onClose={() => setDecisionModal(null)}
        title={
          decisionModal === "APPROVE"
            ? t("applications:finalDecision.approveModal.title")
            : decisionModal === "DECLINE"
              ? t("applications:finalDecision.rejectModal.title")
              : t("applications:finalDecision.overrideModal.title")
        }
        description={
          decisionModal === "OVERRIDE"
            ? t("applications:finalDecision.overrideModal.description", {
                recommendation: app?.recommendation ?? "–",
              })
            : undefined
        }
        footer={
          <>
            <Button variant="secondary" onClick={() => setDecisionModal(null)}>
              {t("common:actions.cancel")}
            </Button>
            <Button
              variant={decisionModal === "DECLINE" ? "danger" : "primary"}
              loading={submitting}
              onClick={() => {
                if (decisionModal) void executeDecision(decisionModal);
              }}
            >
              {t("common:actions.confirm")}
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-4">
          {decisionModal === "OVERRIDE" ? (
            <div className="flex flex-col gap-3 rounded-md border border-border p-3">
              <div className="flex items-center justify-between">
                <span className="text-label text-primary-500">
                  {t("applications:finalDecision.overrideModal.result")}
                </span>
                <span className="text-body font-medium text-primary-900">
                  {app?.recommendation ?? "REVIEW"}
                </span>
              </div>
              <Select
                label={t("applications:finalDecision.overrideModal.yourDecision")}
                options={[
                  { value: "APPROVE", label: t("common:actions.approve") },
                  { value: "DECLINE", label: t("common:actions.reject") },
                ]}
                value={overrideDecision}
                onChange={(event) =>
                  setOverrideDecision(event.target.value as "APPROVE" | "DECLINE")
                }
              />
            </div>
          ) : null}
          <Input
            label={
              decisionModal === "DECLINE"
                ? t("applications:finalDecision.rejectModal.reason")
                : t("common:actions.justification")
            }
            required={decisionModal === "OVERRIDE" || decisionModal === "DECLINE"}
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            error={validationError ?? undefined}
          />
        </div>
      </Modal>
    </div>
  );
}

function ErrorMissing() {
  const { t } = useTranslation();
  return (
    <p className="py-12 text-center text-body text-danger-600">{t("common:errors.missing")}</p>
  );
}
