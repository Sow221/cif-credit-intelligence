import { useEffect } from "react";
import { useDataStore } from "@/store/data";
import { useToastStore } from "@/store/toast";

export function useClients() {
  const clients = useDataStore((state) => state.clients);
  const status = useDataStore((state) => state.clientsStatus);
  const error = useDataStore((state) => state.clientsError);
  const fetchClients = useDataStore((state) => state.fetchClients);
  const createClient = useDataStore((state) => state.createClient);

  useEffect(() => {
    if (status === "idle") {
      void fetchClients();
    }
  }, [status, fetchClients]);

  function reload(search?: string) {
    return fetchClients(search ? { search } : undefined);
  }

  return {
    clients,
    status,
    error,
    reload,
    createClient: async (payload: Record<string, unknown>) => {
      const client = await createClient(payload);
      useToastStore.getState().addToast("success", "clients.toasts.created");
      return client;
    },
  };
}
