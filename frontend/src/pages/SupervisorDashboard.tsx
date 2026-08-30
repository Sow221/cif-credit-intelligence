import { useEffect, useState } from "react";
import type { DecisionItem, OverrideRequest } from "../types/prediction";
import { api, ApiError } from "../services/api";
import { Button, Card, Modal } from "../components/ui";
import { DecisionBadge } from "../components/dashboard/DecisionBadge";
import { formatDate, formatPd } from "../utils/format";

interface SupervisorDashboardProps {
  agentId: string;
}

export function SupervisorDashboard({ agentId }: SupervisorDashboardProps) {
  const [decisions, setDecisions] = useState<DecisionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [overrideFor, setOverrideFor] = useState<DecisionItem | null>(null);
  const [overrideDecision, setOverrideDecision] = useState<OverrideRequest["decision"]>("REVUE_HUMAINE");
  const [justification, setJustification] = useState("");
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listDecisions();
      setDecisions(res.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const submitOverride = async () => {
    if (!overrideFor) return;
    setSaving(true);
    try {
      const body: OverrideRequest = {
        agent_id: agentId,
        decision: overrideDecision,
        justification,
      };
      await api.overrideDecision(overrideFor.prediction_id, body);
      setOverrideFor(null);
      setJustification("");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur d'override");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">Supervision des decisions</h2>
        <Button variant="secondary" size="sm" onClick={() => void load()}>
          Actualiser
        </Button>
      </div>

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-risk-high">{error}</div>}

      <Card>
        {loading ? (
          <div className="text-sm text-gray-500">Chargement...</div>
        ) : decisions.length === 0 ? (
          <div className="text-sm text-gray-500">Aucune decision enregistree.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b text-gray-500">
                  <th className="py-2 pr-3">Client</th>
                  <th className="py-2 pr-3">PD</th>
                  <th className="py-2 pr-3">Decision</th>
                  <th className="py-2 pr-3">Date</th>
                  <th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {decisions.map((d) => (
                  <tr key={d.prediction_id} className="border-b last:border-0">
                    <td className="py-2 pr-3">{d.customer_id}</td>
                    <td className="py-2 pr-3">{formatPd(d.pd_score)}</td>
                    <td className="py-2 pr-3">
                      <DecisionBadge decision={d.recommendation} />
                    </td>
                    <td className="py-2 pr-3 text-gray-500">{formatDate(d.created_at)}</td>
                    <td className="py-2 text-right">
                      <Button variant="secondary" size="sm" onClick={() => setOverrideFor(d)}>
                        Override
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <Modal open={overrideFor !== null} title="Override humain" onClose={() => setOverrideFor(null)}>
        {overrideFor && (
          <div className="grid gap-4">
            <p className="text-sm text-gray-600">
              Decision automatique :{" "}
              <DecisionBadge decision={overrideFor.recommendation} /> (PD{" "}
              {formatPd(overrideFor.pd_score)})
            </p>
            <label className="text-sm font-medium text-gray-700">Nouvelle decision</label>
            <select
              className="rounded-md border border-gray-300 px-3 py-2 text-sm"
              value={overrideDecision}
              onChange={(e) => setOverrideDecision(e.target.value as OverrideRequest["decision"])}
            >
              <option value="APPROBATION">Approbation</option>
              <option value="REVUE_HUMAINE">Revue humaine</option>
              <option value="AJUSTEMENT">Ajustement</option>
              <option value="REFUS">Refus</option>
            </select>
            <label className="text-sm font-medium text-gray-700">Justification</label>
            <textarea
              className="min-h-[100px] rounded-md border border-gray-300 px-3 py-2 text-sm"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder="Justification du superviseur"
            />
            <Button onClick={() => void submitOverride()} isLoading={saving}>
              Valider l'override
            </Button>
          </div>
        )}
      </Modal>
    </div>
  );
}
