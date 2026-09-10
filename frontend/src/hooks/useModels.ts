import { useEffect } from "react";
import { useDataStore } from "@/store/data";

export function useModels() {
  const models = useDataStore((state) => state.models);
  const status = useDataStore((state) => state.modelsStatus);
  const error = useDataStore((state) => state.modelsError);
  const fetchModels = useDataStore((state) => state.fetchModels);
  const promoteModel = useDataStore((state) => state.promoteModel);

  useEffect(() => {
    if (status === "idle") {
      void fetchModels();
    }
  }, [status, fetchModels]);

  const productionModel = models.find((model) => model.status === "PRODUCTION") ?? null;

  return { models, status, error, reload: fetchModels, promoteModel, productionModel };
}
