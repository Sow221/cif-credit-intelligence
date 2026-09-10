from __future__ import annotations

import uuid

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.exceptions import AuthenticationRequiredError
from src.core.security import decode_access_token
from src.models.database import User


async def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise AuthenticationRequiredError()
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise AuthenticationRequiredError()
    try:
        user_id = uuid.UUID(str(payload["sub"]))
    except (ValueError, TypeError, AttributeError):
        raise AuthenticationRequiredError() from None
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.is_active:
        raise AuthenticationRequiredError()
    return user
