"""Service de construction des features a partir du payload client.

Transforme les donnees brutes + historique (epargne, prets) en 25 features
pour le modele XGBoost, dans l'ordre exact du registre.

Regles strictes (reponse.txt - correction Thin-File) :
- Client AVEC historique  -> calculer les 25 features depuis l'historique reel.
- Client SANS historique  -> NE PAS inventer de zeros : signaler thin_file.
- Le modele ne recoit JAMAIS de zeros artificiels.
"""

from typing import Any, Dict, List

import numpy as np

from src.features.registry import FeatureRegistry


class FeatureServiceError(ValueError):
    """Levee quand le payload ne permet pas de construire des features fiables."""


class FeatureService:
    """Calcule les 25 features attendues par le modele XGBoost."""

    @staticmethod
    def _one(entries: List[Dict[str, Any]], key: str) -> List[float]:
        return [float(e[key]) for e in entries]

    @staticmethod
    def is_thin_file(payload: Dict[str, Any]) -> bool:
        """Un client est Thin-File quand aucun historique n'est fourni."""
        if payload.get("has_history") is False:
            return True
        has_savings = bool(payload.get("savings_history"))
        has_loans = bool(payload.get("loan_history"))
        return not (has_savings or has_loans)

    @staticmethod
    def compute_all_features(payload: Dict[str, Any]) -> Dict[str, float]:
        """Calcule les 25 features depuis le payload complet.

        Args:
            payload: 8 champs de base + savings_history + loan_history (+ has_history).

        Raises:
            FeatureServiceError: si le payload est incomplet pour un calcul fiable.

        Returns:
            Dictionnaire des 25 features dans l'ordre du registre.
        """
        # Verification que les champs de base sont presents
        required = {
            "age",
            "seniority_months",
            "monthly_income",
            "current_savings",
            "n_past_loans",
            "current_loan_request",
            "current_loan_duration",
        }
        missing = required - set(payload.keys())
        if missing:
            raise FeatureServiceError(
                f"Champs de base manquants : {sorted(missing)}"
            )

        # Thin-File : pas d'historique -> signaler, ne pas inventer de zeros
        if FeatureService.is_thin_file(payload):
            raise FeatureServiceError(
                "Client Thin-File : aucune donnee d'historique. "
                "Ne pas appeler le modele. Forcer REVUE_HUMAINE (confidence=FAIBLE)."
            )

        features: Dict[str, float] = {}

        # Directes (7)
        features["age"] = float(payload["age"])
        features["seniority_months"] = float(payload["seniority_months"])
        features["monthly_income"] = float(payload["monthly_income"])
        features["current_savings"] = float(payload["current_savings"])
        features["n_past_loans"] = float(payload["n_past_loans"])
        features["current_loan_request"] = float(payload["current_loan_request"])
        features["current_loan_duration"] = float(payload["current_loan_duration"])

        # Derivees simples (4)
        features["loan_to_savings_ratio"] = features["current_loan_request"] / (
            features["current_savings"] + 1.0
        )
        features["loan_to_income_ratio"] = features["current_loan_request"] / (
            features["monthly_income"] + 1.0
        )
        features["savings_to_income_ratio"] = features["current_savings"] / (
            features["monthly_income"] + 1.0
        )
        features["seniority_years"] = features["seniority_months"] / 12.0

        # Agregations epargne (4) - obligatoires ici (sinon Thin-File)
        savings_history = payload.get("savings_history") or []
        if not savings_history:
            raise FeatureServiceError(
                "savings_history absent pour un client non thin-file."
            )
        balances = FeatureService._one(savings_history, "balance")
        avg = float(np.mean(balances))
        std = float(np.std(balances))
        features["avg_savings_24m"] = avg
        features["savings_std_24m"] = std
        features["savings_volatility"] = std / (avg + 1.0)
        features["savings_stability"] = 1.0 / (1.0 + features["savings_volatility"])

        # Agregations prets (8) - obligatoires ici (sinon Thin-File)
        loan_history = payload.get("loan_history") or []
        if not loan_history:
            raise FeatureServiceError("loan_history absent pour un client non thin-file.")
        amounts = FeatureService._one(loan_history, "amount")
        regularities = FeatureService._one(loan_history, "repayment_regularity")
        dpds = FeatureService._one(loan_history, "max_dpd")
        n_defaults = float(
            sum(1 for loan in loan_history if loan.get("status") == "defaulted")
        )
        features["n_loans"] = float(len(loan_history))
        features["avg_loan_amount"] = float(np.mean(amounts))
        features["total_loan_amount"] = float(np.sum(amounts))
        features["avg_repayment_regularity"] = float(np.mean(regularities))
        features["min_repayment_regularity"] = float(np.min(regularities))
        features["max_historical_dpd"] = float(np.max(dpds))
        features["mean_historical_dpd"] = float(np.mean(dpds))
        features["n_defaults"] = n_defaults

        # Derivees des agregations (2)
        features["historical_default_rate"] = features["n_defaults"] / (
            features["n_loans"] + 1.0
        )
        features["overall_payment_regularity"] = (
            features["n_loans"] * features["avg_repayment_regularity"]
        ) / (features["n_loans"] + 1.0)

        # Garantir l'ordre exact du registre (25 features)
        return {name: features[name] for name in FeatureRegistry.all_features()}
