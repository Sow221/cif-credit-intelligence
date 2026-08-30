"""Predictor : interface du modele .joblib.

Charge le modele officiel, utilise le FeatureService pour construire les
25 features depuis le payload, puis produit la probability of default (PD).
"""

import logging
from typing import Any, Dict, Optional

import joblib
import numpy as np

from src.features.registry import FeatureRegistry
from src.services.feature_service import FeatureService

logger = logging.getLogger(__name__)


class ModelUnavailableError(RuntimeError):
    """Levee quand le modele n'a pas pu etre charge."""


class Predictor:
    """Enveloppe du modele XGBoost officiel."""

    def __init__(self, model_path: str) -> None:
        self._model_path = model_path
        self._model = None
        self.load()

    def load(self) -> None:
        try:
            self._model = joblib.load(self._model_path)
        except Exception as exc:  # pragma: no cover - depend de l'environnement
            raise ModelUnavailableError(
                f"Impossible de charger le modele depuis {self._model_path}"
            ) from exc
        # Verification de coherence des features
        expected = list(self._model.feature_names_in_)
        if expected != FeatureRegistry.all_features():
            logger.warning(
                "Features du modele differentes du registre. Modele=%s, registre=%s",
                expected,
                FeatureRegistry.all_features(),
            )

    @property
    def model(self):
        if self._model is None:
            raise ModelUnavailableError("Modele non charge")
        return self._model

    @property
    def model_version(self) -> str:
        return f"MODEL_OFFICIAL-{len(FeatureRegistry.all_features())}f"

    def predict_pd(self, payload: Dict[str, Any]) -> float:
        """Calcule la probability of default (PD) pour un payload client.

        Args:
            payload: donnees brutes + historiques.

        Returns:
            PD dans [0, 1] (probabilite de la classe 1).
        """
        features = FeatureService.compute_all_features(payload)
        # Ordre exact du registre
        X = np.array([[features[name] for name in FeatureRegistry.all_features()]])
        proba = self.model.predict_proba(X)[0]
        return float(proba[1])

    def feature_vector(self, payload: Dict[str, Any]) -> Dict[str, float]:
        """Retourne le vecteur des 25 features pour audit/tracabilite."""
        return FeatureService.compute_all_features(payload)
