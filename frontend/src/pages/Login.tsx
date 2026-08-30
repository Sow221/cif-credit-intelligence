import { useState } from "react";
import { saveSession, decodeRole } from "../services/auth";
import { Button, Card, Input } from "../components/ui";

interface LoginProps {
  onLogin: (agentId: string, role: "agent" | "supervisor") => void;
}

/**
 * Page de connexion. L'API backend s'authentifie par jeton JWT (Bearer) sans
 * route de login dediee : l'agent renseigne l'identifiant agent et son jeton
 * d'acces (decerne par le service d'identite / le mode dev).
 */
export function Login({ onLogin }: LoginProps) {
  const [agentId, setAgentId] = useState("");
  const [token, setToken] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const role = decodeRole(token);
    if (!agentId.trim() || !token.trim() || !role) {
      setError("Identifiant agent et jeton valide requis.");
      return;
    }
    saveSession(token, agentId.trim(), role);
    onLogin(agentId.trim(), role);
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card title="CIF Credit Intelligence" className="w-full max-w-md">
        <form onSubmit={handleSubmit} className="grid gap-4">
          <Input
            label="Identifiant agent"
            value={agentId}
            onChange={(e) => setAgentId(e.target.value)}
            placeholder="agent-001"
            required
          />
          <Input
            label="Jeton d'acces (JWT)"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="eyJhbGciOi..."
            required
          />
          {error && <div className="rounded-md bg-red-50 p-3 text-sm text-risk-high">{error}</div>}
          <Button type="submit" size="lg">
            Se connecter
          </Button>
        </form>
      </Card>
    </div>
  );
}
