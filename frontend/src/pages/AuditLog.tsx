import { useEffect, useState } from "react";
import type { AuditItem } from "../types/prediction";
import { api, ApiError } from "../services/api";
import { Button, Card } from "../components/ui";
import { formatDate } from "../utils/format";

export function AuditLogPage() {
  const [logs, setLogs] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listAudit();
      setLogs(res.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">Journal d'audit</h2>
        <Button variant="secondary" size="sm" onClick={() => void load()}>
          Actualiser
        </Button>
      </div>

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-risk-high">{error}</div>}

      <Card>
        {loading ? (
          <div className="text-sm text-gray-500">Chargement...</div>
        ) : logs.length === 0 ? (
          <div className="text-sm text-gray-500">Aucune entree d'audit.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b text-gray-500">
                  <th className="py-2 pr-3">Prediction</th>
                  <th className="py-2 pr-3">Agent</th>
                  <th className="py-2 pr-3">Decision</th>
                  <th className="py-2 pr-3">Override</th>
                  <th className="py-2 pr-3">Date</th>
                  <th className="py-2">Justification</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((l) => (
                  <tr key={l.audit_id} className="border-b last:border-0 align-top">
                    <td className="py-2 pr-3 font-mono text-xs">{l.prediction_id}</td>
                    <td className="py-2 pr-3">{l.agent_id ?? "—"}</td>
                    <td className="py-2 pr-3">{l.agent_decision ?? "—"}</td>
                    <td className="py-2 pr-3">{l.is_override ? "Oui" : "Non"}</td>
                    <td className="py-2 pr-3 text-gray-500">{formatDate(l.created_at)}</td>
                    <td className="py-2 text-gray-600">{l.agent_justification ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
