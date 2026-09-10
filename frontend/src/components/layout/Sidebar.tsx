import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  Users,
  ClipboardCheck,
  Cpu,
  Activity,
  Settings,
  LogOut,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { useAuth } from "@/hooks/useAuth";
import { useReviews } from "@/hooks/useReviews";
import { cx } from "@/utils/cx";
import { Avatar } from "@/components/ui/Avatar";

const iconMap = {
  LayoutDashboard,
  FileText,
  Users,
  ClipboardCheck,
  Cpu,
  Activity,
  Settings,
};

const navItems = [
  { to: "/dashboard", key: "dashboard", icon: "LayoutDashboard" as const },
  { to: "/applications", key: "applications", icon: "FileText" as const },
  { to: "/clients", key: "clients", icon: "Users" as const },
  { to: "/review", key: "review", icon: "ClipboardCheck" as const, badge: true },
  { to: "/models", key: "models", icon: "Cpu" as const },
  { to: "/monitoring", key: "monitoring", icon: "Activity" as const },
  { to: "/admin", key: "admin", icon: "Settings" as const },
];

export function Sidebar() {
  const { t } = useTranslation();
  const { user, signOut } = useAuth();
  const { pendingCount } = useReviews();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-[260px] flex-col bg-primary-900">
      <div className="flex h-[60px] items-center gap-2 border-b border-primary-800 px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-accent-600 text-white">
          <Activity aria-hidden className="h-4 w-4" />
        </div>
        <div className="flex flex-col">
          <span className="text-body font-semibold text-white">{t("common:app.name")}</span>
          <span className="text-label text-primary-400">CIF Intelligence</span>
        </div>
      </div>

      <nav aria-label="Navigation principale" className="flex-1 overflow-y-auto py-2">
        <ul>
          {navItems.map((item) => {
            const Icon = iconMap[item.icon];
            return (
              <li key={item.to} className="px-2 py-0.5">
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    cx(
                      "flex h-10 items-center gap-3 rounded-md px-3 text-body transition-colors duration-fast",
                      isActive
                        ? "bg-accent-600/15 text-white"
                        : "text-primary-400 hover:bg-primary-800 hover:text-white",
                    )
                  }
                >
                  <Icon aria-hidden className="h-4 w-4" />
                  <span>{t(`common:nav.${item.key}`)}</span>
                  {item.badge && pendingCount > 0 ? (
                    <span
                      aria-label={`${pendingCount} en attente`}
                      className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-warning-600 px-1.5 text-label text-white"
                    >
                      {pendingCount}
                    </span>
                  ) : null}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="border-t border-primary-800 p-4">
        {user ? (
          <div className="flex items-center gap-3">
            <Avatar name={user.full_name} size="sm" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-body-sm font-medium text-white">{user.full_name}</p>
              <p className="truncate text-label text-primary-400">
                {t(`common:roles.${user.role}`)}
              </p>
            </div>
            <button
              type="button"
              onClick={signOut}
              aria-label={t("common:actions.logout")}
              className="rounded-md p-1.5 text-primary-400 transition-colors duration-fast hover:bg-primary-800 hover:text-white focus-ring"
            >
              <LogOut aria-hidden className="h-4 w-4" />
            </button>
          </div>
        ) : null}
      </div>
    </aside>
  );
}
