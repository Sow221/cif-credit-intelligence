import { useState } from "react";
import { useTranslation } from "react-i18next";
import { ArrowUp, Archive, Eye, Cpu } from "lucide-react";
import { useModels } from "@/hooks/useModels";
import { PageState } from "@/components/shared/PageState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { EmptyState } from "@/components/ui/EmptyState";
import type { Model } from "@/types/model";
import { formatDate } from "@/utils/format";

const statusVariant = {
  DRAFT: "neutral",
  STAGING: "info",
  PRODUCTION: "success",
  ARCHIVED: "neutral",
  DEPRECATED: "danger",
} as const;

const STATUS_ORDER = ["PRODUCTION", "STAGING", "DRAFT", "ARCHIVED", "DEPRECATED"] as const;

export default function ModelsPage() {
  const { t } = useTranslation();
  const { models, status, error, reload, promoteModel } = useModels();
  const [selected, setSelected] = useState<Model | null>(null);
  const [busy, setBusy] = useState(false);

  const ordered = [...models].sort(
    (a, b) =>
      STATUS_ORDER.indexOf(a.status as (typeof STATUS_ORDER)[number]) -
      STATUS_ORDER.indexOf(b.status as (typeof STATUS_ORDER)[number]),
  );

  async function handlePromote(model: Model) {
    setBusy(true);
    try {
      await promoteModel(model.model_id, "PROMOTE");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-h1 text-primary-900">{t("models:title")}</h1>

      <PageState
        status={status}
        error={error}
        onRetry={reload}
        defaultEmptyTitle={t("models:title")}
      >
        {ordered.length === 0 ? (
          <EmptyState title={t("models:title")} icon={<Cpu aria-hidden className="h-10 w-10" />} />
        ) : (
          <Card padded={false}>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-background">
                    <th scope="col" className="table-header-cell">
                      {t("models:columns.model")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("models:columns.version")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("models:columns.status")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("models:columns.auc")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("models:columns.featureSet")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("models:columns.date")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("models:columns.actions")}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {ordered.map((model) => (
                    <tr
                      key={model.model_id}
                      className="border-b border-border transition-colors duration-fast hover:bg-primary-50"
                    >
                      <td className="table-cell font-medium">{model.name}</td>
                      <td className="table-cell text-primary-500">{model.version}</td>
                      <td className="table-cell">
                        <Badge variant={statusVariant[model.status]}>
                          {t(`models:statusLabel.${model.status}`)}
                        </Badge>
                      </td>
                      <td className="table-cell text-primary-900">{model.auc.toFixed(4)}</td>
                      <td className="table-cell text-primary-500">{model.feature_set_id}</td>
                      <td className="table-cell text-primary-500">
                        {formatDate(model.created_at)}
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            onClick={() => setSelected(model)}
                            leftIcon={<Eye aria-hidden className="h-3.5 w-3.5" />}
                          >
                            {t("applications:detail")}
                          </Button>
                          {model.status === "STAGING" || model.status === "DRAFT" ? (
                            <Button
                              variant="secondary"
                              loading={busy}
                              onClick={() => void handlePromote(model)}
                              leftIcon={<ArrowUp aria-hidden className="h-3.5 w-3.5" />}
                            >
                              {t("common:actions.promote")}
                            </Button>
                          ) : model.status === "PRODUCTION" ? (
                            <Button
                              variant="secondary"
                              leftIcon={<Archive aria-hidden className="h-3.5 w-3.5" />}
                            >
                              {t("common:actions.archive")}
                            </Button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </PageState>

      <Modal
        open={selected !== null}
        onClose={() => setSelected(null)}
        title={t("models:detail.title")}
        size="lg"
      >
        {selected ? (
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-h2 text-primary-900">{selected.name}</p>
                <p className="text-body-sm text-primary-500">v{selected.version}</p>
              </div>
              <Badge variant={statusVariant[selected.status]}>
                {t(`models:statusLabel.${selected.status}`)}
              </Badge>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Stat label={t("models:columns.auc")} value={selected.auc.toFixed(4)} />
              <Stat label="Brier" value={selected.brier_score?.toFixed(4) ?? "–"} />
              <Stat label={t("models:columns.featureSet")} value={selected.feature_set_id} />
              <Stat label="Stage" value={selected.stage} />
            </div>
            <div>
              <h3 className="mb-1 text-label uppercase text-primary-500">
                {t("models:detail.features")}
              </h3>
              <p className="text-body-sm text-primary-700">
                {(selected.metrics ? Object.keys(selected.metrics) : []).join(", ") || "—"}
              </p>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <p className="text-label uppercase text-primary-500">{label}</p>
      <p className="mt-0.5 text-body font-semibold text-primary-900">{value}</p>
    </div>
  );
}
