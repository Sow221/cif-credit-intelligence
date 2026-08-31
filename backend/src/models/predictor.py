"""Predictor : interface du modele XGBoost.

Charge le modele depre MLflow Registry (`models:/microcredit_risk/Production`,
stack validee) ou, en fallback, depuis un fichier `.joblib` local (tests/CI
hors VM). Utilise le FeatureService pour construire les 25 features puis
produit la probability of default (PD).
"""

import logging
from typing import Any, Dict, Optional

import joblib
import numpy as np

from src.features.registry import FeatureRegistry
from src.services.feature_service import FeatureService

logger = logging.getLogger(__name__)

DEFAULT_REGISTRY_MODEL = "models:/microcredit_risk/Production"


class ModelUnavailableError(RuntimeError):
    """Levee quand le modele n'a pas pu etre charge."""


class Predictor:
    """Enveloppe du modele XGBoost officiel (Registry ou fichier)."""

    def __init__(
        self,
        model_path: str,
        model_uri: Optional[str] = None,
        mlflow_tracking_uri: str = "http://localhost:5001",
    ) -> None:
        self._model_path = model_path
        self._model_uri = model_uri
        self._mlflow_tracking_uri = mlflow_tracking_uri
        self._model = None
        self._source = "file" if not model_uri else f"registry:{model_uri}"
        self.load()

    def load(self) -> None:
        if self._model_uri:
            try:
                import mlflow

                mlflow.set_tracking_uri(self._mlflow_tracking_uri)
                self._model = mlflow.sklearn.load_model(self._model_uri)
                self._source = f"registry:{self._model_uri}"
                self._check_features()
                return
            except Exception as exc:  # noqa: BLE001 - fallback volontaire
                logger.warning(
                    "Registry MLflow indisponible (%s) ; fallback vers le fichier.",
                    exc,
                )
        self._load_from_file()

    def _load_from_file(self) -> None:
        try:
            self._model = joblib.load(self._model_path)
        except Exception as exc:  # pragma: no cover - depend de l'environnement
            raise ModelUnavailableError(
                f"Impossible de charger le modele depuis {self._model_path}"
            ) from exc
        self._source = f"file:{self._model_path}"
        self._check_features()

    def _check_features(self) -> None:
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

    def is_loaded(self) -> bool:
        """Indique si le modele est effectivement charge en memoire."""
        return self._model is not None

    @property
    def source(self) -> str:
        """Origine du modele (`registry:...` ou `file:...`)."""
        return self._source

    @property
    def model_version(self) -> str:
        if self._source.startswith("registry:"):
            return self._model_uri or DEFAULT_REGISTRY_MODEL
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
