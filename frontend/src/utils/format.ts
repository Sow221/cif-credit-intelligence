/** Formate une probabilite de defaut (0..1) en pourcentage. */
export function formatPd(pd: number | null): string {
  if (pd === null || Number.isNaN(pd)) return "—";
  return `${(pd * 100).toFixed(1)}%`;
}

/** Formate un montant (FCFA) avec separateur de milliers. */
export function formatCurrency(value: number): string {
  if (Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(value) + " F";
}

/** Formate une date ISO locale au format JJ/MM/AAAA HH:mm. */
export function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
}
