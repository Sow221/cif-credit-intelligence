export type ReviewStatus = "PENDING" | "ASSIGNED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";

export type ReviewFinalAction = "APPROVE" | "DECLINE";

export interface Review {
  review_id: string;
  application_id: string;
  assigned_to: string | null;
  status: ReviewStatus;
  review_reason: string;
  final_action: ReviewFinalAction | null;
  started_at: string | null;
  completed_at: string | null;
  client_name?: string;
  requested_amount?: number;
  currency?: string;
  pd?: number | null;
  age_hours?: number;
}

export interface AssignReviewPayload {
  assigned_to: string;
}

export interface CompleteReviewPayload {
  final_action: ReviewFinalAction;
}

export interface ReviewFilters {
  status: ReviewStatus | "";
  assigned_to: string | "";
  date_from?: string | "";
  date_to?: string | "";
}
