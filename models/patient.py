from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ConsentStatus(str, Enum):
    PENDING = "Pending"
    OBTAINED = "Obtained"
    WITHDRAWN = "Withdrawn"


class DoshaType(str, Enum):
    VATA = "Vata"
    PITTA = "Pitta"
    KAPHA = "Kapha"
    VATA_PITTA = "Vata-Pitta"
    PITTA_KAPHA = "Pitta-Kapha"
    VATA_KAPHA = "Vata-Kapha"
    TRIDOSHA = "Tridosha"


class PatientRegister(BaseModel):
    subject_identifier: str = Field(..., example="AIIA-CT-2026-001")
    age: int = Field(..., ge=18, le=100)
    gender: str = Field(..., example="Female")
    prakriti_baseline: DoshaType
    ctri_number: str = Field(..., example="CTRI/2026/08/045123")
    consent_status: ConsentStatus = ConsentStatus.OBTAINED
    consent_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class PatientResponse(PatientRegister):
    patient_id: int
    enrolled_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FHIRObservation(BaseModel):
    patient_id: int
    resourceType: str = "Observation"
    status: str = "final"
    code_coding_code: str = Field(
        ..., example="8480-6", description="LOINC code for Blood Pressure"
    )
    code_coding_display: str = Field(..., example="Systolic Blood Pressure")
    value_quantity_value: float = Field(..., example=120.0)
    value_quantity_unit: str = Field(..., example="mmHg")
    issued: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )