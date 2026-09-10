import { ChevronLeft, ChevronRight } from "lucide-react";
import { cx } from "@/utils/cx";
import { PAGE_SIZE_OPTIONS } from "@/utils/constants";

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
}

export function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
  onPageSizeChange,
}: PaginationProps) {
  const pageCount = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(Math.max(page, 1), pageCount);

  function pages(): number[] {
    const list: number[] = [];
    for (let i = 1; i <= pageCount; i++) {
      if (i === 1 || i === pageCount || Math.abs(i - safePage) <= 1) {
        list.push(i);
      } else if (list[list.length - 1] !== 0) {
        list.push(0);
      }
    }
    return list;
  }

  return (
    <nav aria-label="Pagination" className="flex flex-wrap items-center justify-between gap-3 pt-4">
      <div className="flex items-center gap-2">
        <span className="text-body-sm text-primary-500">{total} · </span>
        <select
          aria-label="Taille de page"
          value={pageSize}
          onChange={(event) => onPageSizeChange(Number(event.target.value))}
          className="h-8 rounded-md border border-border bg-surface px-2 text-body-sm text-primary-700 focus-ring"
        >
          {PAGE_SIZE_OPTIONS.map((size) => (
            <option key={size} value={size}>
              {size} / page
            </option>
          ))}
        </select>
      </div>
      <div className="flex items-center gap-1">
        <button
          type="button"
          aria-label="Page précédente"
          disabled={safePage <= 1}
          onClick={() => onPageChange(safePage - 1)}
          className="flex h-8 items-center justify-center rounded-md border border-border bg-surface px-2 text-primary-600 transition-colors duration-fast hover:bg-primary-100 disabled:cursor-not-allowed disabled:opacity-40 focus-ring"
        >
          <ChevronLeft aria-hidden className="h-4 w-4" />
        </button>
        {pages().map((pageNumber, index) =>
          pageNumber === 0 ? (
            <span key={`ellipsis-${index}`} aria-hidden className="px-1 text-primary-400">
              …
            </span>
          ) : (
            <button
              key={pageNumber}
              type="button"
              aria-label={`Page ${pageNumber}`}
              aria-current={pageNumber === safePage ? "page" : undefined}
              onClick={() => onPageChange(pageNumber)}
              className={cx(
                "flex h-8 w-8 items-center justify-center rounded-md border text-body-sm transition-colors duration-fast focus-ring",
                pageNumber === safePage
                  ? "border-accent-600 bg-accent-600 text-white"
                  : "border-border bg-surface text-primary-700 hover:bg-primary-100",
              )}
            >
              {pageNumber}
            </button>
          ),
        )}
        <button
          type="button"
          aria-label="Page suivante"
          disabled={safePage >= pageCount}
          onClick={() => onPageChange(safePage + 1)}
          className="flex h-8 items-center justify-center rounded-md border border-border bg-surface px-2 text-primary-600 transition-colors duration-fast hover:bg-primary-100 disabled:cursor-not-allowed disabled:opacity-40 focus-ring"
        >
          <ChevronRight aria-hidden className="h-4 w-4" />
        </button>
      </div>
    </nav>
  );
}
