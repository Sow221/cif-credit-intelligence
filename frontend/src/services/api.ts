import { API_BASE_URL } from "@/utils/constants";

export type HttpMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

export interface StandardErrorBody {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: unknown;

  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export interface RequestOptions {
  method?: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
  idempotencyKey?: string;
}

const TOKEN_KEY = "cif_access_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function parseError(res: Response): Promise<Error> {
  let code = `HTTP_${res.status}`;
  let message = `Request failed with status ${res.status}`;
  let details: unknown;
  try {
    const data = (await res.json()) as StandardErrorBody | { detail?: string; message?: string };
    const errorBody = (data as StandardErrorBody).error;
    if (errorBody && typeof errorBody === "object") {
      code = errorBody.code;
      message = errorBody.message;
      details = errorBody.details;
    } else {
      const detail = (data as { detail?: string }).detail ?? (data as { message?: string }).message;
      if (detail) message = detail;
    }
  } catch {
    // body not JSON, keep defaults
  }
  return new ApiError(res.status, code, message, details);
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, headers, idempotencyKey } = options;
  const token = getToken();
  const finalHeaders: Record<string, string> = {
    Accept: "application/json",
    ...headers,
  };
  if (body !== undefined) {
    finalHeaders["Content-Type"] = "application/json";
  }
  if (token) {
    finalHeaders["Authorization"] = `Bearer ${token}`;
  }
  if (idempotencyKey) {
    finalHeaders["Idempotency-Key"] = idempotencyKey;
  }

  const init: RequestInit = {
    method,
    headers: finalHeaders,
  };
  if (body !== undefined) {
    init.body = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE_URL}${path}`, init);

  if (res.status === 204) {
    return undefined as T;
  }
  if (!res.ok) {
    throw await parseError(res);
  }
  return (await res.json()) as T;
}

export const api = {
  get<T>(path: string, headers?: Record<string, string>): Promise<T> {
    return request<T>(path, headers ? { method: "GET", headers } : { method: "GET" });
  },
  post<T>(path: string, body?: unknown, opts: RequestOptions = {}): Promise<T> {
    return request<T>(path, { ...opts, method: "POST", ...(body !== undefined ? { body } : {}) });
  },
  patch<T>(path: string, body?: unknown, opts: RequestOptions = {}): Promise<T> {
    return request<T>(path, { ...opts, method: "PATCH", ...(body !== undefined ? { body } : {}) });
  },
  delete<T>(path: string, headers?: Record<string, string>): Promise<T> {
    return request<T>(path, headers ? { method: "DELETE", headers } : { method: "DELETE" });
  },
};
