import { useTranslation } from "react-i18next";
import { useAuth } from "@/hooks/useAuth";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Tabs } from "@/components/ui/Tabs";
import { EmptyState } from "@/components/ui/EmptyState";

const demoUsers = [
  {
    name: "Awa Diallo",
    username: "awa.diallo",
    role: "ADMIN",
    institution: "CREDIT_MUTUEL",
    status: "active",
  },
  {
    name: "Moussa Sow",
    username: "moussa.sow",
    role: "CREDIT_MANAGER",
    institution: "CREDIT_MUTUEL",
    status: "active",
  },
  {
    name: "Fatou Ndiaye",
    username: "fatou.ndiaye",
    role: "CREDIT_OFFICER",
    institution: "CREDIT_MUTUEL",
    status: "active",
  },
];

const rolePermissions: Record<string, string[]> = {
  ADMIN: ["users:read", "users:write", "roles:manage", "policies:write", "*"],
  CREDIT_MANAGER: ["reviews:manage", "decisions:override", "applications:read", "models:promote"],
  CREDIT_OFFICER: ["applications:write", "clients:read", "clients:write"],
  ANALYST: ["applications:read", "models:read", "monitoring:read"],
  AUDITOR: ["audit:read", "monitoring:read"],
};

export default function AdminPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";

  const tabs = [
    {
      id: "users",
      label: t("admin:tabs.users"),
      content: (
        <Card padded={false}>
          {isAdmin ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-background">
                    <th scope="col" className="table-header-cell">
                      {t("admin:users.columns.name")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("admin:users.columns.username")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("admin:users.columns.role")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("admin:users.columns.institution")}
                    </th>
                    <th scope="col" className="table-header-cell">
                      {t("admin:users.columns.status")}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {demoUsers.map((row) => (
                    <tr
                      key={row.username}
                      className="border-b border-border transition-colors duration-fast hover:bg-primary-50"
                    >
                      <td className="table-cell font-medium">{row.name}</td>
                      <td className="table-cell text-primary-500">{row.username}</td>
                      <td className="table-cell">
                        <Badge variant={row.role === "ADMIN" ? "danger" : "info"}>
                          {t(`common:roles.${row.role}`)}
                        </Badge>
                      </td>
                      <td className="table-cell text-primary-500">{row.institution}</td>
                      <td className="table-cell">
                        <Badge variant={row.status === "active" ? "success" : "neutral"}>
                          {row.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState title={t("common:errors.forbidden")} />
          )}
        </Card>
      ),
    },
    {
      id: "roles",
      label: t("admin:tabs.roles"),
      content: (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {Object.entries(rolePermissions).map(([role, permissions]) => (
            <Card key={role} title={t(`common:roles.${role}`)}>
              <ul className="flex flex-wrap gap-1.5">
                {permissions.map((permission) => (
                  <li key={permission}>
                    <Badge variant="neutral">{permission}</Badge>
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      ),
    },
    {
      id: "policies",
      label: t("admin:tabs.policies"),
      content: <EmptyState title={t("admin:policies.description")} />,
    },
    {
      id: "config",
      label: t("admin:tabs.config"),
      content: <EmptyState title={t("admin:config.settings")} />,
    },
  ];

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-h1 text-primary-900">{t("admin:title")}</h1>
      <Tabs tabs={tabs} />
    </div>
  );
}
