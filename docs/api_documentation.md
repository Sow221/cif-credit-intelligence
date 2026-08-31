# Documentation API — CIF Credit Intelligence

Base : `http://<hôte>:8000` · OpenAPI : `/docs` (Swagger) · `/redoc`

Authentification requise sur `/v1/*` : en-tête `Authorization: Bearer <JWT>`.
Les routes de santé et de documentation sont publiques.

## 1. Endpoints

| Méthode | Chemin | Auth | Rate limit | Description |
|---------|--------|------|-----------|-------------|
| GET | `/health` | Non | 120/min | État du service |
| GET | `/health/live` | Non | illimité | Liveness probe |
| GET | `/health/ready` | Non | illimité | Readiness (modèle + DB) |
| POST | `/v1/predict` | JWT | 60/min | Prédiction de défaut |
| GET | `/v1/decisions` | JWT | 30/min | Liste des décisions (paginé) |
| GET | `/v1/decisions/{id}` | JWT | 30/min | Détail d'une décision |
| POST | `/v1/decisions/{id}/override` | JWT | 10/min | Override humain (audité) |
| GET | `/v1/audit` | JWT | 30/min | Journal d'audit (paginé) |
| GET | `/v1/models` | JWT | 60/min | Versions de modèle |
| GET | `/v1/reports/drift` | JWT | 5/min | Rapport de drift |

## 2. POST /v1/predict

### Corps (client avec historique)

```json
{
  "customer_id": 12345,
  "age": 35,
  "seniority_months": 48,
  "monthly_income": 850,
  "current_savings": 1200,
  "n_past_loans": 3,
  "current_loan_request": 500,
  "current_loan_duration": 12,
  "has_history": true,
  "savings_history": [
    {"month": 1, "balance": 1100},
    {"month": 2, "balance": 1150}
  ],
  "loan_history": [
    {"loan_id": 1, "amount": 400, "repayment_regularity": 0.92,
     "max_dpd": 0, "status": "completed"}
  ]
}
```

### Corps (client Thin-File)

```json
{
  "customer_id": 9999,
  "age": 30,
  "seniority_months": 0,
  "monthly_income": 700,
  "current_savings": 300,
  "n_past_loans": 0,
  "current_loan_request": 200,
  "current_loan_duration": 12,
  "has_history": false
}
```

Thin-File ⇒ réponse `200` avec `pd_score: null`, `is_thin_file: true`,
recommandation **REVUE_HUMAINE** (aucun appel au modèle, zéro artificiel).

### Réponse

```json
{
  "status": "success",
  "pd_score": 0.056,
  "confidence": {"level": "MOYENNE", "score": 0.6},
  "recommendation": {"decision": "APPROBATION", "raison": "PD=0.056 <= 0.10"},
  "is_thin_file": false,
  "model_version": "MODEL_OFFICIAL-25f",
  "request_id": "bfd63f4c-...",
  "timestamp": "2026-08-31T10:15:00Z"
}
```

## 3. Codes d'erreur

| Code | Signification | Quand |
|------|---------------|-------|
| 200 | Succès | Requête traitée |
| 401 | Non authentifié | JWT absent/invalide/expiré |
| 404 | Introuvable | decision/{id} inexistante |
| 422 | Validation | Pydantic rejette les données / historique incomplet |
| 429 | Rate limit | Quota dépassé |
| 503 | Indisponible | Modèle non chargé |

## 4. Déclenchement de décision

Le `DecisionEngine` applique R1→R6 (voir Model Card) : requiert les 25
features calculées par le `FeatureService` ; un historique incomplet lève une
erreur 422 (jamais de valeurs par défaut silencieuses).

## 5. Exemples (curl)

```bash
# Santé
curl http://localhost:8000/health

# Prédiction
curl -X POST http://localhost:8000/v1/predict \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "age": 35, "seniority_months": 48,
       "monthly_income": 850, "current_savings": 1200, "n_past_loans": 3,
       "current_loan_request": 500, "current_loan_duration": 12,
       "has_history": true, ...}'

# Override supervisé (audité)
curl -X POST http://localhost:8000/v1/decisions/<id>/override \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"agent_id": "sup-01", "decision": "REFUS", "justification": "Historique client"}'
```
