from __future__ import annotations

import uuid

from fastapi import Depends

from src.api.dependencies.auth import get_current_user
from src.models.database import User


async def get_current_institution(user: User = Depends(get_current_user)) -> uuid.UUID:
    return user.institution_id
