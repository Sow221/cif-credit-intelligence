const currencyLocale: Record<string, string> = {
  XOF: "fr-FR",
  USD: "en-US",
  EUR: "fr-FR",
};

function safeLocale(currency?: string): string {
  return currencyLocale[currency ?? "XOF"] ?? "fr-FR";
}

export function formatCurrency(amount: number, currency = "XOF"): string {
  return new Intl.NumberFormat(safeLocale(currency), {
    style: "currency",
    currency,
    maximumFractionDigits: amount % 1 === 0 ? 0 : 2,
  }).format(amount);
}

export function formatPercent(value: number, digits = 1): string {
  const v = Number.isFinite(value) ? value : 0;
  return `${(v * 100).toFixed(digits)} %`;
}

export function formatNumber(value: number, digits = 0): string {
  return new Intl.NumberFormat("fr-FR", {
    maximumFractionDigits: digits,
  }).format(value);
}

export function formatDate(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

export function formatDateTime(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function formatRelativeTime(value: string, now = new Date()): string {
  const date = new Date(value);
  const diffMs = now.getTime() - date.getTime();
  const minutes = Math.floor(diffMs / 60_000);
  if (minutes < 1) return "à l'instant";
  if (minutes < 60) return `il y a ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `il y a ${hours} h`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `il y a ${days} j`;
  return formatDate(date);
}

export function formatUuid(value: string): string {
  if (value.length !== 36) return value;
  return `${value.slice(0, 8).toUpperCase()}`;
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}
