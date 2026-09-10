export type AuditEventType =
  | "APPLICATION_CREATED"
  | "APPLICATION_SUBMITTED"
  | "DATA_PROFILED"
  | "SCORE_GENERATED"
  | "DECISION_CREATED"
  | "REVIEW_CREATED"
  | "REVIEW_ASSIGNED"
  | "REVIEW_STARTED"
  | "REVIEW_COMPLETED"
  | "OVERRIDE_CREATED"
  | "CONSENT_GRANTED"
  | "CONSENT_REVOKED"
  | "USER_LOGIN"
  | string;

export interface AuditEvent {
  event_id: string;
  institution_id: string;
  event_type: AuditEventType;
  entity_type: string;
  entity_id: string;
  actor_id: string | null;
  payload_hash: string | null;
  created_at: string;
  actor_name?: string;
}

export interface AuditTimelineItem {
  id: string;
  type: AuditEventType;
  label: string;
  timestamp: string;
  actor?: string | null;
  payload?: Record<string, unknown> | null;
}
