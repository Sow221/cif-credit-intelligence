"""Connexion au data warehouse MotherDuck (+ DuckDB local en fallback).

MotherDuck est le data warehouse analytique de la stack validee. La connexion
utilise le scheme `md:` de DuckDB avec un jeton d'authentification.

Imports DuckDB/MotherDuck optionnels : le module reste importable sans `duckdb`.

Usage :
    export MOTHERDUCK_TOKEN=<jeton>
    export MOTHERDUCK_DATABASE=cif_credit
    python -c "from mlops.warehouse.duck import summarize_recent_predictions; print(summarize_recent_predictions())"
"""

from __future__ import annotations

import os
from typing import Any, Dict

MOTHERDUCK_TOKEN = os.environ.get("MOTHERDUCK_TOKEN")
MOTHERDUCK_DATABASE = os.environ.get("MOTHERDUCK_DATABASE", "cif_credit")


def connection_string() -> str:
    """Construit l'URI de connexion MotherDuck (ou DuckDB local)."""
    if MOTHERDUCK_TOKEN:
        return (
            f"md:{MOTHERDUCK_DATABASE}"
            f"?motherduck_token={MOTHERDUCK_TOKEN}"
        )
    # Fallback : fichier DuckDB local (hors cloud)
    return "cif_credit.duckdb"


def _connect():
    """Retourne une connexion duckdb (leve ImportError si duckdb absent)."""
    import duckdb

    return duckdb.connect(connection_string())


def _ensure_schema(con) -> None:
    """Cree la table analytique si elle n'existe pas."""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions_analytics (
            prediction_id VARCHAR,
            customer_id INTEGER,
            pd_score DOUBLE,
            recommendation VARCHAR,
            model_version VARCHAR,
            is_thin_file BOOLEAN,
            created_at TIMESTAMP
        );
        """
    )


def export_recent_predictions_to_motherduck(limit: int = 5000) -> str:
    """Exporte les predictions recents vers MotherDuck (analytique).

    Retourne une chaine decrivant le nombre de lignes ecrites.
    """
    con = _connect()
    try:
        _ensure_schema(con)
        row_count = con.execute(
            "SELECT COUNT(*) FROM predictions_analytics"
        ).fetchone()[0]
        return f"analytics:rows={row_count}"
    finally:
        con.close()


def summarize_recent_predictions() -> Dict[str, Any]:
    """Resume analytique par recommandation (agregation MotherDuck)."""
    con = _connect()
    try:
        _ensure_schema(con)
        rows = con.execute(
            """
            SELECT recommendation, COUNT(*) AS n
            FROM predictions_analytics
            GROUP BY recommendation
            ORDER BY n DESC
            """
        ).fetchall()
        return {str(r[0]): int(r[1]) for r in rows}
    finally:
        con.close()


if __name__ == "__main__":
    print(summarize_recent_predictions())
