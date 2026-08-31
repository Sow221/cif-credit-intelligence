"""Generation du rapport de drift Evidently pour le modele CIF.

Compare un jeu de reference (production) a un jeu courant et produit :
- un tableau de data drift sur les 25 features,
- un rapport de qualite,
- le declenchement d'une alerte si le taux de drift depasse le seuil.

Le rapport est journalise dans MLflow (artefact HTML + metriques).

Usage :
    python mlops/monitoring/drift_report.py \
        --reference data_ref.csv --current data_cur.csv [--no-mlflow]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HTML_OUT = ROOT / "mlops" / "monitoring" / "reports"
JSON_OUT = ROOT / "mlops" / "monitoring" / "reports"


def _load_or_die(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        print(f"[error] Le fichier est vide : {path}", file=sys.stderr)
        raise SystemExit(1)
    return df


def _drifted_columns(drift_df: pd.DataFrame, threshold: float) -> list:
    """Colonnes dont la metrique de drift depasse le seuil."""
    if drift_df is None or drift_df.empty:
        return []
    out = []
    score_col = None
    for col in drift_df.columns:
        if "drift score" in str(col).lower() or str(col).lower() == "drift_score":
            score_col = col
            break
    if score_col is None:
        return []
    for _, row in drift_df.iterrows():
        try:
            if float(row[score_col]) > threshold:
                out.append(str(row.get("column_name", "")))
        except (TypeError, ValueError):
            continue
    return [c for c in out if c]


def main() -> int:
    parser = argparse.ArgumentParser(description="Rapport de drift Evidently")
    parser.add_argument("--reference", required=True, help="CSV de reference (production)")
    parser.add_argument("--current", required=True, help="CSV courant (prelevement)")
    parser.add_argument("--no-mlflow", action="store_true")
    args = parser.parse_args()

    reference = _load_or_die(args.reference)
    current = _load_or_die(args.current)

    try:
        from evidently.report import Report
        from evidently.metric_preset import DataDriftPreset, DataQualityPreset
    except ImportError as exc:  # pragma: no cover
        print(f"[error] Evidently non installe : {exc}", file=sys.stderr)
        return 1

    drift_report = Report(metrics=[DataDriftPreset(), DataQualityPreset()])
    drift_report.run(reference_data=reference, current_data=current)

    drift_table = drift_report.as_dict()["metrics"][0]["result"]
    total = drift_table.get("number_of_columns", 0)
    drifted = drift_table.get("number_of_drifted_columns", 0)
    share = (drifted / total) if total else 0.0
    columns_drift = drift_table.get("columns", {})

    HTML_OUT.mkdir(parents=True, exist_ok=True)
    JSON_OUT.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    html_path = HTML_OUT / f"drift_{ts}.html"
    json_path = JSON_OUT / f"drift_{ts}.json"
    drift_report.save_html(str(html_path))

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_columns": total,
        "drifted_columns": drifted,
        "drift_share": round(share, 4),
        "threshold": 0.3,
        "alert": share > 0.3,
        "columns": columns_drift,
        "report_json": str(json_path),
        "report_html": str(html_path),
    }
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    if not args.no_mlflow:
        try:
            import mlflow

            mlflow.set_tracking_uri("http://localhost:5001")
            with mlflow.start_run(run_name="drift-monitoring") as run:
                mlflow.log_metrics(
                    {"drift_share": share, "drifted_columns": float(drifted)}
                )
                mlflow.log_artifact(str(html_path))
                mlflow.log_param("reference", args.reference)
                mlflow.log_param("current", args.current)
            print("[ok] Rapport journalise dans MLflow:", run.info.run_id)
        except Exception as exc:  # noqa: BLE001 - MLflow optionnel
            print(f"[warn] MLflow indisponible : {exc}")

    if summary["alert"]:
        print(f"[ALERTE] Drift detecte : {drifted}/{total} colonnes ({share:.1%}).")
    else:
        print(f"[ok] Pas de drift significatif ({drifted}/{total}).")
    print("[ok] Rapport :", html_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
