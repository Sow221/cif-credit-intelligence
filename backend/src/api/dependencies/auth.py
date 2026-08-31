"""Dependance d'authentification (P0, etape 19).

Decode le JWT, construit le contexte utilisateur (identite + role +
institution) et refuse les requetes non authentifiees. Le multi-tenancy est
applique au backend : l'institution provient du token, jamais du corps.
"""

from typing import Optional

from fastapi import Header, HTTPException

from src.api.middleware.auth import decode_token
from src.core.security import Role


class CurrentUser:
    """Contexte de l'utilisateur authentifie."""

    def __init__(
        self,
        *,
        subject: str,
        role: Optional[Role],
        institution_id: Optional[str],
    ) -> None:
        self.subject = subject
        self.role = role
        self.institution_id = institution_id

    @classmethod
    def from_token(cls, payload: dict) -> "CurrentUser":
        subject = payload.get("sub")
        role_raw = payload.get("role")
        role = None
        if role_raw is not None:
            try:
                role = Role(role_raw)
            except ValueError:
                role = None
        return cls(
            subject=str(subject) if subject else "",
            role=role,
            institution_id=payload.get("institution_id"),
        )


def decode_user_from_token(
    authorization: Optional[str] = Header(default=None),
) -> CurrentUser:
    """Decode le Bearer token et retourne le contexte utilisateur."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Jeton d'acces manquant")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Jeton d'acces invalide")
    try:
        payload = decode_token(token)
    except Exception as exc:  # PyJWTError
        raise HTTPException(status_code=401, detail="Jeton expiré ou invalide") from exc
    return CurrentUser.from_token(payload)


def get_current_user(
    authorization: Optional[str] = Header(default=None),
) -> CurrentUser:
    """Dependance FastAPI fournissant l'utilisateur courant."""
    return decode_user_from_token(authorization)
