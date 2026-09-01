"""Routes API du profil d'information (P0, etape 8).

Produit le profil d'information d'une candidature : profondeur par dimension,
etat d'information et statut demandeur. Multi-tenancy impose cote backend.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.dependencies import CurrentUser, require_permission
from src.core.security import Permission
from src.db.session import get_db
from src.features.information_profiler import InformationProfileResult, InformationProfilerService
from src.schemas.information_profile import InformationProfileResponse

router = APIRouter(prefix="/v1/applications", tags=["information-profile"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/{application_id}/profile", response_model=InformationProfileResult)
def build_information_profile(
    application_id: uuid.UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> InformationProfileResult:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = InformationProfilerService(db)
    return service.build_profile(
        application_id=application_id,
        institution_id=uuid.UUID(current_user.institution_id),
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )
