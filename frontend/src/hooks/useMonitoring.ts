import { useEffect } from "react";
import { useDataStore } from "@/store/data";

export function useMonitoring() {
  const monitoring = useDataStore((state) => state.monitoring);
  const status = useDataStore((state) => state.monitoringStatus);
  const fetchMonitoring = useDataStore((state) => state.fetchMonitoring);

  useEffect(() => {
    if (status === "idle") {
      void fetchMonitoring();
    }
  }, [status, fetchMonitoring]);

  return { monitoring, status, reload: fetchMonitoring };
}
