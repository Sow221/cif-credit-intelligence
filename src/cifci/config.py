"""Configuration centralisée du projet (lecture de ``configs/params.yaml``).

Utilise ``pydantic-settings`` pour garantir le typage et la validation des
paramètres au chargement — on échoue tôt plutôt que silencieusement.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

# Racine du dépôt (trois niveaux au-dessus de ce fichier : src/cifci/config.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARAMS_PATH = PROJECT_ROOT / "configs" / "params.yaml"


class DataConfig(BaseModel):
    raw_dir: str = "data/raw"
    processed_dir: str = "data/processed"
    test_adversarial_dir: str = "data/test_adversarial"
    random_seed: int = 42
    target_default_rate: float = 0.1183
    split: str = "temporal"


class ModelConfig(BaseModel):
    algorithm: str = "xgboost"
    objective: str = "binary:logistic"
    eval_metric: str = "aucpr"
    n_estimators: int = 300
    max_depth: int = 5
    learning_rate: float = 0.05
    subsample: float = 0.9
    colsample_bytree: float = 0.8
    random_state: int = 42
    early_stopping_rounds: int = 30


class CalibrationConfig(BaseModel):
    method: str = "isotonic"


class EvaluationConfig(BaseModel):
    metrics: list[str] = Field(default_factory=list)
    bootstrap_splits: int = 1000
    confidence_level: float = 0.95
    time_windows: int = 5


class ProjectConfig(BaseModel):
    """Configuration complète du projet."""
    project: dict = Field(default_factory=dict)
    data: DataConfig = DataConfig()
    features: dict = Field(default_factory=dict)
    model: ModelConfig = ModelConfig()
    calibration: CalibrationConfig = CalibrationConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    decision_engine: dict = Field(default_factory=dict)
    cost_model: dict = Field(default_factory=dict)


def load_config(path: Path | None = None) -> ProjectConfig:
    """Charge et valide la configuration depuis params.yaml.

    Args:
        path: Chemin vers le fichier de paramètres. Défaut: configs/params.yaml.

    Raises:
        FileNotFoundError: si le fichier de paramètres est introuvable.
        ValidationError: si la configuration est invalide.
    """
    cfg_path = path or DEFAULT_PARAMS_PATH
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"Fichier de paramètres introuvable : {cfg_path}. "
            "Vérifiez configs/params.yaml."
        )
    with cfg_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    try:
        return ProjectConfig.model_validate(raw)
    except ValidationError as exc:
        raise ValidationError(f"Configuration invalide dans {cfg_path}") from exc


# Instance partagée (cache simple) — charge une fois pour toute la session.
_cached: ProjectConfig | None = None


def get_config(*, reload: bool = False) -> ProjectConfig:
    """Retourne la configuration chargée une seule fois (singleton léger)."""
    global _cached
    if _cached is None or reload:
        _cached = load_config()
    return _cached
