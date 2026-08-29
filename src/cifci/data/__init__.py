"""Ingestion des données: chargement, génération synthétique seedée."""

from cifci.data.ingest import (
    generate_synthetic,
    load_customers,
    load_loans,
)

__all__ = ["load_customers", "load_loans", "generate_synthetic"]
