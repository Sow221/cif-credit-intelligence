export interface MonitoringTabData {
  dataQuality: number;
  missingRate: number;
  driftScore: number;
  auc: number;
  brier: number;
  calibration: number;
  incidentCount: number;
}

export interface MetricTrend {
  metric: string;
  current: number;
  baseline: number;
  drift: number;
  trending: "up" | "down" | "stable";
}

export interface Incident {
  incident_id: string;
  type: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: "OPEN" | "ACKNOWLEDGED" | "RESOLVED";
  created_at: string;
  description: string;
}

export interface FairnessMetric {
  group: string;
  sample_size: number;
  approval_rate: number;
  adverse_impact_ratio: number;
}

export interface DataQualityMetric {
  feature: string;
  completeness: number;
  stability: number;
  drift: number;
}

export interface ModelPerformance {
  auc: number;
  brier: number;
  calibration_error: number;
  ks: number;
  gini: number;
}

export type DecisionStats = Array<[string, number]>;

export interface MonitoringSnapshot {
  dataQuality: DataQualityMetric[];
  modelPerformance: ModelPerformance | null;
  decisionStats: Record<string, number>;
  fairness: FairnessMetric[];
  incidents: Incident[];
}
