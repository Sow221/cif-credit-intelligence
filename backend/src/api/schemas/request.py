"""Schemas de requete de l'API (Pydantic v2).

Encodage strict (extra=forbid) et validation des plages metier pour garantir
des entrees fiables avant tout traitement.
"""


from pydantic import BaseModel, ConfigDict, Field


class SavingsEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    month: int = Field(..., ge=1, le=24)
    balance: float = Field(..., ge=0)


class LoanEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    loan_id: int = Field(..., ge=0)
    amount: float = Field(..., gt=0)
    repayment_regularity: float = Field(..., ge=0, le=1)
    max_dpd: int = Field(..., ge=0, le=90)
    status: str = Field(..., pattern="^(completed|defaulted)$")


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: int = Field(..., ge=0)
    age: int = Field(..., ge=18, le=100)
    seniority_months: int = Field(..., ge=0)
    monthly_income: float = Field(..., gt=0)
    current_savings: float = Field(..., ge=0)
    n_past_loans: int = Field(..., ge=0, le=50)
    current_loan_request: float = Field(..., gt=0)
    current_loan_duration: int = Field(..., ge=1, le=60)
    has_history: bool = Field(True, description="False si client Thin-File")
    savings_history: list[SavingsEntry] | None = Field(
        None, description="Obligatoire si has_history=True"
    )
    loan_history: list[LoanEntry] | None = Field(
        None, description="Obligatoire si has_history=True et n_past_loans > 0"
    )
