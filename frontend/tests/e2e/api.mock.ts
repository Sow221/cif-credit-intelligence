import type { Page, Route } from "@playwright/test";

export const APP = {
  applications: [
    {
      application_id: "APP-001",
      institution_id: "i1",
      client_id: "c1",
      product_id: "SMALL_BUSINESS",
      requested_amount: 250000,
      currency: "XOF",
      requested_term: 12,
      purpose: "Stock",
      status: "SUBMITTED",
      application_timestamp: "2024-03-01T10:00:00Z",
      created_at: "2024-03-01T10:00:00Z",
      client_name: "Awa Diallo",
      information_state: "FULL_FILE",
    },
  ],
  clients: [
    {
      client_id: "c1",
      institution_id: "i1",
      first_name: "Awa",
      last_name: "Diallo",
      status: "ACTIVE",
      created_at: "2024-03-01T10:00:00Z",
    },
  ],
  reviews: [
    {
      review_id: "REV-001",
      application_id: "APP-001",
      assigned_to: null,
      status: "PENDING",
      review_reason: "manual",
      final_action: null,
      started_at: null,
      completed_at: null,
      client_name: "Awa Diallo",
      requested_amount: 250000,
      currency: "XOF",
      age_hours: 2,
    },
  ],
  models: [
    {
      model_id: "MOD-001",
      name: "GBM v2",
      version: "2.1.0",
      status: "STAGING",
      stage: "STAGING",
      auc: 0.82,
      brier_score: 0.12,
      feature_set_id: "CORE_25",
      trained_at: "2024-03-01T10:00:00Z",
      created_at: "2024-03-01T10:00:00Z",
    },
  ],
  monitoring: {
    dataQuality: [{ feature: "age", completeness: 0.95, stability: 0.9, drift: 0.05 }],
    modelPerformance: { auc: 0.81, brier: 0.13, calibration_error: 0.02, ks: 0.35, gini: 0.62 },
    decisionStats: { APPROVE: 10, DECLINE: 5 },
    fairness: [],
    incidents: [],
  },
};

const user = {
  user_id: "u1",
  username: "awa.diallo",
  full_name: "Awa Diallo",
  role: "ADMIN",
  institution_id: "i1",
  email: "awa@example.com",
};

const kpis = { pending: 3, approved: 8, review: 2, declined: 1 };

function json(route: Route, body: unknown): void {
  void route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
}

export async function mockBackend(page: Page): Promise<void> {
  await page.route("**/api/v1/**", async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();

    if (path === "/api/v1/auth/login") {
      json(route, { access_token: "token-e2e", token_type: "bearer" });
      return;
    }
    if (path === "/api/v1/auth/me") {
      json(route, { user });
      return;
    }
    if (path === "/api/v1/kpis") {
      json(route, kpis);
      return;
    }
    if (path.startsWith("/api/v1/audit")) {
      json(route, []);
      return;
    }
    if (path === "/api/v1/applications") {
      if (method === "POST") {
        json(route, { ...APP.applications[0], application_id: "APP-NEW" });
        return;
      }
      json(route, APP.applications);
      return;
    }
    if (path.startsWith("/api/v1/applications/")) {
      json(route, {
        ...APP.applications[0],
        information_state: "FULL_FILE",
        information_profile: { state: "FULL_FILE", score: 0.9, version: 3 },
        uncertainty_level: "LOW",
        eligibility: { eligible: true, reasons: [] },
        recommendation: "APPROVE",
        final_decision: null,
        decision_reason: null,
        policy_version: 3,
        explanation_factors: ["capacite"],
        risk: { pd_raw: 0.05, pd_calibrated: 0.04, risk_band: "LOW", model_version: "v2", feature_set_id: "CORE_25" },
      });
      return;
    }
    if (path.startsWith("/api/v1/clients/")) {
      json(route, { ...APP.clients[0], savings: { balance: 50000, average_balance: 42000, stability_score: 0.9, currency: "XOF" }, loans: [] });
      return;
    }
    if (path.startsWith("/api/v1/clients")) {
      json(route, APP.clients);
      return;
    }
    if (path.startsWith("/api/v1/reviews")) {
      json(route, APP.reviews);
      return;
    }
    if (path.startsWith("/api/v1/models")) {
      json(route, APP.models);
      return;
    }
    if (path.startsWith("/api/v1/monitoring")) {
      json(route, APP.monitoring);
      return;
    }
    if (path === "/api/v1/decisions") {
      json(route, { decision_id: "DEC-1", application_id: "APP-001", recommendation: "APPROVE" });
      return;
    }
    if (path.startsWith("/api/v1/decisions/")) {
      json(route, {});
      return;
    }
    json(route, {});
  });
}

export async function login(page: Page): Promise<void> {
  await mockBackend(page);
  await page.goto("/login");
  await page.getByTestId("username").fill("awa.diallo");
  await page.getByTestId("password").fill("secret");
  await page.getByTestId("submit").click();
  await page.waitForURL("**/dashboard");
}