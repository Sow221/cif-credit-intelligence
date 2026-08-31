"""Service d'eligibilite (P0, etape 4).

Repond a la question ELIGIBLE ? avant d'evaluer le risque puis la decision.
L'eligibilite est DISTINCTE du risque : une application peut etre eligible
mais risquee, et inversement.

Les regles sont CONFIGURABLES et versionnees : aucune valeur de seuil n'est
codee en dur dans la logique. Le service accepte des regles injectees
(source a terme : decision_policies.eligibility_rules) et retombe sur un
jeu de regles par defaut versionne surchargeable.
"""

from datetime import datetime

from src.schemas.eligibility import (
    EligibilityInput,
    EligibilityReason,
    EligibilityResult,
    EligibilityRules,
    EligibilityStatus,
)


# Regles par defaut versionnees (config surchargeable, pas une logique en dur).
DEFAULT_ELIGIBILITY_RULES = EligibilityRules(
    rules_version="1.0",
    age_min=18,
    amount_min=0,
    term_min=1,
)


class EligibilityService:
    """Verifie l'eligibilite d'une candidature selon des regles configurables."""

    def evaluate(
        self,
        payload: EligibilityInput,
        rules: EligibilityRules | None = None,
    ) -> EligibilityResult:
        """Applique les regles et retourne ELIGIBLE / NOT_ELIGIBLE + raisons."""
        active = rules or DEFAULT_ELIGIBILITY_RULES
        reasons: list[EligibilityReason] = []

        def _check(condition: bool, code: str, message: str) -> None:
            if not condition:
                reasons.append(EligibilityReason(code=code, message=message))

        if active.age_min is not None:
            age = payload.client_age
            _check(
                age is not None and age >= active.age_min,
                "AGE_MIN",
                f"Age (moyenne {age}) inferieur au minimum {active.age_min}",
            )
        if active.age_max is not None:
            age = payload.client_age
            _check(
                age is not None and age <= active.age_max,
                "AGE_MAX",
                f"Age (moyenne {age}) superieur au maximum {active.age_max}",
            )
        if active.amount_min is not None:
            amt = payload.requested_amount
            _check(
                amt is not None and amt >= active.amount_min,
                "AMOUNT_MIN",
                f"Montant demande ({amt}) inferieur au minimum {active.amount_min}",
            )
        if active.amount_max is not None:
            amt = payload.requested_amount
            _check(
                amt is not None and amt <= active.amount_max,
                "AMOUNT_MAX",
                f"Montant demande ({amt}) superieur au maximum {active.amount_max}",
            )
        if active.term_min is not None:
            term = payload.requested_term
            _check(
                term is not None and term >= active.term_min,
                "TERM_MIN",
                f"Duree ({term}) inferieure au minimum {active.term_min}",
            )
        if active.term_max is not None:
            term = payload.requested_term
            _check(
                term is not None and term <= active.term_max,
                "TERM_MAX",
                f"Duree ({term}) superieure au maximum {active.term_max}",
            )
        if active.allowed_currencies is not None:
            _check(
                payload.currency in active.allowed_currencies,
                "CURRENCY_NOT_ALLOWED",
                f"Devise {payload.currency} non autorisee",
            )
        if active.allowed_products is not None:
            _check(
                payload.product_id in active.allowed_products,
                "PRODUCT_NOT_ALLOWED",
                f"Produit {payload.product_id} non autorise",
            )

        status = (
            EligibilityStatus.ELIGIBLE if not reasons else EligibilityStatus.NOT_ELIGIBLE
        )
        return EligibilityResult(
            status=status,
            eligible=status == EligibilityStatus.ELIGIBLE,
            reasons=reasons,
            rules_version=active.rules_version,
            evaluated_at=datetime.utcnow(),
        )
