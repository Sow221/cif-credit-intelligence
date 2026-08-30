import type { DecisionType } from "../../types/prediction";
import { Badge } from "../ui/Badge";

type Tone = "low" | "medium" | "high" | "neutral";

const toneByDecision: Record<DecisionType, Tone> = {
  APPROBATION: "low",
  REVUE_HUMAINE: "medium",
  AJUSTEMENT: "medium",
  REFUS: "high",
};

const labels: Record<DecisionType, string> = {
  APPROBATION: "Approbation",
  REVUE_HUMAINE: "Revue humaine",
  AJUSTEMENT: "Ajustement",
  REFUS: "Refus",
};

interface DecisionBadgeProps {
  decision: DecisionType;
}

export function DecisionBadge({ decision }: DecisionBadgeProps) {
  return <Badge tone={toneByDecision[decision] ?? "neutral"}>{labels[decision]}</Badge>;
}
