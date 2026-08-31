# Grafana Cloud — Monitoring CIF Credit Intelligence

Grafana Cloud est le monitoring visuel de la stack validée. Il consomme les
métriques collectées par Prometheus (déployé via `docker-compose`).

## Métriques exposées par l'API (`GET /metrics`)

| Métrique | Type | Sens |
|----------|------|------|
| `cif_predictions_total` | Counter | Nombre de prédictions traitées |
| `cif_requests_total` | Counter | Nombre de requêtes HTTP reçues |
| `cif_model_loaded` | Gauge | 1 si le modèle est chargé, 0 sinon |

L'endpoint `/metrics` est public (pas d'auth) pour le scrape Prometheus.

## Cibles Prometheus (`infrastructure/docker/prometheus/prometheus.yml`)

- `cif-api`  : `api:8000/metrics`
- `mlflow`   : `mlflow:5000`

## Connexion à Grafana Cloud

1. Créer le compte Grafana Cloud (vous) : générer un `instance_id`, une
   `region` et une `api_key` (écrivain de métriques).
2. Renseigner le bloc `remote_write` dans `prometheus.yml` (décommenté par
   l'utilisateur, car il contient des secrets) :

```yaml
remote_write:
  - url: https://prometheus-prod-<region>.grafana.net/api/prom/push
    basic_auth:
      username: <instance-id>
      password: <api-key>
```

3. Redémarrer Prometheus : `docker compose -f infrastructure/docker/docker-compose.prod.yml restart prometheus`.
4. Dans Grafana Cloud, créer un dashboard Prometheus alimenté par les métriques
   `cif_*` (predictions totales, état du modèle, latence).

> Les identifiants Grafana Cloud ne sont jamais commités (bloc `remote_write`
> laissé en commentaire dans `prometheus.yml`).
