import { useState } from "react";
import type { PredictionResponse } from "../types/prediction";
import { ClientForm } from "../components/forms/ClientForm";
import { RiskGauge } from "../components/dashboard/RiskGauge";
import { ConfidenceIndicator } from "../components/dashboard/ConfidenceIndicator";
import { DecisionBadge } from "../components/dashboard/DecisionBadge";
import { Card } from "../components/ui";
import { formatDate } from "../utils/format";

interface AgentDashboardProps {
  agentId: string;
}

export function AgentDashboard({ agentId }: AgentDashboardProps) {
  const [result, setResult] = useState<PredictionResponse | null>(null);

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div>
        <h2 className="mb-3 text-lg font-semibold text-gray-800">
          Nouvelle evaluation (agent {agentId})
        </h2>
        <ClientForm onResult={setResult} />
      </div>

      <div>
        <h2 className="mb-3 text-lg font-semibold text-gray-800">Resultat</h2>
        {result ? (
          <div className="grid gap-4">
            <Card title="Risque de defaut (PD)">
              <RiskGauge pd={result.pd_score} />
            </Card>
            <Card title="Decision">
              <div className="flex items-center justify-between">
                <DecisionBadge decision={result.recommendation.decision} />
                {result.is_thin_file && (
                  <span className="text-xs text-gray-500">Thin-File</span>
                )}
              </div>
              <p className="mt-2 text-sm text-gray-600">{result.recommendation.raison}</p>
            </Card>
            <Card title="Confiance">
              <ConfidenceIndicator confidence={result.confidence} />
            </Card>
            <Card title="Metadonnees">
              <dl className="grid grid-cols-2 gap-2 text-sm">
                <dt className="text-gray-500">Model</dt>
                <dd className="text-right font-medium">{result.model_version ?? "—"}</dd>
                <dt className="text-gray-500">Request ID</dt>
                <dd className="text-right font-mono text-xs break-all">{result.request_id}</dd>
                <dt className="text-gray-500">Date</dt>
                <dd className="text-right">{formatDate(result.timestamp)}</dd>
              </dl>
            </Card>
          </div>
        ) : (
          <Card className="text-sm text-gray-500">
            Remplissez le formulaire et lancez une prediction pour afficher le resultat.
          </Card>
        )}
      </div>
    </div>
  );
}
