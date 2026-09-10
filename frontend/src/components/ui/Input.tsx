import { forwardRef, useId } from "react";
import type { InputHTMLAttributes } from "react";
import { cx } from "@/utils/cx";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helper?: string;
}

const baseInput =
  "input-base focus:ring-3 focus:ring-accent-600/10 disabled:cursor-not-allowed disabled:bg-primary-100";
const errorInput = "border-danger-600 focus:border-danger-600 focus:ring-danger-600/10";

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, helper, className, id, ...rest },
  ref,
) {
  const autoId = useId();
  const inputId = id ?? autoId;
  const describedBy = error ? `${inputId}-error` : helper ? `${inputId}-helper` : undefined;

  return (
    <div className="flex w-full flex-col gap-1.5">
      {label ? (
        <label htmlFor={inputId} className="text-label text-primary-900">
          {label}
        </label>
      ) : null}
      <input
        ref={ref}
        id={inputId}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        className={cx(baseInput, error && errorInput, error && "animate-shake-x", className)}
        {...rest}
      />
      {error ? (
        <p id={`${inputId}-error`} role="alert" className="text-label text-danger-600">
          {error}
        </p>
      ) : helper ? (
        <p id={`${inputId}-helper`} className="text-label text-primary-500">
          {helper}
        </p>
      ) : null}
    </div>
  );
});
