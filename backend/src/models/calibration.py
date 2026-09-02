"""Calibration (P0, etape 12).

Recalibre la probabilite de defaut brute (pd_raw) en probabilite calibree
(pd_calibrated). La methode utilisee en production (PLATT ou ISOTONIC) est
ENREGISTREE et VERSIONNEE, jamais hardcodee : on conserve separement
pd_raw, pd_calibrated et calibration_version (consigne section 22).

La calibration ne change pas la nature d'une prediction : elle ajuste le
niveau de probabilite pour le rendre fiable en niveau. Le choix final de la
methode est valide par l'experimentation ; cette interface permet de
versionner sans coder en dur.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

import numpy as np


class CalibrationMethod(str, Enum):
    PLATT = "PLATT"
    ISOTONIC = "ISOTONIC"


@dataclass
class CalibrationResult:
    """Resultat d'une calibration (pd preserves separement)."""

    pd_raw: float
    pd_calibrated: float
    calibration_version: str
    method: CalibrationMethod


@dataclass
class CalibrationConfig:
    """Parametres VERSIONNES de la calibration (valides par experimentation)."""

    version: str = "1"
    method: CalibrationMethod = CalibrationMethod.PLATT
    # PLATT : parametres sigmoide (a, b) obtenus par regression logistique.
    platt_a: float = 1.0
    platt_b: float = 0.0
    # ISOTONIC : mappe (bin -> pd_calibrated) ; une prediction en dehors des
    # bins est bornee par les extrema.
    isotropic_bins: List[float] = field(default_factory=list)
    isotropic_targets: List[float] = field(default_factory=list)


class Calibrator:
    """Calibrateur pur : pd_raw -> pd_calibrated selon une config versionnee."""

    def __init__(self, config: CalibrationConfig) -> None:
        self._config = config

    def calibrate(self, pd_raw: float) -> float:
        pd_raw = float(np.clip(pd_raw, 0.0, 1.0))
        if self._config.method == CalibrationMethod.PLATT:
            calibrated = self._platt(pd_raw)
        elif self._config.method == CalibrationMethod.ISOTONIC:
            calibrated = self._isotonic(pd_raw)
        else:  # pragma: no cover - methode ajoutee plus tard
            raise ValueError(f"Methode de calibration inconnue: {self._config.method}")
        return float(np.clip(calibrated, 0.0, 1.0))

    def result(self, pd_raw: float) -> CalibrationResult:
        return CalibrationResult(
            pd_raw=float(pd_raw),
            pd_calibrated=self.calibrate(pd_raw),
            calibration_version=self._config.version,
            method=self._config.method,
        )

    def _platt(self, pd_raw: float) -> float:
        # conversion vers v = logit(pd_raw) puis sigmoide parametree (a,b).
        eps = 1e-9
        logit = np.log(max(pd_raw, eps) / max(1.0 - pd_raw, eps))
        z = self._config.platt_a * logit + self._config.platt_b
        return float(1.0 / (1.0 + np.exp(-z)))

    def _isotonic(self, pd_raw: float) -> float:
        if not self._config.isotropic_bins or not self._config.isotropic_targets:
            # pas de mappe : isotonie = identite (mais methode enregistree).
            return float(pd_raw)
        bins = np.asarray(self._config.isotropic_bins, dtype=float)
        targets = np.asarray(self._config.isotropic_targets, dtype=float)
        value = float(np.interp(pd_raw, bins, targets))
        return value


DEFAULT_CALIBRATION_CONFIG = CalibrationConfig()


# ---------------------------------------------------------------------------
# Hypotheses PAR DEFAULT (config versionnee "0") : la methode n'est pas decidee.
# On conserve une calibration "no-op" documentee jusqu'a l'experimentation.
# ---------------------------------------------------------------------------

NOOP_CALIBRATION_CONFIG = CalibrationConfig(version="0", platt_b=0.0)
