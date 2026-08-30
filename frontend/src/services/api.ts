import type {
  AuditItem,
  DecisionItem,
  ListResponse,
  ModelItem,
  OverrideRequest,
  PredictionRequest,
  PredictionResponse,
} from "../types/prediction";
import { getSession, clearSession } from "./auth";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const session = getSession();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (session) {
    headers.Authorization = `Bearer ${session.token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  if (response.status === 401) {
    clearSession();
  }

  if (!response.ok) {
    let detail = `Erreur ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail ?? detail;
    } catch {
      // corps non JSON, garder le message par defaut
    }
    throw new ApiError(response.status, detail);
  }

  return (await response.json()) as T;
}

export const api = {
  predict: (payload: PredictionRequest) =>
    request<PredictionResponse>("/v1/predict", { method: "POST", body: payload }),

  listDecisions: () => request<ListResponse<DecisionItem>>("/v1/decisions"),

  getDecision: (id: string) => request<DecisionItem>(`/v1/decisions/${id}`),

  overrideDecision: (id: string, body: OverrideRequest) =>
    request<{ status: string; audit_id: string }>(`/v1/decisions/${id}/override`, {
      method: "POST",
      body,
    }),

  listAudit: () => request<ListResponse<AuditItem>>("/v1/audit"),

  listModels: () => request<{ items: ModelItem[] }>("/v1/models"),

  driftReport: () => request<Record<string, unknown>>("/v1/reports/drift"),
};
