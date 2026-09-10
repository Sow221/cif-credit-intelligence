import type { HTMLAttributes, ReactNode } from "react";
import { cx } from "@/utils/cx";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  children?: ReactNode;
  padded?: boolean;
  className?: string;
}

export function Card({
  title,
  subtitle,
  actions,
  children,
  padded = true,
  className,
  ...rest
}: CardProps) {
  return (
    <div className={cx("card animate-slide-up", padded && "p-4", className)} {...rest}>
      {title ? (
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <h3 className="text-h3 text-primary-900">{title}</h3>
            {subtitle ? <p className="mt-0.5 text-body-sm text-primary-500">{subtitle}</p> : null}
          </div>
          {actions ? <div className="shrink-0">{actions}</div> : null}
        </div>
      ) : null}
      {children}
    </div>
  );
}
