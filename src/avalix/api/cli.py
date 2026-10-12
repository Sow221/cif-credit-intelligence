"""CLI de prédiction ponctuelle (utilitaire ligne de commande)."""

from __future__ import annotations

import argparse
import json
import sys

from avalix.api.app import load_artifact


def predict_cli(argv: list[str] | None = None) -> int:
    """Lit les features d'un client depuis stdin (JSON) et affiche le score."""
    parser = argparse.ArgumentParser(prog="avalix-predict")
    parser.add_argument("--model", type=str, help="Chemin vers l'artefact joblib")
    parser.add_argument(
        "--json", type=str, default="-", help="JSON des features (ou '-' pour stdin)"
    )
    args = parser.parse_args(argv)

    raw = sys.stdin.read() if args.json == "-" else args.json
    try:
        values = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Erreur JSON : {exc}", file=sys.stderr)
        return 2

    artifact = load_artifact(args.model if args.model else None)
    from avalix.api.app import predict_proba_row
    from avalix.decision.engine import decide

    p = predict_proba_row(artifact, values)
    decision = decide([p])["decision"].tolist()[0]
    print(json.dumps({"probability_default": p, "decision": decision}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(predict_cli())
