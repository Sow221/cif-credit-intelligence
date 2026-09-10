import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { Eye, Plus } from "lucide-react";
import { useApplications } from "@/hooks/useApplications";
import { PageState } from "@/components/shared/PageState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { Pagination } from "@/components/ui/Pagination";
import { EmptyState } from "@/components/ui/EmptyState";
import { SearchBar } from "@/components/ui/SearchBar";
import type { Application, ApplicationFilters } from "@/types/application";
import { statusBadgeVariant } from "@/utils/constants";
import { formatCurrency, formatDate } from "@/utils/format";

type PageSize = 10 | 25 | 50;

const statusOptions = [
  { value: "", label: "" },
  { value: "SUBMITTED", label: "Soumise" },
  { value: "REVIEW", label: "En revue" },
  { value: "APPROVE", label: "Approuvée" },
  { value: "DECLINE", label: "Refusée" },
  { value: "DECIDED", label: "Décidée" },
];

const productOptions = [
  { value: "", label: "" },
  { value: "SMALL_BUSINESS", label: "Petit commerce" },
  { value: "PERSONAL", label: "Personnel" },
  { value: "AGRICULTURE", label: "Agriculture" },
];

const infoStateOptions = [
  { value: "", label: "" },
  { value: "FULL_FILE", label: "Complet" },
  { value: "THIN_FILE", label: "Faible" },
  { value: "NO_FILE", label: "Absent" },
];

export default function ApplicationsListPage() {
  const { t } = useTranslation();
  const { applications, status, error, reload } = useApplications();

  const [filters, setFilters] = useState<ApplicationFilters>({
    status: "",
    risk_band: "",
    information_state: "",
    product_id: "",
    search: "",
  });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<PageSize>(10);

  const filtered = useMemo(() => {
    const q = (filters.search ?? "").trim().toLowerCase();
    return applications.filter((app) => {
      if (filters.status && app.status !== filters.status) return false;
      if (filters.product_id && app.product_id !== filters.product_id) return false;
      if (filters.information_state && (app.information_state ?? "") !== filters.information_state)
        return false;
      if (q) {
        const idMatch = app.application_id.toLowerCase().includes(q);
        const clientMatch = (app.client_name ?? "").toLowerCase().includes(q);
        if (!idMatch && !clientMatch) return false;
      }
      return true;
    });
  }, [applications, filters]);

  const paged = useMemo(
    () => filtered.slice((page - 1) * pageSize, page * pageSize),
    [filtered, page, pageSize],
  );

  function updateFilter(key: keyof ApplicationFilters, value: string) {
    setFilters((current) => ({ ...current, [key]: value }));
    setPage(1);
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-h1 text-primary-900">{t("applications:title")}</h1>
        <Link to="/applications/new">
          <Button leftIcon={<Plus aria-hidden className="h-4 w-4" />}>
            {t("common:actions.newApplication")}
          </Button>
        </Link>
      </div>

      <Card padded={false}>
        <div className="grid grid-cols-1 gap-3 border-b border-border p-4 md:grid-cols-2 lg:grid-cols-5">
          <Select
            aria-label={t("applications:filters.status")}
            label={t("applications:filters.status")}
            options={statusOptions}
            value={filters.status ?? ""}
            onChange={(event) => updateFilter("status", event.target.value)}
          />
          <Select
            aria-label={t("applications:filters.product")}
            label={t("applications:filters.product")}
            options={productOptions}
            value={filters.product_id ?? ""}
            onChange={(event) => updateFilter("product_id", event.target.value)}
          />
          <Select
            aria-label={t("applications:filters.infoState")}
            label={t("applications:filters.infoState")}
            options={infoStateOptions}
            value={filters.information_state ?? ""}
            onChange={(event) => updateFilter("information_state", event.target.value)}
          />
          <Input
            aria-label={t("applications:filters.date")}
            label={t("applications:filters.date")}
            type="date"
            value={filters.date_from ?? ""}
            onChange={(event) => updateFilter("date_from", event.target.value)}
          />
          <div className="flex items-end">
            <SearchBar
              value={filters.search ?? ""}
              onChange={(value) => updateFilter("search", value)}
              placeholder={t("applications:filters.search")}
              className="w-full"
            />
          </div>
        </div>

        <PageState
          status={status}
          error={error}
          onRetry={reload}
          defaultEmptyTitle={t("common:empty.applications")}
        >
          {filtered.length === 0 ? (
            <EmptyState title={t("common:empty.applications")} />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-background">
                    <th scope="col" className="table-header-cell">
                      {t("applications:columns.id")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("applications:columns.client")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("applications:columns.amount")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("applications:columns.pd")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("applications:columns.status")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("applications:columns.infoState")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("applications:columns.date")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("applications:columns.actions")}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paged.map((app: Application) => (
                    <tr
                      key={app.application_id}
                      className="border-b border-border transition-colors duration-fast hover:bg-primary-50"
                    >
                      <td className="table-cell font-medium">
                        {app.application_id.slice(0, 8).toUpperCase()}
                      </td>
                      <td className="table-cell">{app.client_name ?? app.client_id.slice(0, 8)}</td>
                      <td className="table-cell">
                        {formatCurrency(app.requested_amount, app.currency)}
                      </td>
                      <td className="table-cell text-primary-600">
                        {app.risk ? app.risk.pd_raw.toFixed(3) : "–"}
                      </td>
                      <td className="table-cell">
                        <Badge variant={statusBadgeVariant(app.status)}>
                          {t(`common:status.${app.status}`)}
                        </Badge>
                      </td>
                      <td className="table-cell text-primary-500">
                        {app.information_state ?? "–"}
                      </td>
                      <td className="table-cell text-primary-500">
                        {formatDate(app.application_timestamp)}
                      </td>
                      <td className="table-cell">
                        <Link
                          to={`/applications/${app.application_id}`}
                          aria-label={t("applications:detail")}
                          className="inline-flex h-8 w-8 items-center justify-center rounded-md text-primary-500 transition-colors duration-fast hover:bg-primary-100 hover:text-primary-900 focus-ring"
                        >
                          <Eye aria-hidden className="h-4 w-4" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div className="px-4 pb-4">
            <Pagination
              page={page}
              pageSize={pageSize}
              total={filtered.length}
              onPageChange={setPage}
              onPageSizeChange={(size) => {
                setPageSize(size as PageSize);
                setPage(1);
              }}
            />
          </div>
        </PageState>
      </Card>
    </div>
  );
}
