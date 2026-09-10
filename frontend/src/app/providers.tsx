import type { ReactNode } from "react";
import type { Session } from "@/services/auth";
import { useAuthStore } from "@/store/auth";
import { loadStoredSession } from "@/services/auth";

function restoreSession(): void {
  const session: Session | null = loadStoredSession();
  if (session?.user) {
    useAuthStore.getState().setAuthenticated(session.user, "");
  }
}

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  restoreSession();
  return <>{children}</>;
}
