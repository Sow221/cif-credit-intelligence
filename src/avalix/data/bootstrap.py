"""Amorçage reproductible du projet sans dépendance à des fichiers externes.

Les données brutes et le modèle entraîné sont suivis par DVC et ne sont pas
dans le dépôt git. Ce module les régénère de façon déterministe à partir du
générateur synthétique seedé (``avalix.data.ingest.generate_synthetic``) :

    uv run avalix-bootstrap            # données + modèle, si absents
    uv run avalix-bootstrap --force    # tout régénérer

Il est aussi utilisé par la suite de tests (``tests/conftest.py``) et par la
CI, pour que n'importe qui puisse cloner le dépôt et tout exécuter.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from avalix.config import PROJECT_ROOT, get_config

CUSTOMERS_FILE = "customers_final_20260817_145043.csv"
LOANS_FILE = "loans_final_20260817_145043.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "trained" / "reproduced_model.joblib"


def raw_dir() -> Path:
    base = Path(get_config().data.raw_dir)
    return base if base.is_absolute() else PROJECT_ROOT / base


def ensure_raw_data(n_customers: int = 10_000, *, force: bool = False) -> tuple[Path, Path]:
    """Écrit les tables ``customers`` et ``loans`` synthétiques si absentes."""
    from avalix.data.ingest import generate_synthetic

    out = raw_dir()
    cust_path, loans_path = out / CUSTOMERS_FILE, out / LOANS_FILE
    if force or not (cust_path.exists() and loans_path.exists()):
        out.mkdir(parents=True, exist_ok=True)
        customers, loans = generate_synthetic(n_customers)
        customers.to_csv(cust_path, index=False)
        loans.to_csv(loans_path, index=False)
    return cust_path, loans_path


def ensure_model(*, force: bool = False) -> Path:
    """Entraîne et sauvegarde le modèle calibré si l'artefact est absent."""
    if force or not MODEL_PATH.exists():
        from avalix.data.ingest import load_customers, load_loans
        from avalix.models.train import train_pipeline

        train_pipeline(load_customers(), load_loans(), out_path=MODEL_PATH)
    return MODEL_PATH


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="avalix-bootstrap", description=__doc__)
    parser.add_argument("--n-customers", type=int, default=10_000)
    parser.add_argument("--force", action="store_true", help="régénérer même si présent")
    parser.add_argument("--data-only", action="store_true", help="ne pas entraîner le modèle")
    args = parser.parse_args(argv)

    cust, loans = ensure_raw_data(args.n_customers, force=args.force)
    print(f"Données : {cust.relative_to(PROJECT_ROOT)}, {loans.relative_to(PROJECT_ROOT)}")
    if not args.data_only:
        model = ensure_model(force=args.force)
        print(f"Modèle  : {model.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
