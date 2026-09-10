import { useEffect } from "react";
import { useDataStore } from "@/store/data";
import { useToastStore } from "@/store/toast";
import type { ReviewFilters } from "@/types/review";

export function useReviews() {
  const reviews = useDataStore((state) => state.reviews);
  const status = useDataStore((state) => state.reviewsStatus);
  const error = useDataStore((state) => state.reviewsError);
  const fetchReviews = useDataStore((state) => state.fetchReviews);
  const assignReview = useDataStore((state) => state.assignReview);
  const startReview = useDataStore((state) => state.startReview);
  const completeReview = useDataStore((state) => state.completeReview);
  const addToast = useToastStore((state) => state.addToast);

  useEffect(() => {
    if (status === "idle") {
      void fetchReviews();
    }
  }, [status, fetchReviews]);

  function reload(filters?: ReviewFilters) {
    const params: Record<string, unknown> = {};
    if (filters) {
      for (const [key, value] of Object.entries(filters)) {
        if (value !== undefined && value !== "") params[key] = value;
      }
    }
    return fetchReviews(params);
  }

  return {
    reviews,
    status,
    error,
    reload,
    assign: async (id: string, assignedTo: string) => {
      await assignReview(id, assignedTo);
      addToast("success", "review.toasts.assigned");
    },
    start: async (id: string) => {
      await startReview(id);
      addToast("success", "review.toasts.started");
    },
    complete: async (id: string, finalAction: "APPROVE" | "DECLINE") => {
      await completeReview(id, finalAction);
      addToast("success", "review.toasts.completed");
    },
    pendingCount: reviews.filter((review) => review.status === "PENDING").length,
  };
}
