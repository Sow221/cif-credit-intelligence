"""Ingestion des données brutes CIF.

Charge les tables ``customers`` et ``loans`` depuis ``data/raw``, et
fournit un générateur synthétique seedé (LFSR + normal distorsions) pour
permettre une reproduction déterministe de la phase synthétique.

Le split est TOUJOURS temporel (protocole CIF) ; jamais aléatoire.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from cifci.config import PROJECT_ROOT, get_config


def _resolve(rel: str, base_dir: str | None = None) -> Path:
    base = Path(base_dir) if base_dir else Path(get_config().data.raw_dir)
    if base.is_absolute():
        return base / rel
    return PROJECT_ROOT / base / rel


def load_customers(
    filename: str = "customers_final_20260817_145043.csv",
    *,
    raw_dir: str | None = None,
) -> pd.DataFrame:
    """Charge la table ``customers`` brute."""
    path = _resolve(filename, raw_dir)
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier clients introuvable : {path}. "
            "Placez les données CIF dans data/raw/."
        )
    return pd.read_csv(path)


def load_loans(
    filename: str = "loans_final_20260817_145043.csv",
    *,
    raw_dir: str | None = None,
) -> pd.DataFrame:
    """Charge la table ``loans`` (historique de remboursement) brute."""
    path = _resolve(filename, raw_dir)
    if not path.exists():
        raise FileNotFoundError(f"Fichier prêts introuvable : {path}.")
    return pd.read_csv(path)


def generate_synthetic(
    n_customers: int = 10_000,
    *,
    seed: int | None = None,
    target_default_rate: float | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Génère un jeu synthétique seedé (customers + loans).

    Reproduction DÉTERMINISTE : même ``seed`` → mêmes données.
    N'inclut AUCUNE variable interdite (voir ``features.validate``).

    Args:
        n_customers: nombre de clients à générer.
        seed: graine aléatoire (défaut: params.yaml ``random_seed``).
        target_default_rate: taux de défaut cible simulé (défaut: params.yaml).

    Returns:
        (customers_df, loans_df)
    """
    cfg = get_config()
    seed = cfg.data.random_seed if seed is None else seed
    tdr = (
        cfg.data.target_default_rate
        if target_default_rate is None
        else target_default_rate
    )

    rng = np.random.default_rng(seed)

    customer_id = np.arange(1, n_customers + 1)
    age = rng.integers(21, 65, size=n_customers)
    seniority_months = rng.integers(3, 240, size=n_customers)
    monthly_income = np.round(rng.lognormal(mean=12.0, sigma=0.45, size=n_customers), 2)
    current_savings = np.round(
        rng.lognormal(mean=10.0, sigma=0.9, size=n_customers), 2
    )
    avg_savings_24m = np.round(current_savings * rng.uniform(0.6, 1.4, n_customers), 2)
    savings_std_24m = np.round(
        np.abs(avg_savings_24m * rng.uniform(0.05, 0.5, n_customers)), 2
    )
    savings_volatility = savings_std_24m / np.maximum(avg_savings_24m, 1.0)
    savings_stability = 1.0 - np.clip(savings_volatility, 0, 1)
    n_past_loans = rng.integers(0, 8, size=n_customers)
    current_loan_request = np.round(
        rng.lognormal(mean=11.0, sigma=0.5, size=n_customers), 2
    )
    current_loan_duration = rng.integers(3, 36, size=n_customers)

    n_defaults_sim = np.clip(rng.poisson(0.25, size=n_customers), 0, n_past_loans)
    p_default = np.clip(
        0.02 + savings_volatility * 0.3 + (n_defaults_sim > 0) * 0.3
        - savings_stability * 0.2,
        0.0,
        0.95,
    )
    # Ajustement du taux de défaut global vers la cible
    mu = p_default.mean()
    p_default = np.clip(p_default * (tdr / mu) if mu > 0 else p_default, 0.0, 0.99)
    is_default = (rng.random(n_customers) < p_default).astype(int)

    gender = rng.choice(["M", "F"], size=n_customers, p=[0.45, 0.55])
    sector = rng.choice(
        ["commerce", "agriculture", "elevage", "services", "artisanat"],
        size=n_customers,
    )
    location = rng.choice(
        ["urbain", "semi-urbain", "rural"], size=n_customers, p=[0.4, 0.35, 0.25]
    )

    customers = pd.DataFrame(
        {
            "customer_id": customer_id,
            "age": age,
            "gender": gender,
            "sector": sector,
            "location": location,
            "seniority_months": seniority_months,
            "monthly_income": monthly_income,
            "current_savings": current_savings,
            "avg_savings_24m": avg_savings_24m,
            "savings_std_24m": savings_std_24m,
            "savings_volatility": np.round(savings_volatility, 4),
            "savings_stability": np.round(savings_stability, 4),
            "n_past_loans": n_past_loans,
            "current_loan_request": current_loan_request,
            "current_loan_duration": current_loan_duration,
            "current_loan_purpose": rng.choice(
                ["equipement", "stock", "agriculture", "consommation", "formation"],
                size=n_customers,
            ),
            "loan_to_savings_ratio": np.round(
                current_loan_request / np.maximum(current_savings, 1.0), 4
            ),
            "is_default": is_default,
        }
    )

    loans = _generate_loans(rng, customers, n_defaults_sim)
    return customers, loans


def _generate_loans(
    rng: np.random.Generator,
    customers: pd.DataFrame,
    n_defaults_sim: np.ndarray,
) -> pd.DataFrame:
    """Génère l'historique de prêts à partir de la table clients."""
    rows: list[dict] = []
    for idx, cust in customers.iterrows():
        cid = int(cust["customer_id"])
        n_loans = int(cust["n_past_loans"])
        n_def = int(n_defaults_sim[idx])
        for k in range(n_loans):
            is_default = k < n_def
            loan_amount = np.round(
                cust["current_loan_request"]
                * rng.uniform(0.3, 1.2),
                2,
            )
            loan_duration = int(rng.integers(3, 36))
            repayment_regularity = (
                rng.uniform(0.65, 1.0) if not is_default else rng.uniform(0.2, 0.6)
            )
            max_dpd = 0 if not is_default else int(rng.integers(60, 180))
            n_payments = int(loan_duration // 1)
            payments_on_time = int(
                np.round(repayment_regularity * n_payments)
            )
            rows.append(
                {
                    "customer_id": cid,
                    "loan_amount": loan_amount,
                    "loan_duration": loan_duration,
                    "loan_status": "default" if is_default else "repaid",
                    "repayment_regularity": round(repayment_regularity, 4),
                    "max_dpd": max_dpd,
                    "n_payments": n_payments,
                    "payments_on_time": payments_on_time,
                }
            )
    return pd.DataFrame(rows)
