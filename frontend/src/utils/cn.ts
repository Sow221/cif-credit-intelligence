/** Combine plusieurs classes Tailwind en filtrant les valeurs non vides. */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}
