import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { useClients } from "@/hooks/useClients";
import { PageState } from "@/components/shared/PageState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Pagination } from "@/components/ui/Pagination";
import { EmptyState } from "@/components/ui/EmptyState";
import { SearchBar } from "@/components/ui/SearchBar";
import { Avatar } from "@/components/ui/Avatar";

const statusBadge = { ACTIVE: "success", BLOCKED: "danger", PENDING: "warning" } as const;

export default function ClientsListPage() {
  const { t } = useTranslation();
  const { clients, status, error, reload } = useClients();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return clients;
    return clients.filter((client) =>
      `${client.first_name} ${client.last_name} ${client.phone ?? ""} ${client.client_id}`
        .toLowerCase()
        .includes(q),
    );
  }, [clients, search]);

  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-h1 text-primary-900">{t("clients:title")}</h1>
        <Link to="/clients">
          <span className="inline-flex h-10 items-center gap-2 rounded-md bg-accent-600 px-4 font-button text-white transition-colors duration-fast hover:bg-accent-700 focus-ring">
            <Plus aria-hidden className="h-4 w-4" />
            {t("common:actions.newClient")}
          </span>
        </Link>
      </div>

      <Card padded={false}>
        <div className="border-b border-border p-4">
          <SearchBar
            value={search}
            onChange={(value) => {
              setSearch(value);
              setPage(1);
            }}
            placeholder={t("clients:search")}
            className="max-w-md"
          />
        </div>

        <PageState
          status={status}
          error={error}
          onRetry={reload}
          defaultEmptyTitle={t("common:empty.clients")}
        >
          {filtered.length === 0 ? (
            <EmptyState title={t("common:empty.clients")} />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-background">
                    <th scope="col" className="table-header-cell">
                      {t("clients:columns.id")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("clients:columns.name")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("clients:columns.sector")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("clients:columns.zone")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("clients:columns.status")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("clients:columns.applications")}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paged.map((client) => (
                    <tr
                      key={client.client_id}
                      className="border-b border-border transition-colors duration-fast hover:bg-primary-50"
                    >
                      <td className="table-cell font-medium">
                        {client.client_id.slice(0, 8).toUpperCase()}
                      </td>
                      <td className="table-cell">
                        <Link
                          to={`/clients/${client.client_id}`}
                          className="flex items-center gap-2 font-medium text-primary-900 hover:text-accent-600 focus-ring"
                        >
                          <Avatar name={`${client.first_name} ${client.last_name}`} size="sm" />
                          {client.first_name} {client.last_name}
                        </Link>
                      </td>
                      <td className="table-cell text-primary-500">{client.sector ?? "–"}</td>
                      <td className="table-cell text-primary-500">{client.zone ?? "–"}</td>
                      <td className="table-cell">
                        <Badge variant={statusBadge[client.status]}>
                          {t(`clients:statusLabel.${client.status}`)}
                        </Badge>
                      </td>
                      <td className="table-cell text-primary-500">—</td>
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
              onPageSizeChange={setPageSize}
            />
          </div>
        </PageState>
      </Card>
    </div>
  );
}
