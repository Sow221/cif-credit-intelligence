"""Risk engine (P0, etape 11).

Interface unifiee du scoring de risque. Encapsule le modele XGBoost existant
(predictor) derriere une interface stable :

    score(features, model_version, feature_set) -> pd_raw, model_version,
                                                   feature_set_id, prediction_timestamp

Le service de scoring appelle `RiskEngine` et JAMAIS directement
`XGBClassifier` ou une API MLflow specifique (consigne section 18).
L'algorithme de scoring est ainsi remplacable (XGBoost reste notre baseline)
sans changer les appelants.
"""

import uuid
from datetime import UTC, datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

from src.features.registry import FeatureRegistry
from src.models.predictor import Predictor
from src.services.feature_service import FeatureService


@dataclass
class RiskScore:
    """Resultat brut du scoring (avant decision / calibration)."""

    pd_raw: float
    model_version: str
    feature_set_id: str
    prediction_timestamp: str
    model_source: str


class RiskEngine:
    """Enveloppe de scoring encapsulant le modele XGBoost officiel."""

    def __init__(self, predictor: Optional[Predictor] = None) -> None:
        self._predictor = predictor

    @property
    def predictor(self) -> Optional[Predictor]:
        return self._predictor

    def is_available(self) -> bool:
        return self._predictor is not None and self._predictor.is_loaded()

    def score(
        self,
        features: Dict[str, float],
        model_version: Optional[str] = None,
        feature_set: str = "FULL_ADMISSIBLE",
    ) -> RiskScore:
        """Scoring d'un vecteur de features (ordre du registre).

        Args:
            features: dictionnaire des 25 features (nom -> valeur) ou payload.
            model_version: version du modele utilisee (defaut : celle du modele).
            feature_set: identifiant du feature set source (etape 9).

        Returns:
            RiskScore avec pd_raw, model_version, feature_set_id et timestamp.
        """
        vector = self._to_vector(features)
        proba = self._predict(features, vector)
        version = model_version or (
            self._predictor.model_version if self._predictor else "unknown"
        )
        return RiskScore(
            pd_raw=float(proba),
            model_version=version,
            feature_set_id=feature_set,
            prediction_timestamp=datetime.now(UTC).isoformat(),
            model_source=self._predictor.source if self._predictor else "none",
        )

    def score_payload(
        self,
        payload: Dict[str, Any],
        model_version: Optional[str] = None,
        feature_set: str = "FULL_ADMISSIBLE",
    ) -> RiskScore:
        """Scoring depuis un payload client brut (calcul des features internes).

        Encapsule FeatureService + score : le service de scoring n'appelle que
        RiskEngine, jamais XGBClassifier ni MLflow directement.
        """
        features = FeatureService.compute_all_features(payload)
        return self.score(
            features=features,
            model_version=model_version,
            feature_set=feature_set,
        )

    # ------------------------------------------------------------------- interne

    def _to_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Construit le vecteur du modele dans l'ordre exact du registre."""
        names = FeatureRegistry.all_features()
        if set(features.keys()) == set(names):
            return np.array([[float(features[name]) for name in names]])
        # Payload brut : on extrait les champs du registre presents, le reste NaN.
        return np.array([[self._extract(features, name) for name in names]])

    def _extract(self, payload: Dict[str, Any], name: str) -> float:
        if name in payload:
            return float(payload[name])
        return float("nan")

    def _predict(self, features: Dict[str, Any], vector: np.ndarray) -> float:
        """Appelle la couche modele (predictor) ; jamais XGBClassifier ici."""
        if self._predictor is None or not self._predictor.is_loaded():
            raise RuntimeError("Risk engine indisponible : modele non charge")
        return float(self._predictor.model.predict_proba(vector)[0][1])