import { beforeEach, describe, expect, it, vi } from "vitest";
import { useDataStore } from "./data";
import type { Application, ApplicationDetail, KpiSummary } from "@/types/application";
import type { Client } from "@/types/client";
import type { Decision } from "@/types/decision";
import type { Model } from "@/types/model";
import type { MonitoringSnapshot } from "@/types/monitoring";
import type { Review } from "@/types/review";

const mocks = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
}));

vi.mock("@/services/api", () => ({
  api: mocks,
}));

const application: Application = {
  application_id: "app-1",
  institution_id: "i1",
  client_id: "c1",
  product_id: "SMALL_BUSINESS",
  requested_amount: 250000,
  currency: "XOF",
  requested_term: 12,
  status: "SUBMITTED",
  application_timestamp: "2024-03-01T10:00:00Z",
  created_at: "2024-03-01T10:00:00Z",
  client_name: "Awa Diallo",
};

const client: Client = {
  client_id: "c1",
  institution_id: "i1",
  first_name: "Awa",
  last_name: "Diallo",
  status: "ACTIVE",
  created_at: "2024-03-01T10:00:00Z",
};

const review: Review = {
  review_id: "rev-1",
  application_id: "app-1",
  assigned_to: null,
  status: "PENDING",
  review_reason: "manual",
  final_action: null,
  started_at: null,
  completed_at: null,
};

const model: Model = {
  model_id: "mod-1",
  name: "GBM v2",
  version: "2.1.0",
  status: "STAGING",
  stage: "STAGING",
  auc: 0.82,
  brier_score: 0.12,
  feature_set_id: "CORE_25",
  trained_at: "2024-03-01T10:00:00Z",
  created_at: "2024-03-01T10:00:00Z",
};

const decision: Decision = {
  decision_id: "dec-1",
  application_id: "app-1",
  recommendation: "APPROVE",
  final_decision: null,
  proposed_amount: 250000,
  proposed_term: 12,
  decision_reason: null,
  policy_version: 3,
};

const monitoring: MonitoringSnapshot = {
  dataQuality: [{ feature: "age", completeness: 0.95, stability: 0.9, drift: 0.05 }],
  modelPerformance: {
    auc: 0.81,
    brier: 0.13,
    calibration_error: 0.02,
    ks: 0.35,
    gini: 0.62,
  },
  decisionStats: { APPROVE: 10, DECLINE: 5 },
  fairness: [{ group: "g1", sample_size: 100, approval_rate: 0.7, adverse_impact_ratio: 0.9 }],
  incidents: [],
};

function errorFixture(message: string): Error {
  return Object.assign(new Error(message), { name: "Error" });
}

describe("useDataStore", () => {
  beforeEach(() => {
    useDataStore.setState({
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
    });
    mocks.get.mockReset();
    mocks.post.mockReset();
    mocks.patch.mockReset();
  });

  it("fetchApplications builds a query string and stores results", async () => {
    mocks.get.mockResolvedValue([application]);
    await useDataStore.getState().fetchApplications({ status: "SUBMITTED", empty: "" });
    expect(mocks.get).toHaveBeenCalledWith("/applications?status=SUBMITTED");
    expect(useDataStore.getState().applications).toEqual([application]);
    expect(useDataStore.getState().applicationsStatus).toBe("success");
  });

  it("fetchApplications records errors", async () => {
    mocks.get.mockRejectedValue(errorFixture("network down"));
    await useDataStore.getState().fetchApplications();
    expect(useDataStore.getState().applicationsStatus).toBe("error");
    expect(useDataStore.getState().applicationsError).toBe("network down");
  });

  it("fetchApplication loads a single application", async () => {
    const detail: ApplicationDetail = { ...application, recommendation: "APPROVE" };
    mocks.get.mockResolvedValue(detail);
    await useDataStore.getState().fetchApplication("app-1");
    expect(mocks.get).toHaveBeenCalledWith("/applications/app-1");
    expect(useDataStore.getState().currentApplication?.recommendation).toBe("APPROVE");
    expect(useDataStore.getState().currentApplicationStatus).toBe("success");
  });

  it("fetchApplication records errors", async () => {
    mocks.get.mockRejectedValue(errorFixture("not found"));
    await useDataStore.getState().fetchApplication("nope");
    expect(useDataStore.getState().currentApplicationStatus).toBe("error");
    expect(useDataStore.getState().currentApplicationError).toBe("not found");
  });

  it("createApplication prepends the created application", async () => {
    useDataStore.setState({ applications: [application] });
    const created = { ...application, application_id: "app-2" };
    mocks.post.mockResolvedValue(created);
    const result = await useDataStore.getState().createApplication({ client_id: "c1" });
    expect(result.application_id).toBe("app-2");
    expect(useDataStore.getState().applications[0]?.application_id).toBe("app-2");
  });

  it("updateApplicationStatus patches list and current application", async () => {
    const detail: ApplicationDetail = { ...application, status: "SUBMITTED" };
    useDataStore.setState({ applications: [application], currentApplication: detail });
    mocks.patch.mockResolvedValue({});
    await useDataStore.getState().updateApplicationStatus("app-1", "REVIEW");
    expect(mocks.patch).toHaveBeenCalledWith("/applications/app-1/status", {
      status: "REVIEW",
    });
    expect(useDataStore.getState().applications[0]?.status).toBe("REVIEW");
    expect(useDataStore.getState().currentApplication?.status).toBe("REVIEW");
  });

  it("fetchClients / createClient", async () => {
    mocks.get.mockResolvedValue([client]);
    await useDataStore.getState().fetchClients({ status: "ACTIVE" });
    expect(mocks.get).toHaveBeenCalledWith("/clients?status=ACTIVE");
    expect(useDataStore.getState().clients).toEqual([client]);

    const created = { ...client, client_id: "c2" };
    mocks.post.mockResolvedValue(created);
    await useDataStore.getState().createClient({ first_name: "B" });
    expect(useDataStore.getState().clients[0]?.client_id).toBe("c2");
  });

  it("fetchClient stores detail", async () => {
    mocks.get.mockResolvedValue({ ...client, savings: { balance: 5 } });
    await useDataStore.getState().fetchClient("c1");
    expect(useDataStore.getState().currentClient?.client_id).toBe("c1");
    expect(useDataStore.getState().currentClientStatus).toBe("success");
  });

  it("fetchReviews and review mutations", async () => {
    mocks.get.mockResolvedValue([review]);
    await useDataStore.getState().fetchReviews();
    expect(useDataStore.getState().reviewsStatus).toBe("success");

    const assigned = { ...review, assigned_to: "u1", status: "ASSIGNED" as const };
    mocks.patch.mockResolvedValue(assigned);
    await useDataStore.getState().assignReview("rev-1", "u1");
    expect(mocks.patch).toHaveBeenCalledWith("/reviews/rev-1/assign", {
      assigned_to: "u1",
    });
    expect(useDataStore.getState().reviews[0]?.assigned_to).toBe("u1");

    mocks.patch.mockResolvedValue({ ...assigned, status: "IN_PROGRESS" });
    await useDataStore.getState().startReview("rev-1");
    expect(mocks.patch).toHaveBeenCalledWith("/reviews/rev-1/start", {});

    mocks.patch.mockResolvedValue({ ...assigned, status: "COMPLETED", final_action: "APPROVE" });
    await useDataStore.getState().completeReview("rev-1", "APPROVE");
    expect(useDataStore.getState().reviews[0]?.final_action).toBe("APPROVE");
  });

  it("fetchReviews records errors", async () => {
    mocks.get.mockRejectedValue(errorFixture("denied"));
    await useDataStore.getState().fetchReviews();
    expect(useDataStore.getState().reviewsStatus).toBe("error");
    expect(useDataStore.getState().reviewsError).toBe("denied");
  });

  it("fetchModels and promoteModel", async () => {
    mocks.get.mockResolvedValue([model]);
    await useDataStore.getState().fetchModels();
    expect(useDataStore.getState().models).toEqual([model]);

    mocks.post.mockResolvedValue({});
    await useDataStore.getState().promoteModel("mod-1", "PROMOTE");
    expect(mocks.post).toHaveBeenCalledWith("/models/mod-1/status", { action: "PROMOTE" });
    expect(useDataStore.getState().modelsStatus).toBe("success");
  });

  it("fetchModels records errors", async () => {
    mocks.get.mockRejectedValue(errorFixture("bad model"));
    await useDataStore.getState().fetchModels();
    expect(useDataStore.getState().modelsStatus).toBe("error");
  });

  it("fetchMonitoring stores snapshot and errors", async () => {
    mocks.get.mockResolvedValue(monitoring);
    await useDataStore.getState().fetchMonitoring();
    expect(useDataStore.getState().monitoring).toEqual(monitoring);
    expect(useDataStore.getState().monitoringStatus).toBe("success");

    mocks.get.mockRejectedValue(errorFixture("boom"));
    await useDataStore.getState().fetchMonitoring();
    expect(useDataStore.getState().monitoringStatus).toBe("error");
  });

  it("createDecision posts to /decisions", async () => {
    mocks.post.mockResolvedValue(decision);
    const result = await useDataStore.getState().createDecision("app-1");
    expect(mocks.post).toHaveBeenCalledWith("/decisions", { application_id: "app-1" });
    expect(result.recommendation).toBe("APPROVE");
  });

  it("createOverride posts the override payload", async () => {
    mocks.post.mockResolvedValue({});
    await useDataStore.getState().createOverride("dec-1", {
      final_decision: "DECLINE",
      override_reason: "fraud suspicion",
    });
    expect(mocks.post).toHaveBeenCalledWith("/decisions/dec-1/override", {
      final_decision: "DECLINE",
      override_reason: "fraud suspicion",
    });
  });

  it("clearState resets collections to idle", () => {
    useDataStore.setState({ applications: [application], applicationsStatus: "success" });
    useDataStore.getState().clearState();
    const state = useDataStore.getState();
    expect(state.applications).toEqual([]);
    expect(state.applicationsStatus).toBe("idle");
    expect(state.monitoring).toBeNull();
  });

  it("kpis fixture friendly", () => {
    const kpis: KpiSummary = { pending: 3, approved: 8, review: 2, declined: 1 };
    useDataStore.setState({ kpis });
    expect(useDataStore.getState().kpis?.approved).toBe(8);
  });
});
