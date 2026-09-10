import { useState } from "react";
import type { ReactNode } from "react";
import { cx } from "@/utils/cx";

export interface TabItem {
  id: string;
  label: string;
  badge?: number;
  content?: ReactNode;
}

interface TabsProps {
  tabs: TabItem[];
  activeId?: string;
  onChange?: (id: string) => void;
  ariaLabel?: string;
}

export function Tabs({ tabs, activeId, onChange, ariaLabel }: TabsProps) {
  const [internalActive, setInternalActive] = useState(activeId ?? tabs[0]?.id);
  const active = activeId ?? internalActive;

  function select(id: string) {
    setInternalActive(id);
    onChange?.(id);
  }

  return (
    <div>
      <div
        role="tablist"
        aria-label={ariaLabel}
        className="flex h-10 items-end gap-2 border-b border-border"
      >
        {tabs.map((tab) => {
          const isActive = tab.id === active;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              onClick={() => select(tab.id)}
              className={cx(
                "relative flex h-full items-center gap-1.5 px-4 text-body-sm transition-colors duration-fast focus-ring",
                isActive
                  ? "font-medium text-accent-600"
                  : "text-primary-500 hover:text-primary-700",
              )}
            >
              {tab.label}
              {tab.badge && tab.badge > 0 ? (
                <span
                  className={cx(
                    "flex min-w-5 items-center justify-center rounded-full px-1 text-label",
                    isActive ? "bg-accent-600 text-white" : "bg-primary-200 text-primary-600",
                  )}
                >
                  {tab.badge}
                </span>
              ) : null}
              {isActive ? (
                <span aria-hidden className="absolute inset-x-0 bottom-0 h-0.5 bg-accent-600" />
              ) : null}
            </button>
          );
        })}
      </div>
      <div role="tabpanel" className="pt-4">
        {tabs.find((tab) => tab.id === active)?.content}
      </div>
    </div>
  );
}
