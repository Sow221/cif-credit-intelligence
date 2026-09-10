import { create } from "zustand";
import type { Application, ApplicationDetail, KpiSummary } from "@/types/application";
import type { Client, ClientDetail } from "@/types/client";
import type { Review } from "@/types/review";
import type { Model, ModelDetail } from "@/types/model";
import type { MonitoringSnapshot } from "@/types/monitoring";
import type { Decision, OverridePayload } from "@/types/decision";
import { api } from "@/services/api";

export type LoadStatus = "idle" | "loading" | "success" | "error";

interface DataState {
  applications: Application[];
  applicationsStatus: LoadStatus;
  applicationsError: string | null;
  totalApplications: number;
  currentApplication: ApplicationDetail | null;
  currentApplicationStatus: LoadStatus;
  currentApplicationError: string | null;
  clients: Client[];
  clientsStatus: LoadStatus;
  clientsError: string | null;
  currentClient: ClientDetail | null;
  currentClientStatus: LoadStatus;
  currentClientError: string | null;
  reviews: Review[];
  reviewsStatus: LoadStatus;
  reviewsError: string | null;
  models: Model[];
  modelsStatus: LoadStatus;
  modelsError: string | null;
  currentModel: ModelDetail | null;
  monitoring: MonitoringSnapshot | null;
  monitoringStatus: LoadStatus;
  kpis: KpiSummary | null;

  fetchApplications: (params?: Record<string, unknown>) => Promise<void>;
  fetchApplication: (id: string) => Promise<void>;
  createApplication: (payload: Record<string, unknown>) => Promise<Application>;
  updateApplicationStatus: (id: string, status: string) => Promise<void>;
  fetchClients: (params?: Record<string, unknown>) => Promise<void>;
  fetchClient: (id: string) => Promise<void>;
  createClient: (payload: Record<string, unknown>) => Promise<Client>;
  fetchReviews: (params?: Record<string, unknown>) => Promise<void>;
  assignReview: (id: string, assignedTo: string) => Promise<void>;
  startReview: (id: string) => Promise<void>;
  completeReview: (id: string, finalAction: string) => Promise<void>;
  fetchModels: () => Promise<void>;
  promoteModel: (id: string, action: string) => Promise<void>;
  fetchMonitoring: () => Promise<void>;
  createDecision: (applicationId: string) => Promise<Decision>;
  createOverride: (decisionId: string, payload: OverridePayload) => Promise<void>;
  clearState: () => void;
}

function queryString(params?: Record<string, unknown>): string {
  if (!params) return "";
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  }
  const str = search.toString();
  return str ? `?${str}` : "";
}

export const useDataStore = create<DataState>((set, get) => ({
  applications: [],
  applicationsStatus: "idle",
  applicationsError: null,
  totalApplications: 0,
  currentApplication: null,
  currentApplicationStatus: "idle",
  currentApplicationError: null,
  clients: [],
  clientsStatus: "idle",
  clientsError: null,
  currentClient: null,
  currentClientStatus: "idle",
  currentClientError: null,
  reviews: [],
  reviewsStatus: "idle",
  reviewsError: null,
  models: [],
  modelsStatus: "idle",
  modelsError: null,
  currentModel: null,
  monitoring: null,
  monitoringStatus: "idle",
  kpis: null,

  fetchApplications: async (params) => {
    set({ applicationsStatus: "loading", applicationsError: null });
    try {
      const data = await api.get<Application[]>(`/applications${queryString(params)}`);
      set({ applications: data, applicationsStatus: "success" });
    } catch (err) {
      set({
        applicationsStatus: "error",
        applicationsError: err instanceof Error ? err.message : "Unknown error",
      });
    }
  },

  fetchApplication: async (id) => {
    set({ currentApplicationStatus: "loading", currentApplicationError: null });
    try {
      const data = await api.get<ApplicationDetail>(`/applications/${id}`);
      set({ currentApplication: data, currentApplicationStatus: "success" });
    } catch (err) {
      set({
        currentApplicationStatus: "error",
        currentApplicationError: err instanceof Error ? err.message : "Unknown error",
      });
    }
  },

  createApplication: async (payload) => {
    const created = await api.post<Application>("/applications", payload);
    set((state) => ({ applications: [created, ...state.applications] }));
    return created;
  },

  updateApplicationStatus: async (id, status) => {
    await api.patch(`/applications/${id}/status`, { status });
    set((state) => ({
      applications: state.applications.map((app) =>
        app.application_id === id ? { ...app, status: status as typeof app.status } : app,
      ),
      currentApplication:
        state.currentApplication && state.currentApplication.application_id === id
          ? {
              ...state.currentApplication,
              status: status as typeof state.currentApplication.status,
            }
          : state.currentApplication,
    }));
  },

  fetchClients: async (params) => {
    set({ clientsStatus: "loading", clientsError: null });
    try {
      const data = await api.get<Client[]>(`/clients${queryString(params)}`);
      set({ clients: data, clientsStatus: "success" });
    } catch (err) {
      set({
        clientsStatus: "error",
        clientsError: err instanceof Error ? err.message : "Unknown error",
      });
    }
  },

  fetchClient: async (id) => {
    set({ currentClientStatus: "loading", currentClientError: null });
    try {
      const data = await api.get<ClientDetail>(`/clients/${id}`);
      set({ currentClient: data, currentClientStatus: "success" });
    } catch (err) {
      set({
        currentClientStatus: "error",
        currentClientError: err instanceof Error ? err.message : "Unknown error",
      });
    }
  },

  createClient: async (payload) => {
    const created = await api.post<Client>("/clients", payload);
    set((state) => ({ clients: [created, ...state.clients] }));
    return created;
  },

  fetchReviews: async (params) => {
    set({ reviewsStatus: "loading", reviewsError: null });
    try {
      const data = await api.get<Review[]>(`/reviews${queryString(params)}`);
      set({ reviews: data, reviewsStatus: "success" });
    } catch (err) {
      set({
        reviewsStatus: "error",
        reviewsError: err instanceof Error ? err.message : "Unknown error",
      });
    }
  },

  assignReview: async (id, assignedTo) => {
    const updated = await api.patch<Review>(`/reviews/${id}/assign`, { assigned_to: assignedTo });
    set((state) => ({
      reviews: state.reviews.map((review) => (review.review_id === id ? updated : review)),
    }));
  },

  startReview: async (id) => {
    const updated = await api.patch<Review>(`/reviews/${id}/start`, {});
    set((state) => ({
      reviews: state.reviews.map((review) => (review.review_id === id ? updated : review)),
    }));
  },

  completeReview: async (id, finalAction) => {
    const updated = await api.patch<Review>(`/reviews/${id}/complete`, {
      final_action: finalAction,
    });
    set((state) => ({
      reviews: state.reviews.map((review) => (review.review_id === id ? updated : review)),
    }));
  },

  fetchModels: async () => {
    set({ modelsStatus: "loading", modelsError: null });
    try {
      const data = await api.get<Model[]>("/models");
      set({ models: data, modelsStatus: "success" });
    } catch (err) {
      set({
        modelsStatus: "error",
        modelsError: err instanceof Error ? err.message : "Unknown error",
      });
    }
  },

  promoteModel: async (id, action) => {
    await api.post(`/models/${id}/status`, { action });
    await get().fetchModels();
  },

  fetchMonitoring: async () => {
    set({ monitoringStatus: "loading" });
    try {
      const data = await api.get<MonitoringSnapshot>("/monitoring");
      set({ monitoring: data, monitoringStatus: "success" });
    } catch {
      set({ monitoringStatus: "error" });
    }
  },

  createDecision: async (applicationId) => {
    return api.post<Decision>("/decisions", { application_id: applicationId });
  },

  createOverride: async (decisionId, payload) => {
    await api.post(`/decisions/${decisionId}/override`, payload);
  },

  clearState: () =>
    set({
      applications: [],
      applicationsStatus: "idle",
      clients: [],
      clientsStatus: "idle",
      reviews: [],
      reviewsStatus: "idle",
      models: [],
      modelsStatus: "idle",
      monitoring: null,
      monitoringStatus: "idle",
      currentApplication: null,
      currentClient: null,
    }),
}));
