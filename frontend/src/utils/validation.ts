export interface FieldError {
  field: string;
  message: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: FieldError[];
}

function requireField(value: unknown, field: string, message: string): FieldError | null {
  if (value === undefined || value === null || value === "") {
    return { field, message };
  }
  return null;
}

export function validateEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export function validatePhone(value: string): boolean {
  return /^\+?[0-9]{8,15}$/.test(value);
}

export function validateAmount(value: number): boolean {
  return Number.isFinite(value) && value > 0;
}

export function validateTerm(value: number): boolean {
  return [6, 12, 18, 24].includes(value);
}

export function validateRequired(value: unknown): boolean {
  return value !== undefined && value !== null && String(value).trim() !== "";
}

export interface LoginFields {
  username: string;
  password: string;
}

export function validateLogin(values: LoginFields): ValidationResult {
  const errors: FieldError[] = [];
  const u = requireField(values.username, "username", "common.errors.required");
  if (u) errors.push(u);
  const p = requireField(values.password, "password", "common.errors.required");
  if (p) errors.push(p);
  return { valid: errors.length === 0, errors };
}

export interface NewApplicationFields {
  client_id: string;
  product_id: string;
  requested_amount: number;
  requested_term: number;
  purpose?: string;
}

export function validateNewApplication(values: NewApplicationFields): ValidationResult {
  const errors: FieldError[] = [];
  errors.push(
    ...["client_id", "product_id"].flatMap((field) => {
      const err = requireField(
        values[field as keyof NewApplicationFields],
        field,
        "common.errors.required",
      );
      return err ? [err] : [];
    }),
  );
  if (!validateAmount(values.requested_amount)) {
    errors.push({ field: "requested_amount", message: "applications.errors.amount" });
  }
  if (!validateTerm(values.requested_term)) {
    errors.push({ field: "requested_term", message: "applications.errors.term" });
  }
  return { valid: errors.length === 0, errors };
}

export interface OverrideFormFields {
  final_decision: "APPROVE" | "DECLINE";
  override_reason: string;
}

export function validateOverride(values: OverrideFormFields): ValidationResult {
  const errors: FieldError[] = [];
  if (!validateRequired(values.override_reason)) {
    errors.push({ field: "override_reason", message: "applications.errors.overrideReason" });
  }
  if (values.final_decision !== "APPROVE" && values.final_decision !== "DECLINE") {
    errors.push({ field: "final_decision", message: "common.errors.required" });
  }
  return { valid: errors.length === 0, errors };
}
