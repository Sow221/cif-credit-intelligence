import { useNavigate } from "react-router-dom";
import { Bell } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useNotifications } from "@/hooks/useNotifications";
import { Dropdown } from "@/components/ui/Dropdown";

export function NotificationsDropdown() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { items, unreadCount, markAllRead, markRead } = useNotifications();
  const openItems = items.slice(0, 10);

  return (
    <Dropdown
      ariaLabel={t("common:actions.viewAll")}
      trigger={
        <span className="relative flex h-10 w-10 items-center justify-center rounded-md text-primary-500 transition-colors duration-fast hover:bg-primary-100">
          <Bell aria-hidden className="h-5 w-5" />
          {unreadCount > 0 ? (
            <span
              aria-label={`${unreadCount} notifications non lues`}
              className="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-danger-600 px-1 text-label text-white"
            >
              {unreadCount}
            </span>
          ) : null}
        </span>
      }
      align="right"
      items={
        openItems.length === 0
          ? [{ label: t("common:empty.events") }]
          : [
              ...openItems.map((item) => ({
                label: item.title,
                onSelect: () => {
                  markRead(item.id);
                  if (item.link) navigate(item.link);
                },
              })),
              ...(unreadCount > 0
                ? [{ label: t("common:actions.markAllRead"), onSelect: markAllRead }]
                : []),
            ]
      }
    />
  );
}
