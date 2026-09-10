import type { AuthUser } from "@/services/auth";
import { useAuthStore } from "@/store/auth";
import { useDataStore } from "@/store/data";
import { useNotificationsStore } from "@/store/notifications";
import { useToastStore } from "@/store/toast";
import type { Application, ApplicationDetail } from "@/types/application";
import type { Client, ClientDetail } from "@/types/client";
import type { Model } from "@/types/model";
import type { MonitoringSnapshot } from "@/types/monitoring";
import type { Review } from "@/types/review";

export const adminUser: AuthUser = {
  user_id: "u1",
  username: "admin",
  full_name: "Admin Diallo",
  role: "ADMIN",
  institution_id: "i1",
  email: "admin@example.com",
};

export const managerUser: AuthUser = {
  user_id: "u2",
  username: "manager",
  full_name: "Manager Sow",
  role: "CREDIT_MANAGER",
  institution_id: "i1",
};

export const officerUser: AuthUser = {
  user_id: "u3",
  username: "officer",
  full_name: "Officer Ndiaye",
  role: "CREDIT_OFFICER",
  institution_id: "i1",
};

export function seedAuth(user: AuthUser | null = adminUser): void {
  if (user) {
    useAuthStore.getState().setAuthenticated(user, "t");
  } else {
    useAuthStore.setState({ user: null, token: null, status: "unauthenticated", error: null });
  }
}

export function resetStores(): void {
  useAuthStore.setState({ user: null, token: null, status: "unauthenticated", error: null });
  useDataStore.setState({
    applications: [],
    applicationsStatus: "idle",
    applicationsError: null,
    totalApplications: 0,
    currentApplication: null,
    currentApplicationStatus: "idle",
    currentApplicationError: null,
    clients: [],
    clientsStatus: "idle",
    clientsError: null,
    currentClient: null,
    currentClientStatus: "idle",
    currentClientError: null,
    reviews: [],
    reviewsStatus: "idle",
    reviewsError: null,
    models: [],
    modelsStatus: "idle",
    modelsError: null,
    currentModel: null,
    monitoring: null,
    monitoringStatus: "idle",
    kpis: null,
  });
  useNotificationsStore.setState({ items: [], isOpen: false });
  useToastStore.setState({ toasts: [] });
}

export function makeApplication(overrides: Partial<Application> = {}): Application {
  return {
    application_id: "app-1",
    institution_id: "i1",
    client_id: "c1",
    product_id: "SMALL_BUSINESS",
    requested_amount: 250000,
    currency: "XOF",
    requested_term: 12,
    status: "SUBMITTED",
    application_timestamp: "2024-03-01T10:00:00Z",
    created_at: "2024-03-01T10:00:00Z",
    client_name: "Awa Diallo",
    ...overrides,
  };
}

export function makeDetailApplication(
  overrides: Partial<ApplicationDetail> = {},
): ApplicationDetail {
  return {
    ...makeApplication(),
    risk: {
      pd_raw: 0.12,
      pd_calibrated: 0.1,
      risk_band: "LOW",
      model_version: "gbm-v1",
      feature_set_id: "CORE_25",
    },
    information_state: "FULL_FILE",
    eligibility: { eligible: true, reasons: ["Dossier complet"] },
    recommendation: "APPROVE",
    final_decision: null,
    decision_reason: null,
    policy_version: 3,
    uncertainty_level: "LOW",
    explanation_factors: ["savings_balance", "repayment_history"],
    information_gaps: [],
    ...overrides,
  };
}

export function makeClient(overrides: Partial<Client> = {}): Client {
  return {
    client_id: "c1",
    institution_id: "i1",
    first_name: "Awa",
    last_name: "Diallo",
    status: "ACTIVE",
    created_at: "2024-03-01T10:00:00Z",
    ...overrides,
  };
}

export function makeClientDetail(overrides: Partial<ClientDetail> = {}): ClientDetail {
  return {
    ...makeClient(),
    email: "awa.diallo@example.com",
    phone: "+221771234567",
    zone: "Dakar",
    sector: "Commerce",
    savings: {
      balance: 150000,
      average_balance: 120000,
      stability_score: 0.85,
      currency: "XOF",
    },
    loans: [
      {
        loan_id: "loan-1",
        amount: 100000,
        currency: "XOF",
        status: "ACTIVE",
        started_at: "2023-06-01T00:00:00Z",
      },
    ],
    ...overrides,
  };
}

export function makeReview(overrides: Partial<Review> = {}): Review {
  return {
    review_id: "rev-1",
    application_id: "app-1",
    assigned_to: null,
    status: "PENDING",
    review_reason: "manual",
    final_action: null,
    started_at: null,
    completed_at: null,
    client_name: "Awa Diallo",
    pd: 0.25,
    ...overrides,
  };
}

export function makeModel(overrides: Partial<Model> = {}): Model {
  return {
    model_id: "mod-1",
    name: "GBM v2",
    version: "2.1.0",
    status: "STAGING",
    stage: "STAGING",
    auc: 0.82,
    brier_score: 0.12,
    feature_set_id: "CORE_25",
    trained_at: "2024-03-01T10:00:00Z",
    created_at: "2024-03-01T10:00:00Z",
    ...overrides,
  };
}

export function makeMonitoring(overrides: Partial<MonitoringSnapshot> = {}): MonitoringSnapshot {
  return {
    dataQuality: [{ feature: "age", completeness: 0.95, stability: 0.9, drift: 0.05 }],
    modelPerformance: {
      auc: 0.81,
      brier: 0.13,
      calibration_error: 0.02,
      ks: 0.35,
      gini: 0.62,
    },
    decisionStats: { APPROVE: 10, DECLINE: 5 },
    fairness: [{ group: "women", sample_size: 100, approval_rate: 0.7, adverse_impact_ratio: 0.9 }],
    incidents: [],
    ...overrides,
  };
}
