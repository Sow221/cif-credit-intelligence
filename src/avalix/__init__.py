"""Avalix — infrastructure de décision et de suivi du risque crédit.

Package central du projet. Chaque sous-module couvre une étape de la pipeline :

- ``avalix.data``      : ingestion et génération des données (synthétiques / réelles)
- ``avalix.features``  : feature engineering + gardes anti-leakage
- ``avalix.models``    : entraînement, calibration, registre de modèles
- ``avalix.evaluate``  : métriques, bootstrap IC95, fairness, drift, coût
- ``avalix.decision``  : moteur de décision (approbation / revue / ajustement / refus)
- ``avalix.explain``   : explicabilité (SHAP)
- ``avalix.api``       : service de scoring (FastAPI)
"""

__version__ = "0.1.0"
