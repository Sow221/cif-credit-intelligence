import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useModels } from "./useModels";
import { useDataStore } from "@/store/data";
import type { Model } from "@/types/model";

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

const stagingModel: Model = {
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

const prodModel: Model = {
  ...stagingModel,
  model_id: "mod-2",
  name: "GBM v3",
  status: "PRODUCTION",
  stage: "PRODUCTION",
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

describe("useModels", () => {
  beforeEach(() => {
    resetDataStore();
    mockedApi.get.mockReset();
    mockedApi.post.mockReset();
    mockedApi.patch.mockReset();
  });

  it("returns models from the store", () => {
    useDataStore.setState({ models: [stagingModel, prodModel], modelsStatus: "success" });
    const { result } = renderHook(() => useModels());
    expect(result.current.models).toEqual([stagingModel, prodModel]);
    expect(result.current.status).toBe("success");
    expect(result.current.error).toBeNull();
  });

  it("computes productionModel correctly", () => {
    useDataStore.setState({ models: [stagingModel, prodModel], modelsStatus: "success" });
    const { result } = renderHook(() => useModels());
    expect(result.current.productionModel).toEqual(prodModel);
  });

  it("returns null productionModel when no PRODUCTION model", () => {
    useDataStore.setState({ models: [stagingModel], modelsStatus: "success" });
    const { result } = renderHook(() => useModels());
    expect(result.current.productionModel).toBeNull();
  });

  it("does not fetch when store is already success", () => {
    useDataStore.setState({ models: [stagingModel], modelsStatus: "success" });
    renderHook(() => useModels());
    expect(mockedApi.get).not.toHaveBeenCalled();
  });

  it("reload is the same function reference as fetchModels", () => {
    useDataStore.setState({ models: [], modelsStatus: "success" });
    const { result } = renderHook(() => useModels());
    expect(result.current.reload).toBe(useDataStore.getState().fetchModels);
  });

  it("promoteModel delegates to store", async () => {
    mockedApi.get.mockResolvedValue([]);
    useDataStore.setState({ models: [stagingModel], modelsStatus: "success" });
    const { result } = renderHook(() => useModels());

    mockedApi.post.mockResolvedValue({});
    await result.current.promoteModel("mod-1", "PROMOTE");

    expect(mockedApi.post).toHaveBeenCalledWith("/models/mod-1/status", { action: "PROMOTE" });
  });
});
