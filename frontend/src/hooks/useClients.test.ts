import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useClients } from "./useClients";
import { useDataStore } from "@/store/data";
import { useToastStore } from "@/store/toast";
import type { Client } from "@/types/client";

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

const client: Client = {
  client_id: "c1",
  institution_id: "i1",
  first_name: "Awa",
  last_name: "Diallo",
  status: "ACTIVE",
  created_at: "2024-03-01T10:00:00Z",
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

describe("useClients", () => {
  beforeEach(() => {
    resetDataStore();
    useToastStore.setState({ toasts: [] });
    mockedApi.get.mockReset();
    mockedApi.post.mockReset();
    mockedApi.patch.mockReset();
  });

  it("returns clients from the store", () => {
    useDataStore.setState({ clients: [client], clientsStatus: "success" });
    const { result } = renderHook(() => useClients());
    expect(result.current.clients).toEqual([client]);
    expect(result.current.status).toBe("success");
    expect(result.current.error).toBeNull();
  });

  it("does not fetch when store is already success", () => {
    useDataStore.setState({ clients: [client], clientsStatus: "success" });
    renderHook(() => useClients());
    expect(mockedApi.get).not.toHaveBeenCalled();
  });

  it("reload with search calls fetchClients with search param", async () => {
    mockedApi.get.mockResolvedValue([]);
    useDataStore.setState({ clients: [client], clientsStatus: "success" });
    const { result } = renderHook(() => useClients());

    await act(async () => {
      await result.current.reload("Awa");
    });

    expect(mockedApi.get).toHaveBeenCalledWith("/clients?search=Awa");
  });

  it("reload without search calls fetchClients without params", async () => {
    mockedApi.get.mockResolvedValue([]);
    useDataStore.setState({ clients: [client], clientsStatus: "success" });
    const { result } = renderHook(() => useClients());

    await act(async () => {
      await result.current.reload();
    });

    expect(mockedApi.get).toHaveBeenCalledWith("/clients");
  });

  it("createClient calls store and shows toast", async () => {
    const created = { ...client, client_id: "c2" };
    mockedApi.post.mockResolvedValue(created);
    useDataStore.setState({ clients: [client], clientsStatus: "success" });
    const { result } = renderHook(() => useClients());

    await act(async () => {
      const res = await result.current.createClient({ first_name: "B" });
      expect(res.client_id).toBe("c2");
    });

    expect(mockedApi.post).toHaveBeenCalledWith("/clients", { first_name: "B" });
    expect(useToastStore.getState().toasts.length).toBe(1);
    expect(useToastStore.getState().toasts[0]?.variant).toBe("success");
  });
});
