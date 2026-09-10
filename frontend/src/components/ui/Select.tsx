import { forwardRef, useId } from "react";
import type { SelectHTMLAttributes } from "react";
import { ChevronDown } from "lucide-react";
import { cx } from "@/utils/cx";

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options?: SelectOption[];
  error?: string;
  helper?: string;
  placeholder?: string;
}

const baseSelect =
  "input-base appearance-none pr-9 focus:ring-3 focus:ring-accent-600/10 disabled:cursor-not-allowed disabled:bg-primary-100";
const errorSelect = "border-danger-600 focus:border-danger-600 focus:ring-danger-600/10";
const emptySelect = "text-primary-400";

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, options = [], error, helper, placeholder, className, id, value, ...rest },
  ref,
) {
  const autoId = useId();
  const selectId = id ?? autoId;

  return (
    <div className="flex w-full flex-col gap-1.5">
      {label ? (
        <label htmlFor={selectId} className="text-label text-primary-900">
          {label}
        </label>
      ) : null}
      <div className="relative">
        <select
          ref={ref}
          id={selectId}
          value={value ?? ""}
          aria-invalid={error ? true : undefined}
          className={cx(baseSelect, value === "" && emptySelect, error && errorSelect, className)}
          {...rest}
        >
          {placeholder ? (
            <option value="" disabled>
              {placeholder}
            </option>
          ) : null}
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown
          aria-hidden
          className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary-400"
        />
      </div>
      {error ? (
        <p role="alert" className="text-label text-danger-600">
          {error}
        </p>
      ) : helper ? (
        <p className="text-label text-primary-500">{helper}</p>
      ) : null}
    </div>
  );
});
