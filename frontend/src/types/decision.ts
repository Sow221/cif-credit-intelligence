export type Recommendation = "APPROVE" | "DECLINE" | "REVIEW" | "REFER" | "UNKNOWN";

export interface Decision {
  decision_id: string;
  application_id: string;
  recommendation: Recommendation;
  final_decision: string | null;
  proposed_amount: number | null;
  proposed_term: number | null;
  decision_reason: string | null;
  policy_version: number | null;
  override?: Override | null;
}

export interface Override {
  override_id: string;
  decision_id: string;
  original_recommendation: string;
  final_decision: string;
  override_reason: string;
  actor_id: string;
  created_at: string;
}

export interface OverridePayload {
  final_decision: "APPROVE" | "DECLINE";
  override_reason: string;
}

export interface DecisionOutcome {
  applications_total: number;
  approved: number;
  reviewed: number;
  declined: number;
  override_rate: number;
}
