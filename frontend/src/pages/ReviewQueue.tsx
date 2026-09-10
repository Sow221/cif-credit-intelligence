import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Clock, Play, CheckSquare } from "lucide-react";
import { useReviews } from "@/hooks/useReviews";
import { PageState } from "@/components/shared/PageState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { EmptyState } from "@/components/ui/EmptyState";
import { useAuth } from "@/hooks/useAuth";
import { reviewStatusVariant } from "@/utils/constants";
import { formatRelativeTime } from "@/utils/format";

const statusOptions = [
  { value: "", label: "" },
  { value: "PENDING", label: "En attente" },
  { value: "ASSIGNED", label: "Assignée" },
  { value: "IN_PROGRESS", label: "En cours" },
  { value: "COMPLETED", label: "Terminée" },
];

export default function ReviewQueuePage() {
  const { t } = useTranslation();
  const { reviews, status, error, reload, assign, start, complete } = useReviews();
  const { user } = useAuth();

  const [filterStatus, setFilterStatus] = useState("");
  const [completeId, setCompleteId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const canManage = user?.role === "CREDIT_MANAGER" || user?.role === "ADMIN";
  const managerId = user?.user_id ?? "";

  const filtered = useMemo(
    () => (filterStatus ? reviews.filter((review) => review.status === filterStatus) : reviews),
    [reviews, filterStatus],
  );

  async function handleComplete() {
    if (!completeId) return;
    setSubmitting(true);
    try {
      await complete(completeId, "APPROVE");
      setCompleteId(null);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-h1 text-primary-900">{t("review:title")}</h1>

      <Card padded={false}>
        <div className="flex flex-wrap items-center gap-3 border-b border-border p-4">
          <div className="w-56">
            <Select
              aria-label={t("review:filters.status")}
              label={t("review:filters.status")}
              options={statusOptions}
              value={filterStatus}
              onChange={(event) => setFilterStatus(event.target.value)}
            />
          </div>
        </div>

        <PageState
          status={status}
          error={error}
          onRetry={reload}
          defaultEmptyTitle={t("common:empty.reviews")}
        >
          {filtered.length === 0 ? (
            <EmptyState title={t("common:empty.reviews")} />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-background">
                    <th scope="col" className="table-header-cell">
                      {t("review:columns.id")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("review:columns.client")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("review:columns.pd")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("review:columns.reason")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("review:columns.age")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("review:columns.actions")}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((review) => (
                    <tr
                      key={review.review_id}
                      className="border-b border-border transition-colors duration-fast hover:bg-primary-50"
                    >
                      <td className="table-cell font-medium">
                        {review.review_id.slice(0, 8).toUpperCase()}
                      </td>
                      <td className="table-cell">
                        {review.client_name ?? review.application_id.slice(0, 8)}
                      </td>
                      <td className="table-cell text-primary-600">
                        {review.pd != null ? review.pd.toFixed(3) : "–"}
                      </td>
                      <td className="table-cell text-primary-500">{review.review_reason}</td>
                      <td className="table-cell text-primary-500">
                        <span className="flex items-center gap-1">
                          <Clock aria-hidden className="h-3.5 w-3.5" />
                          {review.started_at
                            ? formatRelativeTime(review.started_at)
                            : review.age_hours != null
                              ? `${review.age_hours} h`
                              : "–"}
                        </span>
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center gap-2">
                          <Badge variant={reviewStatusVariant(review.status)}>
                            {t(`common:reviewStatus.${review.status}`)}
                          </Badge>
                          {canManage && review.status === "PENDING" ? (
                            <Button
                              variant="secondary"
                              onClick={() => void assign(review.review_id, managerId)}
                            >
                              {t("review:actions.assign")}
                            </Button>
                          ) : null}
                          {canManage && review.status === "ASSIGNED" ? (
                            <Button
                              variant="secondary"
                              onClick={() => void start(review.review_id)}
                              leftIcon={<Play aria-hidden className="h-3.5 w-3.5" />}
                            >
                              {t("review:actions.start")}
                            </Button>
                          ) : null}
                          {canManage && review.status === "IN_PROGRESS" ? (
                            <Button
                              onClick={() => setCompleteId(review.review_id)}
                              leftIcon={<CheckSquare aria-hidden className="h-3.5 w-3.5" />}
                            >
                              {t("review:actions.complete")}
                            </Button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </PageState>
      </Card>

      <Modal
        open={completeId !== null}
        onClose={() => setCompleteId(null)}
        title={t("review:completeModal.title")}
        description={t("review:completeModal.description")}
        footer={
          <>
            <Button variant="secondary" onClick={() => setCompleteId(null)}>
              {t("common:actions.cancel")}
            </Button>
            <Button loading={submitting} onClick={() => void handleComplete()}>
              {t("common:actions.approve")}
            </Button>
          </>
        }
      />
    </div>
  );
}
