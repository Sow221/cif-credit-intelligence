import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useMonitoring } from "./useMonitoring";
import { useDataStore } from "@/store/data";
import type { MonitoringSnapshot } from "@/types/monitoring";

vi.mock("@/services/api", () => {
  const mock = { get: vi.fn(), post: vi.fn(), patch: vi.fn() };
  return { api: mock };
});

const mockedApi = vi.mocked(
  (await import("@/services/api")).api as unknown as {
    get: ReturnType<typeof vi.fn>;
    post: ReturnType<typeof vi.fn>;
    patch: ReturnType<typeof vi.fn>;
  },
);

const snapshot: MonitoringSnapshot = {
  dataQuality: [{ feature: "age", completeness: 0.95, stability: 0.9, drift: 0.05 }],
  modelPerformance: { auc: 0.81, brier: 0.13, calibration_error: 0.02, ks: 0.35, gini: 0.62 },
  decisionStats: { APPROVE: 10, DECLINE: 5 },
  fairness: [{ group: "g1", sample_size: 100, approval_rate: 0.7, adverse_impact_ratio: 0.9 }],
  incidents: [],
};

function resetDataStore() {
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
}

describe("useMonitoring", () => {
  beforeEach(() => {
    resetDataStore();
    mockedApi.get.mockReset();
    mockedApi.post.mockReset();
    mockedApi.patch.mockReset();
  });

  it("returns monitoring from the store", () => {
    useDataStore.setState({ monitoring: snapshot, monitoringStatus: "success" });
    const { result } = renderHook(() => useMonitoring());
    expect(result.current.monitoring).toEqual(snapshot);
    expect(result.current.status).toBe("success");
  });

  it("returns null monitoring when not loaded", () => {
    useDataStore.setState({ monitoring: null, monitoringStatus: "success" });
    const { result } = renderHook(() => useMonitoring());
    expect(result.current.monitoring).toBeNull();
    expect(result.current.status).toBe("success");
  });

  it("does not fetch when store is already success", () => {
    useDataStore.setState({ monitoring: snapshot, monitoringStatus: "success" });
    renderHook(() => useMonitoring());
    expect(mockedApi.get).not.toHaveBeenCalled();
  });

  it("reload is the same function reference as fetchMonitoring", () => {
    useDataStore.setState({ monitoring: null, monitoringStatus: "success" });
    const { result } = renderHook(() => useMonitoring());
    expect(result.current.reload).toBe(useDataStore.getState().fetchMonitoring);
  });
});
