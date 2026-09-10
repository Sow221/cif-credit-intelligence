import { useState } from "react";
import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { cx } from "@/utils/cx";

interface AccordionItemProps {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
}

export function AccordionItem({ title, children, defaultOpen = false }: AccordionItemProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="overflow-hidden rounded-md border border-border bg-surface">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-body font-semibold text-primary-900 transition-colors duration-fast hover:bg-primary-50 focus-ring"
      >
        {title}
        <ChevronDown
          aria-hidden
          className={cx(
            "h-4 w-4 text-primary-500 transition-transform duration-base",
            open && "rotate-180",
          )}
        />
      </button>
      {open ? <div className="border-t border-border p-4">{children}</div> : null}
    </div>
  );
}

interface AccordionProps {
  items: Array<{ title: string; content: ReactNode; defaultOpen?: boolean }>;
}

export function Accordion({ items }: AccordionProps) {
  return (
    <div className="flex flex-col gap-2">
      {items.map((item) => (
        <AccordionItem key={item.title} title={item.title} defaultOpen={item.defaultOpen}>
          {item.content}
        </AccordionItem>
      ))}
    </div>
  );
}
