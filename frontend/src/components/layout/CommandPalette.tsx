import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { FileText, Users, Search, Plus } from "lucide-react";
import { useDataStore } from "@/store/data";
import { Avatar } from "@/components/ui/Avatar";
import { cx } from "@/utils/cx";
import { formatCurrency } from "@/utils/format";

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
}

interface ResultItem {
  id: string;
  category: string;
  label: string;
  description?: string;
  href?: string;
  action?: () => void;
}

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const applications = useDataStore((state) => state.applications);
  const clients = useDataStore((state) => state.clients);

  useEffect(() => {
    if (open) {
      setQuery("");
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    function handleKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  const results = useMemo<ResultItem[]>(() => {
    const q = query.trim().toLowerCase();
    const categories: ResultItem[] = [];

    if (q === "") {
      categories.push({
        id: "action-new",
        category: "action",
        label: t("common:actions.newApplication"),
        href: "/applications/new",
        action: () => navigate("/applications/new"),
      });
      categories.push({
        id: "action-client",
        category: "action",
        label: t("common:actions.newClient"),
        href: "/clients",
        action: () => navigate("/clients"),
      });
      return categories;
    }

    for (const client of clients) {
      const name = `${client.first_name} ${client.last_name}`.toLowerCase();
      if (name.includes(q)) {
        categories.push({
          id: `client-${client.client_id}`,
          category: "client",
          label: `${client.first_name} ${client.last_name}`,
          description: client.zone ?? client.phone ?? undefined,
          href: `/clients/${client.client_id}`,
          action: () => navigate(`/clients/${client.client_id}`),
        });
      }
    }
    for (const app of applications) {
      if (app.application_id.toLowerCase().includes(q)) {
        categories.push({
          id: `application-${app.application_id}`,
          category: "application",
          label: app.application_id.slice(0, 8).toUpperCase(),
          description: `${formatCurrency(app.requested_amount, app.currency)} — ${app.status}`,
          href: `/applications/${app.application_id}`,
          action: () => navigate(`/applications/${app.application_id}`),
        });
      }
    }
    return categories.slice(0, 12);
  }, [query, applications, clients, t, navigate]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  if (!open) return null;

  function handleKey(event: React.KeyboardEvent) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setSelectedIndex((index) => Math.min(index + 1, results.length - 1));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setSelectedIndex((index) => Math.max(index - 1, 0));
    } else if (event.key === "Enter") {
      const item = results[selectedIndex];
      if (item) {
        onClose();
        item.action?.();
      }
    }
  }

  const categoryLabel = (cat: string) => {
    if (cat === "client") return t("common:nav.clients");
    if (cat === "application") return t("common:nav.applications");
    return t("common:actions.search");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-[15vh]">
      <div
        aria-hidden
        onClick={onClose}
        className="absolute inset-0 bg-primary-900/50 animate-fade-in"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t("common:actions.search")}
        className="relative w-full max-w-lg overflow-hidden rounded-lg bg-surface shadow-lg animate-pop-in"
      >
        <div className="border-b border-border">
          <div className="flex items-center gap-3 px-4">
            <Search aria-hidden className="h-4 w-4 shrink-0 text-primary-400" />
            <input
              ref={inputRef}
              role="searchbox"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={handleKey}
              placeholder={t("common:actions.search")}
              className="h-12 w-full bg-transparent text-body text-primary-900 placeholder:text-primary-400 focus:outline-none"
            />
          </div>
        </div>
        <ul role="listbox" className="max-h-80 overflow-y-auto py-2">
          {results.length === 0 ? (
            <li className="px-4 py-6 text-center text-body-sm text-primary-500">
              {t("common:empty.applications")}
            </li>
          ) : (
            results.map((item, index) => (
              <li key={item.id} role="option" aria-selected={index === selectedIndex}>
                <button
                  type="button"
                  onClick={() => {
                    onClose();
                    item.action?.();
                  }}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={cx(
                    "flex w-full items-center gap-3 px-4 py-2.5 text-left",
                    index === selectedIndex && "bg-accent-50",
                  )}
                >
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary-100 text-primary-500">
                    {item.category === "client" ? (
                      <Avatar name={item.label} size="sm" />
                    ) : item.category === "application" ? (
                      <FileText aria-hidden className="h-4 w-4" />
                    ) : item.action ? (
                      <Plus aria-hidden className="h-4 w-4" />
                    ) : (
                      <Users aria-hidden className="h-4 w-4" />
                    )}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-body font-medium text-primary-900">
                      {item.label}
                    </span>
                    {item.description ? (
                      <span className="block truncate text-label text-primary-500">
                        {item.description}
                      </span>
                    ) : null}
                  </span>
                  <span className="shrink-0 text-label uppercase text-primary-400">
                    {categoryLabel(item.category)}
                  </span>
                </button>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}
