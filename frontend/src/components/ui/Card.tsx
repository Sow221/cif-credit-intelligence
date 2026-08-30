import { cn } from "../../utils/cn";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
}

export function Card({ title, className, children, ...props }: CardProps) {
  return (
    <div
      className={cn("rounded-lg border border-gray-200 bg-white p-5 shadow-sm", className)}
      {...props}
    >
      {title && <h3 className="mb-3 text-base font-semibold text-gray-800">{title}</h3>}
      {children}
    </div>
  );
}
