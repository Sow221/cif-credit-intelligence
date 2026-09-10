import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useReviews } from "./useReviews";
import { useDataStore } from "@/store/data";
import { useToastStore } from "@/store/toast";
import type { Review } from "@/types/review";

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

const inProgressReview: Review = {
  ...review,
  review_id: "rev-2",
  status: "IN_PROGRESS",
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

describe("useReviews", () => {
  beforeEach(() => {
    resetDataStore();
    useToastStore.setState({ toasts: [] });
    mockedApi.get.mockReset();
    mockedApi.post.mockReset();
    mockedApi.patch.mockReset();
  });

  it("returns reviews from the store", () => {
    useDataStore.setState({ reviews: [review, inProgressReview], reviewsStatus: "success" });
    const { result } = renderHook(() => useReviews());
    expect(result.current.reviews).toEqual([review, inProgressReview]);
    expect(result.current.status).toBe("success");
    expect(result.current.error).toBeNull();
  });

  it("computes pendingCount correctly", () => {
    useDataStore.setState({ reviews: [review, inProgressReview], reviewsStatus: "success" });
    const { result } = renderHook(() => useReviews());
    expect(result.current.pendingCount).toBe(1);
  });

  it("does not fetch when store is already success", () => {
    useDataStore.setState({ reviews: [review], reviewsStatus: "success" });
    renderHook(() => useReviews());
    expect(mockedApi.get).not.toHaveBeenCalled();
  });

  it("assign calls store and shows toast", async () => {
    useDataStore.setState({ reviews: [review], reviewsStatus: "success" });
    const assigned = { ...review, assigned_to: "u1", status: "ASSIGNED" as const };
    mockedApi.patch.mockResolvedValue(assigned);
    const { result } = renderHook(() => useReviews());

    await act(async () => {
      await result.current.assign("rev-1", "u1");
    });

    expect(mockedApi.patch).toHaveBeenCalledWith("/reviews/rev-1/assign", { assigned_to: "u1" });
    expect(useToastStore.getState().toasts.length).toBe(1);
    expect(useToastStore.getState().toasts[0]?.variant).toBe("success");
  });

  it("start calls store and shows toast", async () => {
    useDataStore.setState({ reviews: [review], reviewsStatus: "success" });
    mockedApi.patch.mockResolvedValue({ ...review, status: "IN_PROGRESS" });
    const { result } = renderHook(() => useReviews());

    await act(async () => {
      await result.current.start("rev-1");
    });

    expect(mockedApi.patch).toHaveBeenCalledWith("/reviews/rev-1/start", {});
    expect(useToastStore.getState().toasts.length).toBe(1);
  });

  it("complete calls store and shows toast", async () => {
    useDataStore.setState({ reviews: [review], reviewsStatus: "success" });
    mockedApi.patch.mockResolvedValue({ ...review, status: "COMPLETED", final_action: "APPROVE" });
    const { result } = renderHook(() => useReviews());

    await act(async () => {
      await result.current.complete("rev-1", "APPROVE");
    });

    expect(mockedApi.patch).toHaveBeenCalledWith("/reviews/rev-1/complete", {
      final_action: "APPROVE",
    });
    expect(useToastStore.getState().toasts.length).toBe(1);
  });

  it("reload filters empty values", async () => {
    mockedApi.get.mockResolvedValue([]);
    useDataStore.setState({ reviews: [review], reviewsStatus: "success" });
    const { result } = renderHook(() => useReviews());

    await act(async () => {
      await result.current.reload({ status: "PENDING", assigned_to: "", date_from: undefined });
    });

    expect(mockedApi.get).toHaveBeenCalledWith("/reviews?status=PENDING");
  });
});
