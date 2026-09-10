import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useApplications } from "./useApplications";
import { useDataStore } from "@/store/data";
import { useToastStore } from "@/store/toast";
import type { Application } from "@/types/application";

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

const approvedApp: Application = {
  ...application,
  application_id: "app-2",
  status: "APPROVE",
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

describe("useApplications", () => {
  beforeEach(() => {
    resetDataStore();
    useToastStore.setState({ toasts: [] });
    mockedApi.get.mockReset();
    mockedApi.post.mockReset();
    mockedApi.patch.mockReset();
  });

  it("returns applications from the store when status is success", () => {
    useDataStore.setState({
      applications: [application, approvedApp],
      applicationsStatus: "success",
    });
    const { result } = renderHook(() => useApplications());
    expect(result.current.applications).toEqual([application, approvedApp]);
    expect(result.current.status).toBe("success");
    expect(result.current.error).toBeNull();
  });

  it("computes pendingCount correctly", () => {
    useDataStore.setState({
      applications: [application, approvedApp],
      applicationsStatus: "success",
    });
    const { result } = renderHook(() => useApplications());
    expect(result.current.pendingCount).toBe(1);
  });

  it("returns 0 pendingCount when no SUBMITTED apps", () => {
    useDataStore.setState({ applications: [approvedApp], applicationsStatus: "success" });
    const { result } = renderHook(() => useApplications());
    expect(result.current.pendingCount).toBe(0);
  });

  it("does not fetch when store is already success", () => {
    useDataStore.setState({ applications: [application], applicationsStatus: "success" });
    renderHook(() => useApplications());
    expect(mockedApi.get).not.toHaveBeenCalled();
  });

  it("createApplication calls store and shows toast", async () => {
    const created = { ...application, application_id: "app-3" };
    mockedApi.post.mockResolvedValue(created);
    useDataStore.setState({ applications: [application], applicationsStatus: "success" });
    const { result } = renderHook(() => useApplications());

    await act(async () => {
      const res = await result.current.createApplication({ client_id: "c1" });
      expect(res.application_id).toBe("app-3");
    });

    expect(mockedApi.post).toHaveBeenCalledWith("/applications", { client_id: "c1" });
    expect(useToastStore.getState().toasts.length).toBe(1);
    expect(useToastStore.getState().toasts[0]?.variant).toBe("success");
  });

  it("updateStatus calls store and shows toast", async () => {
    useDataStore.setState({
      applications: [application],
      applicationsStatus: "success",
    });
    mockedApi.patch.mockResolvedValue({});
    const { result } = renderHook(() => useApplications());

    await act(async () => {
      await result.current.updateStatus("app-1", "REVIEW");
    });

    expect(mockedApi.patch).toHaveBeenCalledWith("/applications/app-1/status", {
      status: "REVIEW",
    });
    expect(useToastStore.getState().toasts.length).toBe(1);
  });

  it("reload calls fetchApplications with filtered params", async () => {
    mockedApi.get.mockResolvedValue([]);
    useDataStore.setState({ applications: [application], applicationsStatus: "success" });
    const { result } = renderHook(() => useApplications());

    await act(async () => {
      await result.current.reload({ status: "SUBMITTED", risk_band: "" });
    });

    expect(mockedApi.get).toHaveBeenCalledWith("/applications?status=SUBMITTED");
  });
});
