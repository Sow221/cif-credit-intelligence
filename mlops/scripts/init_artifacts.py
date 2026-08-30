"""
Script d'initialisation des artefacts ML.
Copie les modèles depuis l'ancien projet vers mlops/artifacts/.

Usage :
    python mlops/scripts/init_artifacts.py

Source attendue :
    <ancienne racine projet>/02_MODELS/trained/MODEL_OFFICIAL.joblib

Destination :
    mlops/artifacts/MODEL_OFFICIAL.joblib
"""

import shutil
from pathlib import Path

SOURCE_DIR = Path(
    "C:/Users/MS/Desktop/DEV/CIF_CREDIT_INTELLIGENCE-20260817T205307Z-1-001"
    "/CIF_CREDIT_INTELLIGENCE/02_MODELS/trained"
)
DEST_DIR = Path(__file__).parent.parent / "artifacts"

MODELS = [
    "MODEL_OFFICIAL.joblib",
    "MODEL_OFFICIAL_CALIBRATED.joblib",
]


def main() -> None:
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    for model_name in MODELS:
        src = SOURCE_DIR / model_name
        dest = DEST_DIR / model_name

        if src.exists() and not dest.exists():
            shutil.copy2(src, dest)
            print(f"Copié : {model_name}")
        elif dest.exists():
            print(f"Déjà présent : {model_name}")
        else:
            print(f"Introuvable : {src}")

    print("\nInitialisation des artefacts terminée.")


if __name__ == "__main__":
    main()
