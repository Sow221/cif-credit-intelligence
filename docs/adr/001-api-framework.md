# ADR-001 : Cadre d'implementation de l'API

**Statut :** Accepté
**Date :** 2026-08-31
**Contexte :** L'API doit servir un contrat métier de 11 endpoints
(Dosier : Partie 3.1) : predictions de défaut, décisions, audit, versions de
modèle et rapport de drift, avec authentification et rate limiting.

## Décision
Utiliser **FastAPI** (Python 3.11) comme framework HTTP, avec :

- **Pydantic v2** pour la validation des schémas (request/response).
- **Uvicorn** (ASGI) comme serveur.
- **PyJWT** pour l'authentification Bearer (header `Authorization`).
- **slowapi** pour le rate limiting (statut 429 au dépassement).
- Middleware de request-id (`X-Request-ID`) pour la traçabilité.
- Routers par domaine : `health`, `predict`, `decisions`, `audit`,
  `models`, `reports`.

## Alternatives considérées
- **Django REST Framework** : robuste mais plus lourd et moins adapté aux
  transformations ML en temps réel.
- **Flask** : plus simple mais sans validation native ni OpenAPI générée.

## Conséquences
- Documentation OpenAPI auto-générée (`/docs`, `/redoc`).
- Schémas fortement typés garantis côté frontend (types partagés).
- 3 endpoints de santé (`/health`, `/health/live`, `/health/ready`) pour
  orchestrateur et sondes k8s.
