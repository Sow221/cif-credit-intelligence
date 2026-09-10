export type ModelStatus = "DRAFT" | "STAGING" | "PRODUCTION" | "ARCHIVED" | "DEPRECATED";

export type ModelStage = "DEVELOPMENT" | "VALIDATION" | "STAGING" | "PRODUCTION";

export type FeatureSet = "CORE_25" | "EXTENDED" | "SIMPLE";

export interface Model {
  model_id: string;
  name: string;
  version: string;
  status: ModelStatus;
  stage: ModelStage;
  auc: number;
  brier_score: number | null;
  feature_set_id: FeatureSet;
  trained_at: string;
  created_at: string;
  description?: string | null;
  metrics?: Record<string, number>;
}

export interface ModelDetail extends Model {
  features: string[];
  thresholds: Record<string, number>;
  calibration_version: string | null;
  is_approved: boolean;
}

export interface PromotePayload {
  action: "PROMOTE" | "DEMOTE" | "ARCHIVE";
}
