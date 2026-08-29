"""CIF Credit Intelligence — infrastructure de décision et de suivi du risque crédit.

Package central du projet. Chaque sous-module couvre une étape de la pipeline :

- ``cifci.data``      : ingestion et génération des données (synthétiques / réelles CIF)
- ``cifci.features``  : feature engineering + gardes anti-leakage
- ``cifci.models``    : entraînement, calibration, registre de modèles
- ``cifci.evaluate``  : métriques, bootstrap IC95, fairness, drift, coût
- ``cifci.decision``  : moteur de décision (approbation / revue / ajustement / refus)
- ``cifci.explain``   : explicabilité (SHAP)
- ``cifci.api``       : service de scoring (FastAPI)
"""

__version__ = "0.1.0"
