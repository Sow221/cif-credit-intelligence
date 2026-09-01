"""Information profiler (P0, etape 8).

Le profiler est un composant PUR (dans `features/`) : il ne prend aucune
decision de credit. Il analyse la quantite et la qualite de l'information
disponible pour une candidature et produit un profil d'information :

    credit_depth, financial_depth, business_depth, relationship_depth,
    data_quality        -> NONE / LOW / MEDIUM / HIGH
    information_state   -> NO_FILE / THIN_FILE / FULL_FILE / DATA_POOR / UNKNOWN
    applicant_status    -> NEW_TO_INSTITUTION / NEW_TO_CREDIT / EXISTING / UNKNOWN

Contraintes (consigne section 12-14) :
  - Pas de regle arbitraire du type "previous_loans < 2 => THIN_FILE".
  - Les seuils sont CONFIGURABLES et VERSIONNES (valides par l'etude
    experimentale), jamais codes en dur.
  - Ne pas confondre NEW_TO_INSTITUTION, NEW_TO_CREDIT, NO_FILE, THIN_FILE,
    DATA_POOR. Un nouveau client n'est pas automatiquement un no-file ; un
    thin-file n'est pas automatiquement un risque eleve (le risque est traite
    ailleurs).
"""

import uuid
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.core.exceptions import NotFoundError
from src.repositories.application_data_repository import ApplicationDataRepository
from src.repositories.application_repository import ApplicationRepository
from src.repositories.information_profile_repository import InformationProfileRepository


class InformationDepth(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InformationState(str, Enum):
    NO_FILE = "NO_FILE"
    THIN_FILE = "THIN_FILE"
    FULL_FILE = "FULL_FILE"
    DATA_POOR = "DATA_POOR"
    UNKNOWN = "UNKNOWN"


class ApplicantStatus(str, Enum):
    NEW_TO_INSTITUTION = "NEW_TO_INSTITUTION"
    NEW_TO_CREDIT = "NEW_TO_CREDIT"
    EXISTING = "EXISTING"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Entree : resume structure de l'information disponible
# ---------------------------------------------------------------------------


class InformationInput(BaseModel):
    """Ce que le profiler sait sur l'information d'une candidature.

    Chaque champ est un compteur/nombre de marqueurs d'information disponibles.
    Les seuils qui transforment ces compteurs en niveaux sont dans la config.
    """

    model_config = ConfigDict(extra="forbid")

    # Nombre de champs financiaƼrs / de sources financieres distinctes.
    financial_sources: int = 0
    # Nombre de champs de business (activite) disponibles.
    business_fields: int = 0
    # Nombre de marqueurs de relation avec l'institution.
    relationship_markers: int = 0
    # Nombre de marqueurs d'historique de credit (factures, lignes, etc.).
    credit_markers: int = 0
    # Indique si des donnees sont posees pour ce dossier.
    has_data: bool = False
    # Indique si le demandeur a deja un historique institutionnel (applications
    # precedentes, comptes, etc.). Un nouveau client n'est pas un no-file.
    new_to_institution: bool = True
    # Indique si le demandeur a un historique de credit hors institution.
    new_to_credit: bool = True

    # Resultat de qualite des donnees (optionnel, sinon derive).
    data_quality: Optional[str] = None


class InformationProfileConfig(BaseModel):
    """Seuils CONFIGURABLES et VERSIONNES pour le profilage.

    Chaque dimension mappe un compteur vers NONE/LOW/MEDIUM/HIGH via les
    bornes [none_lt, low_lt, medium_lt, high_lt]. La definition finale sera
    validee par l'etude experimentale ; cette classe permet de versionner.
    """

    model_config = ConfigDict(extra="forbid")

    version: str = "1.0"

    # Bornes des profondeurs : nombre de marqueurs.
    credit: tuple = Field(default=(1, 2, 3, 9999), description="(none_lt, low_lt, medium_lt, high_lt)")
    financial: tuple = Field(default=(1, 2, 3, 9999))
    business: tuple = Field(default=(1, 2, 3, 9999))
    relationship: tuple = Field(default=(1, 2, 3, 9999))

    # Regles de l'etat d'information.
    thin_credit_threshold: int = Field(default=2, description="Nb de marqueurs credit pour FULL_FILE")
    credit_markers_for_file: int = Field(default=1, description="Marqueurs credit minimum pour un fichier")
    data_poor_quality_scale: float = Field(default=0.5, ge=0, le=1)


DEFAULT_PROFILE_CONFIG = InformationProfileConfig()


# ---------------------------------------------------------------------------
# Profil calcule
# ---------------------------------------------------------------------------


class InformationProfileResult(BaseModel):
    """Profil d'information produit par le profiler."""

    model_config = ConfigDict(extra="forbid")

    applicant_status: ApplicantStatus
    credit_depth: InformationDepth
    financial_depth: InformationDepth
    business_depth: InformationDepth
    relationship_depth: InformationDepth
    data_quality_value: InformationDepth
    information_state: InformationState
    profile_version: str


class InformationProfiler:
    """Calcule le profil d'information a partir d'un resume structure."""

    def __init__(self, config: Optional[InformationProfileConfig] = None) -> None:
        self._config = config or DEFAULT_PROFILE_CONFIG

    def profile(self, data: InformationInput) -> InformationProfileResult:
        credit = self._to_depth(data.credit_markers, self._config.credit)
        financial = self._to_depth(data.financial_sources, self._config.financial)
        business = self._to_depth(data.business_fields, self._config.business)
        relationship = self._to_depth(data.relationship_markers, self._config.relationship)
        quality = self._quality_depth(data)

        applicant_status = self._applicant_status(data)
        info_state = self._information_state(data, credit, quality)

        return InformationProfileResult(
            applicant_status=applicant_status,
            credit_depth=credit,
            financial_depth=financial,
            business_depth=business,
            relationship_depth=relationship,
            data_quality_value=quality,
            information_state=info_state,
            profile_version=self._config.version,
        )

    # --------------------------------------------------------------- interne --

    def _to_depth(self, count: int, bounds: tuple) -> InformationDepth:
        none_lt, low_lt, medium_lt, high_lt = bounds
        if count < none_lt or count <= 0:
            return InformationDepth.NONE
        if count < low_lt:
            return InformationDepth.LOW
        if count < medium_lt:
            return InformationDepth.MEDIUM
        if count < high_lt:
            return InformationDepth.HIGH
        return InformationDepth.HIGH

    def _quality_depth(self, data: InformationInput) -> InformationDepth:
        # Un champ de qualite est fourni (ex: data_quality checker) sinon par defaut.
        if data.data_quality is not None:
            value = data.data_quality.upper()
            if value in ("HIGH", "GOOD", "EXCELLENT"):
                return InformationDepth.HIGH
            if value in ("MEDIUM", "FAIR"):
                return InformationDepth.MEDIUM
            if value in ("LOW", "POOR"):
                return InformationDepth.LOW
            return InformationDepth.NONE
        # Si on a des donnees, on considere une qualite moyenne par defaut.
        if data.has_data:
            return InformationDepth.MEDIUM
        return InformationDepth.NONE

    def _applicant_status(self, data: InformationInput) -> ApplicantStatus:
        if not data.new_to_institution and not data.new_to_credit:
            return ApplicantStatus.EXISTING
        if not data.new_to_credit:
            # A deja un historique de credit hors institution, nouveau a l'institution.
            return ApplicantStatus.NEW_TO_INSTITUTION
        if not data.new_to_institution:
            # Deja client de l'institution mais nouveau au credit.
            return ApplicantStatus.NEW_TO_CREDIT
        return ApplicantStatus.UNKNOWN

    def _information_state(
        self, data: InformationInput, credit: InformationDepth, quality: InformationDepth
    ) -> InformationState:
        # Aucune donnee -> pas de fichier, mais on precise le statut demandeur.
        if not data.has_data:
            return InformationState.UNKNOWN if data.new_to_institution else InformationState.NO_FILE
        # Pas de marqueurs credit -> NO_FILE (pas de fichier de credit).
        if credit == InformationDepth.NONE:
            return InformationState.NO_FILE
        # Fichier plein : assez de marqueurs et qualite suffisante.
        if (
            credit in (InformationDepth.MEDIUM, InformationDepth.HIGH)
            and quality in (InformationDepth.MEDIUM, InformationDepth.HIGH)
        ):
            return InformationState.FULL_FILE
        # Fichier mince : peu de marqueurs de credit.
        if credit in (InformationDepth.LOW, InformationDepth.MEDIUM):
            return InformationState.THIN_FILE
        # Donnees presentes mais pauvres.
        if quality in (InformationDepth.LOW, InformationDepth.NONE):
            return InformationState.DATA_POOR
        return InformationState.UNKNOWN


# Classification des types de source (consigne section 10) vers les dimensions
# du profil. Le code metier ne depend d'aucun fournisseur particulier.
_FINANCIAL_SOURCE_TYPES = {"INTERNAL_SFD", "SAVINGS", "TRANSACTION", "BANK", "PAY"}
_BUSINESS_SOURCE_TYPES = {"BUSINESS"}
_RELATIONSHIP_SOURCE_TYPES = {"INTERNAL_SFD", "RELATION"}
# Toute source de credit / dette contribue a la profondeur crediit.
_CREDIT_SOURCE_TYPES = {
    "INTERNAL_SFD",
    "BIC",
    "SAVINGS",
    "TRANSACTION",
    "BUSINESS",
    "ALTERNATIVE",
    "PUBLIC",
    "BANK",
    "PAY",
    "EMP",
}


class InformationProfilerService:
    """Orchestre la collecte, le calcul et la persistance d'un profil.

    Le calcul est delegue au `InformationProfiler` pur ; ce service ne fait que
    reunir les donnees applicatives, construire l'input et persister le resultat
    (meme pattern que DataIntakeService).
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        self._data_repo = ApplicationDataRepository(db)
        self._profile_repo = InformationProfileRepository(db)
        self._apps = ApplicationRepository(db)
        self._audit = AuditService(db)
        self._profiler = InformationProfiler()

    def build_profile(
        self,
        *,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> InformationProfileResult:
        application = self._apps.get(application_id, institution_id)
        if application is None:
            raise NotFoundError(f"Application {application_id} introuvable")

        entries = self._data_repo.list_for_application(application_id, institution_id)
        sources = {
            str(s.source_id): s for s in self._data_repo.list_active_sources()
        }

        financial = business = relationship = credit = 0
        for entry in entries:
            if entry.source_id is None:
                continue
            source = sources.get(str(entry.source_id))
            if source is None:
                continue
            stype = (source.type or "").upper()
            if stype in _FINANCIAL_SOURCE_TYPES:
                financial += 1
            if stype in _BUSINESS_SOURCE_TYPES:
                business += 1
            if stype in _RELATIONSHIP_SOURCE_TYPES:
                relationship += 1
            if stype in _CREDIT_SOURCE_TYPES:
                credit += 1

        # Deja une autre application pour ce client -> existant a l'institution.
        other_apps = [
            a for a in self._apps.list(institution_id) if a.client_id == application.client_id
        ]
        new_to_institution = len(other_apps) <= 1

        # new_to_credit : par defaut on le derive du fait qu'aucune source de
        # credit n'a fourni de marqueurs.
        new_to_credit = credit == 0

        data_input = InformationInput(
            financial_sources=financial,
            business_fields=business,
            relationship_markers=relationship,
            credit_markers=credit,
            has_data=len(entries) > 0,
            new_to_institution=new_to_institution,
            new_to_credit=new_to_credit,
        )
        result = self._profiler.profile(data_input)

        self._profile_repo.create(
            application_id=application_id,
            applicant_status=result.applicant_status.value,
            credit_depth=result.credit_depth.value,
            financial_depth=result.financial_depth.value,
            business_depth=result.business_depth.value,
            relationship_depth=result.relationship_depth.value,
            data_quality=result.data_quality_value.value,
            information_state=result.information_state.value,
            profile_version=result.profile_version,
            details_json=data_input.model_dump(),
        )
        self._db.flush()
        self._audit.log(
            AuditEventType.PROFILE_CREATED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="application",
            entity_id=str(application_id),
            request_id=request_id,
            details={
                "information_state": result.information_state.value,
                "credit_depth": result.credit_depth.value,
                "profile_version": result.profile_version,
            },
        )
        self._db.commit()
        return result
