"""Feature engine (P0, etape 9-10).

Definit le registre des features (Feature Definitions) et les sets de features
versionnes (Feature Sets). Repose sur le registre central `FeatureRegistry` qui
porte les 25 features exactes du modele officiel.

Contraintes (consigne section 15-17) :
  - Chaque feature porte un statut (PROPOSED / EXPERIMENTAL / APPROVED /
    RETIRED / REJECTED). Seules les features APPROVED peuvent etre utilisees
    sur le chemin de production.
  - Les sets sont VERSIONNES : MINIMAL / BUSINESS / FINANCIAL / CREDIT /
    ALTERNATIVE / FULL_ADMISSIBLE. La version fait partie de l'identite d'un set.
  - Le choix du set pour une candidature doit etre deterministe et justifiable
    (ici aligne sur le profil d'information de l'etape 8) ; jamais de regle
    arbitraire hoc. Ne pas confondre un dossier mince avec un risque eleve.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.features.information_profiler import InformationState
from src.features.registry import FeatureRegistry


class FeatureStatus(str, Enum):
    PROPOSED = "PROPOSED"
    EXPERIMENTAL = "EXPERIMENTAL"
    APPROVED = "APPROVED"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


class FeatureGroup(str, Enum):
    MINIMAL = "MINIMAL"
    BUSINESS = "BUSINESS"
    FINANCIAL = "FINANCIAL"
    CREDIT = "CREDIT"
    ALTERNATIVE = "ALTERNATIVE"


class FeatureDefinition(BaseModel):
    """Definition d'une feature du chemin decisionnel.

    Porte les metadonnees (consigne section 16) et son statut. Seules les
    features APPROVED comptent pour le chemin de production.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    data_type: str = "numeric"
    unit: str = ""
    feature_group: FeatureGroup
    source: str = ""
    formula_reference: str = ""
    availability_rule: str = ""
    sensitivity_class: str = "LOW"
    status: FeatureStatus = FeatureStatus.APPROVED
    version: str = "1"


# ---------------------------------------------------------------------------
# Definitions des 25 features du modele (issues du FeatureRegistry)
# ---------------------------------------------------------------------------

# Groupe d'appartenance de chaque feature du modele officiel.
_FEATURE_GROUP: Dict[str, FeatureGroup] = {
    "age": FeatureGroup.BUSINESS,
    "seniority_months": FeatureGroup.BUSINESS,
    "monthly_income": FeatureGroup.BUSINESS,
    "current_savings": FeatureGroup.FINANCIAL,
    "avg_savings_24m": FeatureGroup.FINANCIAL,
    "savings_std_24m": FeatureGroup.FINANCIAL,
    "savings_volatility": FeatureGroup.FINANCIAL,
    "savings_stability": FeatureGroup.FINANCIAL,
    "n_past_loans": FeatureGroup.CREDIT,
    "current_loan_request": FeatureGroup.CREDIT,
    "current_loan_duration": FeatureGroup.CREDIT,
    "loan_to_savings_ratio": FeatureGroup.FINANCIAL,
    "n_loans": FeatureGroup.CREDIT,
    "avg_loan_amount": FeatureGroup.CREDIT,
    "total_loan_amount": FeatureGroup.CREDIT,
    "avg_repayment_regularity": FeatureGroup.CREDIT,
    "min_repayment_regularity": FeatureGroup.CREDIT,
    "max_historical_dpd": FeatureGroup.CREDIT,
    "mean_historical_dpd": FeatureGroup.CREDIT,
    "n_defaults": FeatureGroup.CREDIT,
    "loan_to_income_ratio": FeatureGroup.FINANCIAL,
    "historical_default_rate": FeatureGroup.CREDIT,
    "savings_to_income_ratio": FeatureGroup.FINANCIAL,
    "seniority_years": FeatureGroup.BUSINESS,
    "overall_payment_regularity": FeatureGroup.CREDIT,
}

# Sensitivite des features (classification au premier ordre).
_SENSITIVITY: Dict[str, str] = {
    "age": "LOW",
    "seniority_months": "LOW",
    "monthly_income": "MEDIUM",
    "current_savings": "MEDIUM",
    "avg_savings_24m": "MEDIUM",
    "savings_std_24m": "MEDIUM",
    "savings_volatility": "MEDIUM",
    "savings_stability": "MEDIUM",
    "n_past_loans": "LOW",
    "current_loan_request": "MEDIUM",
    "current_loan_duration": "LOW",
    "loan_to_savings_ratio": "MEDIUM",
    "n_loans": "LOW",
    "avg_loan_amount": "MEDIUM",
    "total_loan_amount": "MEDIUM",
    "avg_repayment_regularity": "LOW",
    "min_repayment_regularity": "LOW",
    "max_historical_dpd": "HIGH",
    "mean_historical_dpd": "HIGH",
    "n_defaults": "HIGH",
    "loan_to_income_ratio": "MEDIUM",
    "historical_default_rate": "HIGH",
    "savings_to_income_ratio": "MEDIUM",
    "seniority_years": "LOW",
    "overall_payment_regularity": "LOW",
}

# Features minimales (identite + demande) : toujours dans tout set.
_MINIMAL_FEATURES: List[str] = [
    "age",
    "monthly_income",
    "current_savings",
    "current_loan_request",
    "current_loan_duration",
]

_SOURCE_BY_FEATURE: Dict[str, str] = {
    "age": "APPLICATION",
    "seniority_months": "INTERNAL_SFD",
    "monthly_income": "APPLICATION",
    "current_savings": "SAVINGS",
    "avg_savings_24m": "TRANSACTION",
    "savings_std_24m": "TRANSACTION",
    "savings_volatility": "TRANSACTION",
    "savings_stability": "TRANSACTION",
    "n_past_loans": "INTERNAL_SFD",
    "current_loan_request": "APPLICATION",
    "current_loan_duration": "APPLICATION",
    "loan_to_savings_ratio": "DERIVED",
    "n_loans": "INTERNAL_SFD",
    "avg_loan_amount": "INTERNAL_SFD",
    "total_loan_amount": "INTERNAL_SFD",
    "avg_repayment_regularity": "INTERNAL_SFD",
    "min_repayment_regularity": "INTERNAL_SFD",
    "max_historical_dpd": "BIC",
    "mean_historical_dpd": "BIC",
    "n_defaults": "BIC",
    "loan_to_income_ratio": "DERIVED",
    "historical_default_rate": "BIC",
    "savings_to_income_ratio": "DERIVED",
    "seniority_years": "DERIVED",
    "overall_payment_regularity": "INTERNAL_SFD",
}


def build_feature_definitions() -> List[FeatureDefinition]:
    """Construit la liste des definitions APPROVED pour les 25 features."""
    definitions: List[FeatureDefinition] = []
    for name in FeatureRegistry.all_features():
        definitions.append(
            FeatureDefinition(
                name=name,
                description=FeatureRegistry.formula(name),
                data_type="numeric",
                unit="" if name not in _MINIMAL_FEATURES else "Varies",
                feature_group=_FEATURE_GROUP.get(name, FeatureGroup.ALTERNATIVE),
                source=_SOURCE_BY_FEATURE.get(name, "UNK"),
                formula_reference=f"FeatureRegistry.formula('{name}')",
                availability_rule=_availability_rule(name),
                sensitivity_class=_SENSITIVITY.get(name, "LOW"),
                status=FeatureStatus.APPROVED,
                version="1",
            )
        )
    return definitions


def _availability_rule(name: str) -> str:
    """Regle de disponibilite (champ source presente) pour la feature."""
    source = _SOURCE_BY_FEATURE.get(name, "UNK")
    if source == "DERIVED":
        return f"require input features of '{name}'"
    return f"source '{source}' available"


class FeatureSet(BaseModel):
    """Un set versionne de features (consigne section 15).

    La version fait partie de l'identite : (code, version) est unique. Un set
    versionne ne reference que des features APPROVED.
    """

    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    version: str = "1"
    schema_version: str = "1"
    status: str = "APPROVED"
    features: List[str] = Field(default_factory=list)

    def feature_ids(self) -> List[str]:
        return list(self.features)


class FeatureSetCatalog:
    """Catalogue versionne des sets de features (MINIMAL..FULL_ADMISSIBLE)."""

    _MINIMAL = "MINIMAL"
    _BUSINESS = "BUSINESS"
    _FINANCIAL = "FINANCIAL"
    _CREDIT = "CREDIT"
    _ALTERNATIVE = "ALTERNATIVE"
    _FULL_ADMISSIBLE = "FULL_ADMISSIBLE"

    # Ordre de couverture : inclusif croissant.
    _INCLUDES = {
        _MINIMAL: [],
        _BUSINESS: [_MINIMAL],
        _FINANCIAL: [_MINIMAL, _BUSINESS],
        _CREDIT: [_MINIMAL, _BUSINESS, _FINANCIAL],
        _ALTERNATIVE: [_MINIMAL, _BUSINESS, _FINANCIAL, _CREDIT],
        _FULL_ADMISSIBLE: [_MINIMAL, _BUSINESS, _FINANCIAL, _CREDIT, _ALTERNATIVE],
    }

    # Groupe() -> features groupees (les derives et bases sont regroupés sur
    # la base du FeatureDefinition). On construit les sets par inclusion.
    _GROUPS = {
        FeatureGroup.MINIMAL.value: _MINIMAL_FEATURES,
        FeatureGroup.BUSINESS.value: [
            f for f in FeatureRegistry.all_features()
            if _FEATURE_GROUP.get(f) == FeatureGroup.BUSINESS
        ],
        FeatureGroup.FINANCIAL.value: [
            f for f in FeatureRegistry.all_features()
            if _FEATURE_GROUP.get(f) == FeatureGroup.FINANCIAL
        ],
        FeatureGroup.CREDIT.value: [
            f for f in FeatureRegistry.all_features()
            if _FEATURE_GROUP.get(f) == FeatureGroup.CREDIT
        ],
        FeatureGroup.ALTERNATIVE.value: [
            f for f in FeatureRegistry.all_features()
            if _FEATURE_GROUP.get(f) == FeatureGroup.ALTERNATIVE
        ],
    }

    def __init__(self) -> None:
        self._sets: Dict[str, Dict[str, FeatureSet]] = {}
        self._build_defaults()

    def _build_defaults(self) -> None:
        ordered = [
            self._MINIMAL,
            self._BUSINESS,
            self._FINANCIAL,
            self._CREDIT,
            self._ALTERNATIVE,
            self._FULL_ADMISSIBLE,
        ]
        for code in ordered:
            features = self._collect(code)
            self._sets[code] = {
                "1": FeatureSet(
                    code=code,
                    name=f"Feature set {code} (version 1)",
                    version="1",
                    schema_version="1",
                    status="APPROVED",
                    features=features,
                )
            }

    def _collect(self, code: str) -> List[str]:
        members: List[str] = []
        # Le set FULL_ADMISSIBLE contient toute l'union des groupes.
        if code == self._FULL_ADMISSIBLE:
            union: List[str] = []
            for feats in self._GROUPS.values():
                for f in feats:
                    if f not in union:
                        union.append(f)
            return union
        # Les sets precedents inclus.
        for previous in self._INCLUDES.get(code, []):
            for f in self._collect(previous):
                if f not in members:
                    members.append(f)
        # Le groupe propre a ce code.
        if code in self._GROUPS:
            for f in self._GROUPS[code]:
                if f not in members:
                    members.append(f)
        return members

    def get(self, code: str, version: str = "1") -> Optional[FeatureSet]:
        return self._sets.get(code, {}).get(version)

    def list_codes(self) -> List[str]:
        return list(self._sets.keys())


DEFAULT_CATALOG = FeatureSetCatalog()


def resolve_feature_set(
    information_state: Optional[InformationState],
    catalog: Optional[FeatureSetCatalog] = None,
) -> FeatureSet:
    """Determine le set de features applicable a une candidature.

    Aligne le set sur le profil d'information (etape 8) : un dossier sans
    fichier ou mince n'a pas assez d'historique pour alimenter les features
    credit => set minimal/business ; un dossier complet => FULL_ADMISSIBLE.
    Le choix est deterministe et justifie ; il ne traduit PAS en risque.
    """
    catalog = catalog or DEFAULT_CATALOG
    state = information_state.value if information_state else "UNKNOWN"

    if state in (InformationState.FULL_FILE.value,):
        return catalog.get(FeatureSetCatalog._FULL_ADMISSIBLE, "1")
    if state in (InformationState.THIN_FILE.value,):
        return catalog.get(FeatureSetCatalog._FINANCIAL, "1")
    if state in (InformationState.DATA_POOR.value,):
        return catalog.get(FeatureSetCatalog._BUSINESS, "1")
    # NO_FILE / UNKNOWN : seulement le socle minimal (pas de regle de risque).
    return catalog.get(FeatureSetCatalog._MINIMAL, "1")
