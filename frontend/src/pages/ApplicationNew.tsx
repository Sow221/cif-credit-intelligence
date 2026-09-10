import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { Plus } from "lucide-react";
import { useClients } from "@/hooks/useClients";
import { useApplications } from "@/hooks/useApplications";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { SearchBar } from "@/components/ui/SearchBar";
import { Avatar } from "@/components/ui/Avatar";
import { PRODUCT_OPTIONS, TERM_OPTIONS } from "@/utils/constants";
import { validateNewApplication } from "@/utils/validation";

export default function ApplicationNewPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { clients } = useClients();
  const { createApplication } = useApplications();

  const [query, setQuery] = useState("");
  const [selectedClientId, setSelectedClientId] = useState("");
  const [productId, setProductId] = useState("");
  const [amount, setAmount] = useState("");
  const [term, setTerm] = useState("");
  const [purpose, setPurpose] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const matchedClients = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return clients.filter((client) =>
      `${client.first_name} ${client.last_name} ${client.phone ?? ""}`.toLowerCase().includes(q),
    );
  }, [query, clients]);

  const selectedClient = clients.find((client) => client.client_id === selectedClientId) ?? null;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const result = validateNewApplication({
      client_id: selectedClientId,
      product_id: productId,
      requested_amount: Number(amount),
      requested_term: Number(term),
      purpose,
    });
    if (!result.valid) {
      const byField: Record<string, string> = {};
      for (const err of result.errors) byField[err.field] = t(err.message);
      setFieldErrors(byField);
      return;
    }
    setFieldErrors({});
    setSubmitting(true);
    try {
      const created = await createApplication({
        client_id: selectedClientId,
        product_id: productId,
        requested_amount: Number(amount),
        currency: "XOF",
        requested_term: Number(term),
        purpose: purpose || null,
      });
      navigate(`/applications/${created.application_id}`);
    } catch {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-4 text-h1 text-primary-900">{t("applications:new.title")}</h1>

      <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
        <Card title={t("applications:new.client")}>
          <div className="flex flex-col gap-3">
            <SearchBar
              value={query}
              onChange={setQuery}
              placeholder={t("applications:new.client")}
              ariaLabel={t("applications:new.client")}
            />
            {matchedClients.length > 0 ? (
              <ul
                role="listbox"
                className="max-h-48 overflow-y-auto rounded-md border border-border"
              >
                {matchedClients.slice(0, 6).map((client) => (
                  <li key={client.client_id}>
                    <button
                      type="button"
                      role="option"
                      aria-selected={client.client_id === selectedClientId}
                      onClick={() => setSelectedClientId(client.client_id)}
                      className="flex w-full items-center gap-3 px-3 py-2 text-left hover:bg-primary-50 data-[selected=true]:bg-accent-50"
                      data-selected={client.client_id === selectedClientId}
                    >
                      <Avatar name={`${client.first_name} ${client.last_name}`} size="sm" />
                      <span className="min-w-0 flex-1">
                        <span className="block text-body-sm font-medium text-primary-900">
                          {client.first_name} {client.last_name}
                        </span>
                        <span className="block text-label text-primary-500">
                          {client.zone ?? client.phone ?? client.client_id.slice(0, 8)}
                        </span>
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
            {selectedClient ? (
              <div className="flex items-center gap-3 rounded-md border border-success-600 bg-success-50 p-3">
                <Avatar
                  name={`${selectedClient.first_name} ${selectedClient.last_name}`}
                  size="sm"
                />
                <div>
                  <p className="text-body-sm font-medium text-primary-900">
                    {selectedClient.first_name} {selectedClient.last_name}
                  </p>
                  <p className="text-label text-success-700">
                    {selectedClient.client_id.slice(0, 8)}
                  </p>
                </div>
              </div>
            ) : null}
            {fieldErrors.client_id ? (
              <p role="alert" className="text-label text-danger-600">
                {fieldErrors.client_id}
              </p>
            ) : null}
            <Button
              variant="ghost"
              type="button"
              leftIcon={<Plus aria-hidden className="h-4 w-4" />}
              onClick={() => navigate("/clients")}
            >
              {t("applications:new.createNew")}
            </Button>
          </div>
        </Card>

        <Card title={t("common:nav.applications")}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Select
              label={t("applications:new.product")}
              required
              placeholder={t("applications:filters.product")}
              options={PRODUCT_OPTIONS}
              value={productId}
              onChange={(event) => setProductId(event.target.value)}
              error={fieldErrors.product_id}
            />
            <Input
              label={`${t("applications:new.amount")} (XOF)`}
              required
              type="number"
              min={1}
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              error={fieldErrors.requested_amount}
            />
            <Select
              label={t("applications:new.term")}
              required
              placeholder={t("applications:new.term")}
              options={TERM_OPTIONS.map((value) => ({
                value: String(value),
                label: `${value} mois`,
              }))}
              value={term}
              onChange={(event) => setTerm(event.target.value)}
              error={fieldErrors.requested_term}
            />
            <Input
              label={t("applications:new.purpose")}
              value={purpose}
              onChange={(event) => setPurpose(event.target.value)}
            />
          </div>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" loading={submitting}>
            {t("applications:new.submit")}
          </Button>
        </div>
      </form>
    </div>
  );
}
