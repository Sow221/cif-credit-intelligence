"""Service de journalisation d'audit.

Enregistre chaque appel de prediction (donnees d'entree, PD, decision,
request_id) pour la tracabilite et la conformite reglementaire.
La sortie est structuree en JSON pour une ingestion facile dans un
collecteur de logs / base d'audit.
"""

import json
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Journalise les evenements metier et d'acces de l'API."""

    @staticmethod
    def _record(event: str, **payload) -> None:
        record = {"event": event, **payload}
        logger.info(json.dumps(record, ensure_ascii=False, default=str))

    def log_prediction(
        self,
        request_id: str,
        customer_id: int,
        pd_score,
        decision: str,
        confidence_level: str,
        is_thin_file: bool,
        model_version=None,
    ) -> None:
        """Trace un appel de prediction avec sa decision."""
        self._record(
            "prediction",
            request_id=request_id,
            customer_id=customer_id,
            pd_score=pd_score,
            decision=decision,
            confidence_level=confidence_level,
            is_thin_file=is_thin_file,
            model_version=model_version,
        )

    def log_access(
        self, request_id: str, path: str, method: str, status_code: int
    ) -> None:
        """Trace un acces a une route de l'API."""
        self._record(
            "access",
            request_id=request_id,
            path=path,
            method=method,
            status_code=status_code,
        )
