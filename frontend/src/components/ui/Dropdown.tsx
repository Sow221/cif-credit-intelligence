import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { cx } from "@/utils/cx";

export interface DropdownItem {
  label: string;
  icon?: ReactNode;
  onSelect?: () => void;
  danger?: boolean;
}

interface DropdownProps {
  trigger: ReactNode;
  items: DropdownItem[];
  align?: "left" | "right";
  ariaLabel?: string;
}

export function Dropdown({ trigger, items, align = "left", ariaLabel }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    function handleKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKey);
    };
  }, []);

  return (
    <div ref={containerRef} className="relative inline-flex">
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={ariaLabel}
        onClick={() => setOpen((value) => !value)}
        className="focus-ring rounded-md"
      >
        {trigger}
      </button>
      {open ? (
        <div
          role="menu"
          className={cx(
            "absolute z-30 mt-1 min-w-44 rounded-md border border-border bg-surface py-1 shadow-md animate-pop-in",
            align === "right" ? "right-0" : "left-0",
          )}
        >
          {items.map((item) => (
            <button
              key={item.label}
              type="button"
              role="menuitem"
              onClick={() => {
                setOpen(false);
                item.onSelect?.();
              }}
              className={cx(
                "flex w-full items-center gap-2 px-3 py-2 text-body text-left transition-colors duration-fast hover:bg-primary-100",
                item.danger && "text-danger-600",
              )}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
