export type ConfidenceLevel = "FAIBLE" | "MOYENNE" | "ELEVEE";

export type DecisionType = "APPROBATION" | "REVUE_HUMAINE" | "AJUSTEMENT" | "REFUS";

export interface ConfidenceScore {
  level: ConfidenceLevel;
  score: number;
}

export interface Recommendation {
  decision: DecisionType;
  raison: string;
}

export interface SavingsEntry {
  month: number;
  balance: number;
}

export interface LoanEntry {
  loan_id: number;
  amount: number;
  repayment_regularity: number;
  max_dpd: number;
  status: "completed" | "defaulted";
}

export interface PredictionRequest {
  customer_id: number;
  age: number;
  seniority_months: number;
  monthly_income: number;
  current_savings: number;
  n_past_loans: number;
  current_loan_request: number;
  current_loan_duration: number;
  has_history?: boolean;
  savings_history?: SavingsEntry[];
  loan_history?: LoanEntry[];
}

export interface PredictionResponse {
  status: string;
  pd_score: number | null;
  confidence: ConfidenceScore;
  recommendation: Recommendation;
  is_thin_file: boolean;
  model_version: string | null;
  request_id: string;
  timestamp: string;
}

export interface DecisionItem {
  prediction_id: string;
  customer_id: number;
  pd_score: number;
  confidence_level: ConfidenceLevel;
  confidence_score: number;
  recommendation: DecisionType;
  model_version: string;
  created_at: string;
}

export interface AuditItem {
  audit_id: string;
  prediction_id: string;
  agent_id: string | null;
  agent_decision: DecisionType | null;
  agent_justification: string | null;
  is_override: boolean;
  created_at: string;
}

export interface ModelItem {
  version_id: number;
  version_name: string;
  mlflow_run_id: string | null;
  roc_auc: number | null;
  pr_auc: number | null;
  brier_score: number | null;
  status: string;
  deployed_at: string | null;
  created_at: string;
}

export interface ListResponse<T> {
  total: number;
  items: T[];
}

export interface OverrideRequest {
  agent_id: string;
  decision: DecisionType;
  justification: string;
}
