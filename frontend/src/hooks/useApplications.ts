import { useEffect, useMemo } from "react";
import { useDataStore } from "@/store/data";
import type { ApplicationFilters } from "@/types/application";
import { useToastStore } from "@/store/toast";

export function useApplications() {
  const applications = useDataStore((state) => state.applications);
  const status = useDataStore((state) => state.applicationsStatus);
  const error = useDataStore((state) => state.applicationsError);
  const fetchApplications = useDataStore((state) => state.fetchApplications);
  const createApplication = useDataStore((state) => state.createApplication);
  const updateApplicationStatus = useDataStore((state) => state.updateApplicationStatus);
  const addToast = useToastStore((state) => state.addToast);

  useEffect(() => {
    if (status === "idle") {
      void fetchApplications();
    }
  }, [status, fetchApplications]);

  function reload(filters?: ApplicationFilters) {
    const params: Record<string, unknown> = {};
    if (filters) {
      for (const [key, value] of Object.entries(filters)) {
        if (value !== undefined && value !== "") params[key] = value;
      }
    }
    return fetchApplications(params);
  }

  const pendingCount = useMemo(
    () => applications.filter((app) => app.status === "SUBMITTED").length,
    [applications],
  );

  return {
    applications,
    status,
    error,
    reload,
    createApplication: async (payload: Record<string, unknown>) => {
      const created = await createApplication(payload);
      addToast("success", "applications.toasts.created");
      return created;
    },
    updateStatus: async (id: string, status: string) => {
      await updateApplicationStatus(id, status);
      addToast("success", "applications.toasts.statusUpdated");
    },
    pendingCount,
  };
}
