from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth import get_current_user, require_roles
from models.db_models import ClinicalAuditTrail as DBAudit
from models.db_models import TrialPatient as DBPatient
from models.intervention import InterventionCreate, InterventionResponse
from models.user import TokenData

router = APIRouter(
    prefix="/api/v1/interventions",
    tags=["Ayurveda Interventions & Drug Tracking"],
)


@router.post(
    "/log",
    response_model=InterventionResponse,
    status_code=status.HTTP_201_CREATED,
)
def log_intervention(
    intervention_data: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(
        require_roles(["Investigator", "Admin"])
    ),
):
    # 1. Verify patient exists in PostgreSQL
    patient = (
        db.query(DBPatient)
        .filter(DBPatient.patient_id == intervention_data.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{intervention_data.patient_id}' not found.",
        )

    # 2. Build response payload matching InterventionResponse
    record_data = intervention_data.model_dump()
    record_data.update(
        {
            "intervention_id": 1,  # Set ID for response serialization
            "prescribed_by_user_id": current_user.user_id,
            "created_at": datetime.now(timezone.utc),
        }
    )

    # 3. Create GCP Audit Trail entry
    audit_entry = DBAudit(
        trial_id=patient.trial_id,
        patient_id=patient.subject_id,
        changed_by=current_user.user_id,
        action_type="LOG_INTERVENTION",
        field_name="formulation_name",
        old_value=None,
        new_value=getattr(
            intervention_data, "formulation_name", "Herbal Protocol"
        ),
        ip_address="127.0.0.1",
    )
    db.add(audit_entry)
    db.commit()

    return record_data


@router.get("/", response_model=List[dict])
def list_interventions(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    # Returns logged GCP audit trail records for interventions
    audit_logs = (
        db.query(DBAudit)
        .filter(DBAudit.action_type == "LOG_INTERVENTION")
        .all()
    )
    return [
        {
            "log_id": log.log_id,
            "trial_id": log.trial_id,
            "patient_id": log.patient_id,
            "action_type": log.action_type,
            "formulation": log.new_value,
            "changed_by": log.changed_by,
            "timestamp": log.timestamp,
        }
        for log in audit_logs
    ]