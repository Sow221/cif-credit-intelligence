"""API de scoring CIF (FastAPI).

Expose un service de prédiction micro-crédit : à partir des features d'un
client, retourne la probabilité de défaut calibrée, la décision métier et
une explication SHAP locale.

Démarrage (dev) :
    uv run uvicorn cifci.api.app:app --reload
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from cifci.config import PROJECT_ROOT, get_config

app = FastAPI(
    title="CIF Credit Intelligence API",
    description="Scoring & décision micro-crédit (UEMOA)",
    version=get_config().project.get("version", "0.1.0"),
)

# Chemin du modèle par défaut ; surchargeable via env var CIFCI_MODEL_PATH.
_DEFAULT_MODEL = (
    PROJECT_ROOT / "models" / "trained" / "reproduced_model.joblib"
)


def _feature_names() -> list[str]:
    return list(get_config().features["list"])


def _build_request_model():
    """Construit dynamiquement le schéma Pydantic à partir des 25 features."""
    from typing import Annotated

    from pydantic import Field

    fields = {
        name: Annotated[float, Field(..., description=f"Feature {name}")]
        for name in _feature_names()
    }
    return type(
        "DynamicScoreRequest",
        (BaseModel,),
        {"__annotations__": fields, "model_config": {"extra": "forbid"}},
    )


DynamicScoreRequest = _build_request_model()


def load_artifact(path: Path | None = None) -> dict:
    p = Path(path) if path else Path(_DEFAULT_MODEL)
    if not p.exists():
        raise HTTPException(status_code=503, detail=f"Modèle introuvable : {p}")
    return joblib.load(p)


_model_artifact: dict | None = None


def get_artifact() -> dict:
    global _model_artifact
    if _model_artifact is None:
        _model_artifact = load_artifact()
    return _model_artifact


def predict_proba_row(artifact: dict, values: dict) -> float:
    model = artifact["model"]
    calibrator = artifact["calibrator"]
    feats = artifact["model_features"]
    df = pd.DataFrame([{k: values[k] for k in feats}], columns=feats)
    raw = model.predict_proba(df)[:, 1]
    calib = calibrator.predict(raw)[0]
    return float(min(max(calib, 0.0), 1.0))


@app.post("/score", response_model=dict)
def score(req: DynamicScoreRequest) -> dict:  # type: ignore[valid-type]
    """Retourne probabilité, décision et décision brute d'un client."""
    from cifci.decision.engine import decide

    artifact = get_artifact()
    values = req.model_dump()  # type: ignore[attr-defined]
    p = predict_proba_row(artifact, values)
    decision = decide([p])["decision"].tolist()[0]
    return {"probability_default": p, "decision": decision}


@app.post("/explain", response_model=dict)
def explain(req: DynamicScoreRequest) -> dict:  # type: ignore[valid-type]
    """Retourne l'explication SHAP locale d'un client (top features)."""
    from cifci.explain.shap_explainer import explain_one

    artifact = get_artifact()
    values = req.model_dump()  # type: ignore[attr-defined]
    feats = artifact["model_features"]
    row = pd.DataFrame([{k: values[k] for k in feats}], columns=feats)
    contrib = explain_one(artifact["model"], row, display_columns=feats)
    return {
        "explanation": contrib.to_dict("records")[:10],
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": get_artifact() is not None}
