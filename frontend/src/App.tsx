import { useState } from "react";
import type { Session } from "./services/auth";
import { getSession, clearSession } from "./services/auth";
import { Login } from "./pages/Login";
import { AgentDashboard } from "./pages/AgentDashboard";
import { SupervisorDashboard } from "./pages/SupervisorDashboard";
import { AuditLogPage } from "./pages/AuditLog";

type View = "dashboard" | "audit";

export function App() {
  const [session, setSession] = useState<Session | null>(() => getSession());
  const [view, setView] = useState<View>("dashboard");

  const handleLogin = (agentId: string, role: "agent" | "supervisor") => {
    const s = getSession();
    if (s) {
      setSession({ token: s.token, agentId, role });
    }
    setView("dashboard");
  };

  const handleLogout = () => {
    clearSession();
    setSession(null);
  };

  if (!session) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <h1 className="text-lg font-bold text-brand-700">
            CIF Credit Intelligence
          </h1>
          <nav className="flex items-center gap-4 text-sm">
            <button
              onClick={() => setView("dashboard")}
              className={view === "dashboard" ? "font-semibold text-brand-600" : "text-gray-600"}
            >
              {session.role === "supervisor" ? "Supervision" : "Evaluation"}
            </button>
            <button
              onClick={() => setView("audit")}
              className={view === "audit" ? "font-semibold text-brand-600" : "text-gray-600"}
            >
              Audit
            </button>
            <span className="text-gray-400">|</span>
            <span className="text-gray-600">{session.agentId}</span>
            <button onClick={handleLogout} className="text-gray-600 hover:underline">
              Deconnexion
            </button>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        {view === "dashboard" ? (
          session.role === "supervisor" ? (
            <SupervisorDashboard agentId={session.agentId} />
          ) : (
            <AgentDashboard agentId={session.agentId} />
          )
        ) : (
          <AuditLogPage />
        )}
      </main>
    </div>
  );
}
