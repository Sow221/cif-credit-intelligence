import { useRef, useState } from "react";
import { Search, X } from "lucide-react";
import { cx } from "@/utils/cx";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onFocus?: () => void;
  className?: string;
  ariaLabel?: string;
}

export function SearchBar({
  value,
  onChange,
  placeholder,
  onFocus,
  className,
  ariaLabel,
}: SearchBarProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [focused, setFocused] = useState(false);

  return (
    <div
      className={cx(
        "relative flex h-10 items-center rounded-md border transition-colors duration-fast",
        focused ? "border-accent-600 ring-3 ring-accent-600/10" : "border-border",
        className,
      )}
    >
      <Search
        aria-hidden
        className="pointer-events-none absolute left-3 h-4 w-4 text-primary-400"
      />
      <input
        ref={inputRef}
        type="search"
        role="searchbox"
        aria-label={ariaLabel}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        onFocus={() => {
          setFocused(true);
          onFocus?.();
        }}
        onBlur={() => setFocused(false)}
        className="h-full w-full bg-transparent pl-9 pr-8 text-body text-primary-900 placeholder:text-primary-400 focus:outline-none"
      />
      {value ? (
        <button
          type="button"
          aria-label="Effacer"
          onClick={() => {
            onChange("");
            inputRef.current?.focus();
          }}
          className="absolute right-2 rounded-sm text-primary-400 hover:text-primary-600 focus-ring"
        >
          <X aria-hidden className="h-4 w-4" />
        </button>
      ) : null}
    </div>
  );
}
