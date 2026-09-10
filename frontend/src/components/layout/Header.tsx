import { useTranslation } from "react-i18next";
import { Breadcrumb } from "./Breadcrumb";
import { NotificationsDropdown } from "./NotificationsDropdown";
import { UserDropdown } from "./UserDropdown";
import { SearchBar } from "@/components/ui/SearchBar";

interface HeaderProps {
  onOpenCommandPalette: () => void;
  query: string;
  setQuery: (value: string) => void;
}

export function Header({ onOpenCommandPalette, query, setQuery }: HeaderProps) {
  const { t } = useTranslation();

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-border bg-surface px-6">
      <div className="min-w-0 flex-1">
        <Breadcrumb />
      </div>

      <div className="relative hidden w-80 md:block">
        <SearchBar
          value={query}
          onChange={setQuery}
          placeholder={t("common:actions.search")}
          ariaLabel={t("common:actions.search")}
          onFocus={onOpenCommandPalette}
          className="w-full"
        />
        <kbd
          aria-hidden
          className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rounded border border-border bg-primary-50 px-1.5 py-0.5 text-label text-primary-500"
        >
          ⌘K
        </kbd>
      </div>

      <div className="flex items-center gap-1">
        <NotificationsDropdown />
        <UserDropdown />
      </div>
    </header>
  );
}
