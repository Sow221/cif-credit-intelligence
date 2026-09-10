import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { Activity } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { validateLogin } from "@/utils/validation";

export default function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { signIn, error, status } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const result = validateLogin({ username, password });
    if (!result.valid) {
      const byField: Record<string, string> = {};
      for (const err of result.errors) byField[err.field] = t(err.message);
      setFieldErrors(byField);
      return;
    }
    setFieldErrors({});
    try {
      await signIn(username, password);
      navigate("/dashboard", { replace: true });
    } catch {
      // error surface via store
    }
  }

  const loading = status === "loading";
  const isDisabled =
    Boolean(error) || fieldErrors.username !== undefined || fieldErrors.password !== undefined;

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm">
        <div className="rounded-lg border border-border bg-surface p-8 shadow-sm">
          <div className="mb-6 flex flex-col items-center gap-2 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent-600 text-white">
              <Activity aria-hidden className="h-6 w-6" />
            </div>
            <h1 className="text-h1 text-primary-900">{t("common:app.name")}</h1>
            <p className="text-body-sm text-primary-500">{t("common:app.tagline")}</p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
            <Input
              label={t("common:login.username")}
              id="username"
              name="username"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              error={fieldErrors.username ? t(fieldErrors.username) : undefined}
              data-testid="username"
            />
            <Input
              label={t("common:login.password")}
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              error={fieldErrors.password ? t(fieldErrors.password) : undefined}
              data-testid="password"
            />

            {error ? (
              <p role="alert" className="text-label text-danger-600">
                {error}
              </p>
            ) : null}

            <Button type="submit" loading={loading} disabled={isDisabled} data-testid="submit">
              {t("common:login.submit")}
            </Button>
          </form>

          <p className="mt-6 text-center text-label text-primary-500">{t("common:app.version")}</p>
        </div>
      </div>
    </div>
  );
}
