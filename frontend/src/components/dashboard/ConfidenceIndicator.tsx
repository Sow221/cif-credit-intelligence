import type { ConfidenceScore as ConfidenceScoreType } from "../../types/prediction";
import { Badge } from "../ui/Badge";

type Tone = "low" | "medium" | "high" | "neutral";

const toneByLevel: Record<ConfidenceScoreType["level"], Tone> = {
  FAIBLE: "high",
  MOYENNE: "medium",
  ELEVEE: "low",
};

const labels: Record<ConfidenceScoreType["level"], string> = {
  FAIBLE: "Confiance faible",
  MOYENNE: "Confiance moyenne",
  ELEVEE: "Confiance elevee",
};

interface ConfidenceIndicatorProps {
  confidence: ConfidenceScoreType;
}

export function ConfidenceIndicator({ confidence }: ConfidenceIndicatorProps) {
  const tone = toneByLevel[confidence.level] ?? "neutral";
  return (
    <div className="flex items-center justify-between">
      <Badge tone={tone}>{labels[confidence.level]}</Badge>
      <span className="text-sm font-medium text-gray-700">
        {Math.round(confidence.score * 100)}%
      </span>
    </div>
  );
}
