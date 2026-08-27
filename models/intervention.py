from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime, timezone

class DosageForm(str, Enum):
    KASHAYA = "Kashaya (Decoction)"
    CHOORNA = "Choorna (Powder)"
    VATI = "Vati (Tablet/Pill)"
    BHASMA = "Bhasma (Calx)"
    GHRITA = "Ghrita (Medicated Ghee)"
    TAILA = "Taila (Medicated Oil)"

class InterventionCreate(BaseModel):
    patient_id: int
    formulation_name: str = Field(..., example="Ashwagandha Choorna")
    dosage_form: DosageForm = DosageForm.CHOORNA
    dose_quantity: str = Field(..., example="3 grams")
    frequency: str = Field(..., example="Twice daily after meals")
    anupana: str = Field(..., example="Warm Milk / Luke-warm Water")
    batch_number: str = Field(..., example="AY-2026-B882")
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_days: int = Field(..., ge=1, le=365)
    compliance_percentage: float = Field(default=100.0, ge=0.0, le=100.0)

class InterventionResponse(InterventionCreate):
    intervention_id: int
    prescribed_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True