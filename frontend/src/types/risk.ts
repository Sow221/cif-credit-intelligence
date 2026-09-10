import type { RiskAssessment, RiskBand } from "./application";

export interface UncertaintyLevel {
  label: "LOW" | "MODERATE" | "HIGH";
  score: number;
}

export interface UncertaintyFactor {
  name: string;
  impact: "LOW" | "MODERATE" | "HIGH";
  description?: string;
}

export interface Uncertainty {
  level: UncertaintyLevel["label"];
  score: number;
  method: string;
  factors: UncertaintyFactor[];
  confidence_interval?: { lower: number; upper: number } | null;
}

export interface ModelContribution {
  feature: string;
  contribution: number;
}

export interface ModelExplanation {
  contributions: ModelContribution[];
  top_features: string[];
}

export interface RiskDetailBundle {
  assessment: RiskAssessment;
  uncertainty: Uncertainty;
  explanation?: ModelExplanation | null;
}

export type { RiskAssessment, RiskBand };
