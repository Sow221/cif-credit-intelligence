"""Package audit : enregistrement append-only des evenements (P0).

L'audit est separe du fonctionnement metier et n'influence jamais une
decision (consigne section 9, etape 18).
"""

from src.audit.audit_service import AuditEventType, AuditService

__all__ = ["AuditService", "AuditEventType"]
