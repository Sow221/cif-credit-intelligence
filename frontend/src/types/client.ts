export type ClientStatus = "ACTIVE" | "BLOCKED" | "PENDING";

export interface Client {
  client_id: string;
  institution_id: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string | null;
  phone?: string | null;
  email?: string | null;
  zone?: string | null;
  sector?: string | null;
  external_ref?: string | null;
  status: ClientStatus;
  created_at: string;
}

export interface CreateClientPayload {
  first_name: string;
  last_name: string;
  date_of_birth?: string | null;
  phone?: string | null;
  email?: string | null;
  zone?: string | null;
  sector?: string | null;
  external_ref?: string | null;
}

export interface SavingsSummary {
  balance: number;
  average_balance: number;
  stability_score: number;
  currency: string;
}

export interface LoanRecord {
  loan_id: string;
  amount: number;
  currency: string;
  status: string;
  started_at: string;
  ended_at?: string | null;
}

export interface ClientDetail extends Client {
  savings?: SavingsSummary;
  loans?: LoanRecord[];
}
