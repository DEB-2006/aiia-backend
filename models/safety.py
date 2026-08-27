from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime, timezone

class AESeverity(str, Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"

class CausalityAssessment(str, Enum):
    CERTAIN = "Certain"
    PROBABLE = "Probable"
    POSSIBLE = "Possible"
    UNLIKELY = "Unlikely"
    UNRELATED = "Unrelated"

class AdverseEventCreate(BaseModel):
    patient_id: int
    event_term: str = Field(..., example="Nausea after Kashaya administration")
    onset_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: AESeverity = AESeverity.MILD
    is_serious: bool = Field(default=False, description="Flag for Serious Adverse Event (SAE)")
    causality: CausalityAssessment = CausalityAssessment.POSSIBLE
    action_taken: str = Field(..., example="Dose reduced by 50%")
    ctri_reported: bool = Field(default=False)

class AdverseEventResponse(AdverseEventCreate):
    ae_id: int
    reported_by_user_id: int
    reported_at: datetime

    class Config:
        from_attributes = True