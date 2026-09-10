import { useLocation } from "react-router-dom";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

const TITLE_BY_PATH: Array<[string, string]> = [
  ["/dashboard", "dashboard"],
  ["/applications/new", "applications"],
  ["/applications", "applications"],
  ["/clients", "clients"],
  ["/review", "review"],
  ["/models", "models"],
  ["/monitoring", "monitoring"],
  ["/admin", "admin"],
];

export function Breadcrumb() {
  const { t } = useTranslation();
  const location = useLocation();

  const { matchesTitle, crumbs } = useMemo(() => {
    const parts = location.pathname.split("/").filter(Boolean);
    const match = TITLE_BY_PATH.find(([prefix]) => location.pathname.startsWith(prefix)) ?? null;
    const isDetail = location.pathname.startsWith("/applications/") && parts.length >= 2;
    const isClientDetail =
      location.pathname.startsWith("/clients/") && parts.length >= 2 && parts[1] !== "new";
    const matchesTitle = !isDetail && !isClientDetail && match !== null;
    const crumbs: string[] = [];
    if (isDetail) {
      crumbs.push(t("common:nav.applications"));
      crumbs.push("…");
    } else if (isClientDetail) {
      crumbs.push(t("common:nav.clients"));
      crumbs.push("…");
    } else if (match) {
      crumbs.push(t(`common:nav.${match[1]}`));
    } else {
      crumbs.push("Adaptive Credit");
    }
    return { matchesTitle, crumbs };
  }, [location, t]);

  const title = useMemo(() => {
    if (
      location.pathname.startsWith("/applications/") &&
      location.pathname !== "/applications/new"
    ) {
      return t("applications:title");
    }
    const match = TITLE_BY_PATH.find(([prefix]) => location.pathname.startsWith(prefix));
    if (!match) return t("common:app.name");
    if (match[1] === "dashboard") return t("dashboard:greeting");
    return t(`common:nav.${match[1]}`);
  }, [location, t]);

  return (
    <div>
      <nav aria-label="Fil d'Ariane" className="text-label uppercase text-primary-500">
        {crumbs.join(" / ")}
      </nav>
      {matchesTitle ? <h1 className="mt-0.5 text-h2 text-primary-900">{title}</h1> : null}
    </div>
  );
}
