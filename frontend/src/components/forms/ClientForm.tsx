import { useState } from "react";
import type {
  LoanEntry,
  PredictionRequest,
  PredictionResponse,
  SavingsEntry,
} from "../../types/prediction";
import { api, ApiError } from "../../services/api";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import { Card } from "../ui/Card";

interface ClientFormProps {
  onResult: (result: PredictionResponse) => void;
}

interface BaseFields {
  customer_id: string;
  age: string;
  seniority_months: string;
  monthly_income: string;
  current_savings: string;
  n_past_loans: string;
  current_loan_request: string;
  current_loan_duration: string;
}

const INITIAL_BASE: BaseFields = {
  customer_id: "",
  age: "",
  seniority_months: "",
  monthly_income: "",
  current_savings: "",
  n_past_loans: "",
  current_loan_request: "",
  current_loan_duration: "",
};

export function ClientForm({ onResult }: ClientFormProps) {
  const [base, setBase] = useState<BaseFields>(INITIAL_BASE);
  const [hasHistory, setHasHistory] = useState(true);
  const [savings, setSavings] = useState<SavingsEntry[]>([]);
  const [loans, setLoans] = useState<LoanEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const setField = (key: keyof BaseFields) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setBase((prev) => ({ ...prev, [key]: e.target.value }));

  const addSavings = () =>
    setSavings((prev) => [...prev, { month: prev.length + 1, balance: 0 }]);

  const updateSavings = (index: number, value: number) =>
    setSavings((prev) => prev.map((s, i) => (i === index ? { ...s, balance: value } : s)));

  const removeSavings = (index: number) =>
    setSavings((prev) => prev.filter((_, i) => i !== index));

  const addLoan = () =>
    setLoans((prev) => [
      ...prev,
      { loan_id: prev.length + 1, amount: 0, repayment_regularity: 1, max_dpd: 0, status: "completed" },
    ]);

  const updateLoan = (index: number, patch: Partial<LoanEntry>) =>
    setLoans((prev) => prev.map((l, i) => (i === index ? { ...l, ...patch } : l)));

  const removeLoan = (index: number) => setLoans((prev) => prev.filter((_, i) => i !== index));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const payload: PredictionRequest = {
        customer_id: Number(base.customer_id),
        age: Number(base.age),
        seniority_months: Number(base.seniority_months),
        monthly_income: Number(base.monthly_income),
        current_savings: Number(base.current_savings),
        n_past_loans: Number(base.n_past_loans),
        current_loan_request: Number(base.current_loan_request),
        current_loan_duration: Number(base.current_loan_duration),
        has_history: hasHistory,
        savings_history: hasHistory ? savings : undefined,
        loan_history: hasHistory && Number(base.n_past_loans) > 0 ? loans : undefined,
      };
      const result = await api.predict(payload);
      onResult(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur inattendue pendant la prediction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="grid gap-6">
      <Card title="Donnees du client">
        <div className="grid grid-cols-2 gap-4">
          <Input label="ID client" type="number" required value={base.customer_id} onChange={setField("customer_id")} />
          <Input label="Age" type="number" required min={18} max={100} value={base.age} onChange={setField("age")} />
          <Input label="Anciennete (mois)" type="number" required min={0} value={base.seniority_months} onChange={setField("seniority_months")} />
          <Input label="Revenu mensuel" type="number" required min={0} value={base.monthly_income} onChange={setField("monthly_income")} />
          <Input label="Epargne courante" type="number" required min={0} value={base.current_savings} onChange={setField("current_savings")} />
          <Input label="Nombre de prets passes" type="number" required min={0} max={50} value={base.n_past_loans} onChange={setField("n_past_loans")} />
          <Input label="Montant du pret demande" type="number" required min={0} value={base.current_loan_request} onChange={setField("current_loan_request")} />
          <Input label="Duree du pret (mois)" type="number" required min={1} max={60} value={base.current_loan_duration} onChange={setField("current_loan_duration")} />
        </div>
      </Card>

      <Card title="Historique">
        <label className="mb-3 flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={hasHistory}
            onChange={(e) => setHasHistory(e.target.checked)}
          />
          Client avec historique (cocher seulement si le client n'est pas Thin-File)
        </label>

        {hasHistory && (
          <div className="grid gap-4">
            <div>
              <div className="mb-2 flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-700">Historique d'epargne</h4>
                <Button type="button" variant="secondary" size="sm" onClick={addSavings}>
                  + Ajouter
                </Button>
              </div>
              {savings.map((s, i) => (
                <div key={i} className="mb-2 flex items-center gap-2">
                  <span className="w-32 text-sm text-gray-600">Mois {s.month}</span>
                  <Input
                    type="number"
                    min={0}
                    value={s.balance}
                    onChange={(e) => updateSavings(i, Number(e.target.value))}
                    aria-label={`Solde mois ${s.month}`}
                  />
                  <Button type="button" variant="danger" size="sm" onClick={() => removeSavings(i)}>
                    &times;
                  </Button>
                </div>
              ))}
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-700">Historique des prets</h4>
                <Button type="button" variant="secondary" size="sm" onClick={addLoan}>
                  + Ajouter
                </Button>
              </div>
              {loans.map((l, i) => (
                <div key={i} className="mb-3 grid grid-cols-2 gap-2 rounded border p-2">
                  <Input
                    label="Montant"
                    type="number"
                    min={0}
                    value={l.amount}
                    onChange={(e) => updateLoan(i, { amount: Number(e.target.value) })}
                  />
                  <Input
                    label="Regularite (0-1)"
                    type="number"
                    min={0}
                    max={1}
                    step={0.01}
                    value={l.repayment_regularity}
                    onChange={(e) => updateLoan(i, { repayment_regularity: Number(e.target.value) })}
                  />
                  <Input
                    label="Max DPD"
                    type="number"
                    min={0}
                    max={90}
                    value={l.max_dpd}
                    onChange={(e) => updateLoan(i, { max_dpd: Number(e.target.value) })}
                  />
                  <div>
                    <label className="text-sm font-medium text-gray-700">Statut</label>
                    <select
                      className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                      value={l.status}
                      onChange={(e) =>
                        updateLoan(i, { status: e.target.value as LoanEntry["status"] })
                      }
                    >
                      <option value="completed">Termine</option>
                      <option value="defaulted">En defaut</option>
                    </select>
                  </div>
                  <div className="col-span-2 flex justify-end">
                    <Button type="button" variant="danger" size="sm" onClick={() => removeLoan(i)}>
                      Supprimer
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-risk-high">{error}</div>}

      <Button type="submit" size="lg" isLoading={loading}>
        {loading ? "Calcul du score..." : "Lancer la prediction"}
      </Button>
    </form>
  );
}
