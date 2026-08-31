# ADR-003 : Choix du frontend

**Statut :** Accepté
**Date :** 2026-08-31
**Contexte :** Une interface web est nécessaire pour l'agent (formulaire de
prédiction, affichage du risque) et le superviseur (supervision des décisions
et overrides, journal d'audit).

## Décision
Utiliser **React 18 + TypeScript (strict)** avec **Vite** et **Tailwind CSS** :

- Actions centrées sur le rôle : `AgentDashboard` / `SupervisorDashboard`,
  `Login`, `AuditLog`.
- Composants UI : `Button`, `Input`, `Card`, `Badge`, `Modal`.
- Composants métier : `RiskGauge`, `ConfidenceIndicator`, `DecisionBadge`,
  `ClientForm`.
- Client HTTP typé (`services/api.ts`) aligné sur le contrat FastAPI.
- Sessions JWT côté client (`services/auth.ts`), role décodé du subject.
- Tests **Vitest** + Testing Library.
- Serveur **nginx** statique produisant le build Vite, proxys `/v1` et
  `/health` vers l'API.

## Alternatives considérées
- **Vue/nuxt** : viable, mais React + TS est plus répandu pour ce type de
  dashboard d'entreprise.
- **Next.js** : SSR non requis (application interne authentifiée), Vite plus
  léger.

## Conséquences
- Build de production (tsc -b + vite build) et gate de type strict.
- Typecheck, eslint et vitest exécutés en CI.
- Contrat de types partagé avec le backend (étapes 21-25 du Dossier).
