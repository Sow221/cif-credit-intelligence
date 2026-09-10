import type { ReactNode } from "react";
import type { LoadStatus } from "@/store/data";
import { SkeletonList } from "../ui/Skeleton";
import { ErrorState } from "../ui/ErrorState";
import { EmptyState } from "../ui/EmptyState";
import { useTranslation } from "react-i18next";

interface PageStateProps {
  status: LoadStatus | "forbidden";
  error?: string | null;
  onRetry?: () => void;
  emptyState?: ReactNode;
  defaultEmptyTitle?: string;
  defaultEmptyDescription?: string;
  children: ReactNode;
}

export function PageState({
  status,
  error,
  onRetry,
  emptyState,
  defaultEmptyTitle,
  defaultEmptyDescription,
  children,
}: PageStateProps) {
  const { t } = useTranslation();

  if (status === "forbidden") {
    return <ErrorState title={t("common:errors.forbidden")} />;
  }
  if (status === "loading") {
    return <SkeletonList rows={6} variant="card" />;
  }
  if (status === "error") {
    return (
      <ErrorState
        title={error ?? t("common:errors.title")}
        description={t("common:errors.description")}
        onRetry={onRetry}
      />
    );
  }
  if (status === "success") {
    if (emptyState) return <>{emptyState}</>;
    return <>{children}</>;
  }
  if (defaultEmptyTitle !== undefined) {
    return <EmptyState title={defaultEmptyTitle} description={defaultEmptyDescription} />;
  }
  return <>{children}</>;
}
