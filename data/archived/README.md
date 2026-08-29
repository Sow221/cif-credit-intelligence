# Archives de données

Ce dossier contient des artefacts de données **retirés du pipeline actif**,
conservés à des fins de traçabilité et d'audit. Ils ne doivent **jamais** être
réinjectés dans un entraînement sans validation préalable.

## `contaminated/`

### `features_prepared_20260817_140211.csv` — SANCTIONNÉ (fuite de la cible)

- **Contexte** : fichier de features du **tout premier prototype** (modèle
  logistique, `best_model_20260817_140415.joblib`, AUC ≈ 0.56). Non retenu
  comme modèle officiel.
- **Motif de la sanction** : contient la colonne **`p_default_true`**, qui est
  la probabilité de défaut *de génération* du jeu synthétique (elle encode la
  cible `is_default` par construction). Son inclusion dans un entraînement
  constituerait un **leakage catégorique**.
- **Risque réel** : ce fichier est la source supposée de `best_model_140415`
  (AUC 0.56). Son utilisation est disqualifiante pour un audit CIF.
- **Preuve objective** : le garde anti-leakage (`tests/test_anti_leakage.py`,
  `test_processed_features_are_contamination_free`) détecte `p_default_true`
  dans ce fichier et **bloque** son usage. C'est pourquoi il a été archivé ici.
- **Le modèle officiel** (`MODEL_OFFICIAL_CALIBRATED.joblib`, 25 features,
  listées dans `configs/params.yaml` → `features.list`) **ne contient pas**
  `p_default_true` : voir `data/processed/feature_columns.json`.

### Règle d'or

Toute nouvelle version de `features_prepared_*.csv` dans `data/processed/`
passe obligatoirement le garde anti-leakage. Un fichier qui échoue est archivé
ici — jamais utilisé pour entraîner.
