import type { InformationState } from "./information";

export type ApplicationStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "DATA_VALIDATION"
  | "PROFILED"
  | "SCORED"
  | "REVIEW"
  | "DECIDED"
  | "CANCELLED"
  | "APPROVE"
  | "DECLINE";

export interface Application {
  application_id: string;
  institution_id: string;
  client_id: string;
  product_id: string;
  requested_amount: number;
  currency: string;
  requested_term: number;
  purpose?: string | null;
  status: ApplicationStatus;
  application_timestamp: string;
  created_at: string;
  client_name?: string;
  information_state?: string;
  risk?: RiskAssessment | null;
}

export interface CreateApplicationPayload {
  client_id: string;
  product_id: string;
  requested_amount: number;
  currency: string;
  requested_term: number;
  purpose?: string | null;
}

export interface ApplicationFilters {
  status?: ApplicationStatus | "";
  risk_band?: string | "";
  information_state?: string | "";
  date_from?: string | "";
  date_to?: string | "";
  product_id?: string | "";
  search?: string;
}

export type RiskBand = "LOW" | "MEDIUM" | "HIGH" | "UNKNOWN";

export interface RiskAssessment {
  pd_raw: number;
  pd_calibrated: number | null;
  risk_band: RiskBand;
  model_version: string;
  feature_set_id: string;
  calibration_version?: string | null;
}

export interface ApplicationDetail extends Application {
  risk?: RiskAssessment | null;
  information_state?: string;
  eligibility?: EligibilityResult;
  recommendation?: string | null;
  final_decision?: string | null;
  decision_reason?: string | null;
  policy_version?: number | null;
  information_profile?: {
    state: InformationState;
    score: number;
    version: number;
  } | null;
  uncertainty_level?: string | null;
  explanation_factors?: string[];
  information_gaps?: Array<{ item: string; type: "missing" | "stale" | "unavailable" }>;
}

export interface EligibilityResult {
  eligible: boolean;
  reasons: string[];
}

export interface ActivityPoint {
  date: string;
  applications: number;
  approved: number;
}

export interface KpiSummary {
  pending: number;
  approved: number;
  review: number;
  declined: number;
}
