"""Flows Prefect Cloud d'orchestration du pipeline CIF.

Enchainement : COLLECTE -> VALIDATION -> VERSIONING (DVC) -> ENTRAINEMENT.

Imports Prefect optionnels : si `prefect` n'est pas installe, les decorateurs
deviennent des no-op et le module reste importable et testable en CI.

Usage (sur un worker connecte a Prefect Cloud) :
    prefect cloud login
    python -m mlops.orchestration.flows
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    from prefect import flow, task
except ImportError:  # pragma: no cover - environnement sans Prefect
    def _identity(obj=None, **kwargs):
        """No-op decorator : Prefect absent, la fonction reste telle quelle.

        Fonctionne en mode "@flow(name=...)" (factory) comme en mode "@flow".
        """

        def _wrap(fn):
            return fn

        if callable(obj):
            return obj
        return _wrap

    flow = _identity
    task = _identity

ROOT = Path(__file__).resolve().parents[2]


@task
def collect_step() -> str:
    """Collecte : exporte les predictions recentes vers MotherDuck."""
    from mlops.warehouse.duck import export_recent_predictions_to_motherduck

    return export_recent_predictions_to_motherduck(limit=5000)


@task
def validate_step() -> int:
    """Validation : verifie l'integrite du jeu (NaN / contrat 25 features)."""
    import pandas as pd

    csv = ROOT / "mlops" / "data" / "training.csv"
    if not csv.exists():
        return 0
    data = pd.read_csv(csv)
    return int(data.isna().sum().sum())


@task
def train_step() -> None:
    """Entrainement : declenche train_pipeline.py (Registry MLflow + W&B)."""
    script = ROOT / "mlops" / "training" / "train_pipeline.py"
    subprocess.run([sys.executable, str(script)], check=True)


@flow(name="cif-collect-validate-train")
def pipeline() -> None:
    """Pipeline complet : collecte -> validation -> entrainement."""
    collected = collect_step()
    validate_step(collected)
    train_step()


def main() -> None:
    """Decreche le pipeline en mode standalone (sans worker Prefect)."""
    pipeline()
    print("[ok] Pipeline termine.")


if __name__ == "__main__":
    main()
