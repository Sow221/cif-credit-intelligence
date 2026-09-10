import { useState } from "react";
import type { ReactNode } from "react";

interface TooltipProps {
  content: string;
  children: ReactNode;
  position?: "top" | "bottom" | "left" | "right";
}

export function Tooltip({ content, children, position = "top" }: TooltipProps) {
  const [visible, setVisible] = useState(false);
  const [timer, setTimer] = useState<ReturnType<typeof setTimeout> | null>(null);

  function show() {
    if (timer) clearTimeout(timer);
    setTimer(setTimeout(() => setVisible(true), 300));
  }

  function hide() {
    if (timer) clearTimeout(timer);
    setVisible(false);
  }

  const positionClasses: Record<string, string> = {
    top: "bottom-full left-1/2 mb-1 -translate-x-1/2",
    bottom: "top-full left-1/2 mt-1 -translate-x-1/2",
    left: "right-full top-1/2 mr-1 -translate-y-1/2",
    right: "left-full top-1/2 ml-1 -translate-y-1/2",
  };

  return (
    <span
      className="relative inline-flex"
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
    >
      {children}
      {visible ? (
        <span
          role="tooltip"
          className={`absolute z-30 whitespace-nowrap rounded-sm bg-primary-900 px-2.5 py-1.5 text-label text-white animate-fade-in ${positionClasses[position]}`}
        >
          {content}
        </span>
      ) : null}
    </span>
  );
}
