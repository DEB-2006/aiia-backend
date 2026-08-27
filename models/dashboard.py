from pydantic import BaseModel
from typing import Dict

class DashboardKPIs(BaseModel):
    total_patients_enrolled: int
    active_interventions: int
    total_adverse_events: int
    serious_adverse_events: int
    ctri_compliance_rate: float
    dosha_breakdown: Dict[str, int]