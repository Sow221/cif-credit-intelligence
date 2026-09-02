"""Uncertainty engine (P0, etape 13).

Interface INDEPENDANTE de la methode finale d'incertitude. Produit :
{ level, score, method, version, factors }.

INTERDICTION (consigne section 23) : l'incertitude ne doit jamais etre calculee
comme `confidence = 1 - pd`. L'incertitude doit provenir d'une methode
explicitement definie et evaluee. La methode par defaut ('EVIDENCE_BASED')
estime l'incertitude a partir de la DISPERSION entre hypotheses de scoring et
de la qualite/quantite d'information disponible (via le profiler). Elle ne
derive pas d'un complement a 1 de la probabilite.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class UncertaintyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


@dataclass
class UncertaintyResult:
    """Resultat d'une evaluation d'incertitude."""

    level: UncertaintyLevel
    score: float
    method: str
    version: str
    factors: List[str] = field(default_factory=list)


@dataclass
class UncertaintyConfig:
    """Config versionnee de la methode d'incertitude (validee par experimentation)."""

    version: str = "1"
    method: str = "EVIDENCE_BASED"
    # Bornes du score d'incertitude.
    high_threshold: float = 0.60
    medium_threshold: float = 0.35


class UncertaintyEngine:
    """Estime l'incertitude par une methode definie et configurable."""

    def __init__(self, config: Optional[UncertaintyConfig] = None) -> None:
        self._config = config or UncertaintyConfig()

    def assess(
        self,
        *,
        pd_raw: float,
        information_state: Optional[str] = None,
        data_quality: Optional[str] = None,
        evidence_spread: Optional[float] = None,
    ) -> UncertaintyResult:
        """Calcule le niveau d'incertitude.

        La methode 'EVIDENCE_BASED' combine :
          - la dispersion entre hypotheses de scoring (evidence_spread, 0..1) ;
          - la pauvrete de l'information (information_state / data_quality).

        Jamais de `1 - pd`.
        """
        if self._config.method == "EVIDENCE_BASED":
            return self._evidence_based(
                pd_raw=pd_raw,
                information_state=information_state,
                data_quality=data_quality,
                evidence_spread=evidence_spread,
            )
        raise ValueError(f"Methode d'incertitude inconnue: {self._config.method}")

    # ------------------------------------------------------------------- interne

    def _evidence_based(
        self,
        *,
        pd_raw: float,
        information_state: Optional[str],
        data_quality: Optional[str],
        evidence_spread: Optional[float],
    ) -> UncertaintyResult:
        factors: List[str] = []

        # 1) Dispersion des scoring (evidence_spread) : principal contributeur.
        spread = 0.0 if evidence_spread is None else float(evidence_spread)
        if evidence_spread is not None:
            factors.append(f"spread={spread:.2f}")

        # 2) Pauvrete informationnelle (fichier mince / pas de donnees).
        info_penalty = 0.0
        if information_state:
            upper = information_state.upper()
            if upper in ("NO_FILE", "UNKNOWN"):
                info_penalty = 0.30
                factors.append(f"information_state={upper}")
            elif upper in ("THIN_FILE", "DATA_POOR"):
                info_penalty = 0.15
                factors.append(f"information_state={upper}")

        # 3) Qualite des donnees.
        quality_penalty = 0.0
        if data_quality:
            q = data_quality.upper()
            if q in ("LOW", "NONE", "UNKNOWN"):
                quality_penalty = 0.15
                factors.append(f"data_quality={q}")

        score = float(min(1.0, spread + info_penalty + quality_penalty))
        level = self._level_for(score)
        if not factors:
            factors.append("no_evidence_penalty")
        return UncertaintyResult(
            level=level,
            score=score,
            method=self._config.method,
            version=self._config.version,
            factors=factors,
        )

    def _level_for(self, score: float) -> UncertaintyLevel:
        if score >= self._config.high_threshold:
            return UncertaintyLevel.HIGH
        if score >= self._config.medium_threshold:
            return UncertaintyLevel.MEDIUM
        return UncertaintyLevel.LOW