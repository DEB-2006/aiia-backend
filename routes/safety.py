from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth import get_current_user, require_roles
from models.db_models import ClinicalAuditTrail as DBAudit
from models.db_models import TrialPatient as DBPatient
from models.safety import AdverseEventCreate, AdverseEventResponse
from models.user import TokenData

router = APIRouter(
    prefix="/api/v1/safety",
    tags=["Pharmacovigilance & AE/SAE Safety Engine"],
)


@router.post(
    "/adverse-event",
    response_model=AdverseEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def report_adverse_event(
    ae_data: AdverseEventCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(
        require_roles(["Investigator", "Admin"])
    ),
):
    # 1. Verify patient exists in PostgreSQL
    patient = (
        db.query(DBPatient)
        .filter(DBPatient.patient_id == ae_data.patient_id)
        .first()
    )
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{ae_data.patient_id}' not found.",
        )

    # 2. Build response payload matching AdverseEventResponse
    record_data = ae_data.model_dump()
    record_data.update(
        {
            "ae_id": 1,
            "reported_by_user_id": current_user.user_id,
            "reported_at": datetime.now(timezone.utc),
        }
    )

    # 3. Log GCP audit trail for Adverse Event / Serious Adverse Event reporting
    action_type = (
        "REPORT_SERIOUS_ADVERSE_EVENT"
        if ae_data.is_serious
        else "REPORT_ADVERSE_EVENT"
    )
    audit_entry = DBAudit(
        trial_id=patient.trial_id,
        patient_id=patient.subject_id,
        changed_by=current_user.user_id,
        action_type=action_type,
        field_name="event_term",
        old_value=None,
        new_value=ae_data.event_term,
        ip_address="127.0.0.1",
    )
    db.add(audit_entry)
    db.commit()

    return record_data


@router.get("/adverse-events", response_model=List[dict])
def list_adverse_events(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    # Fetch AE/SAE safety audit logs from PostgreSQL
    ae_logs = (
        db.query(DBAudit)
        .filter(
            DBAudit.action_type.in_(
                ["REPORT_ADVERSE_EVENT", "REPORT_SERIOUS_ADVERSE_EVENT"]
            )
        )
        .all()
    )
    return [
        {
            "log_id": log.log_id,
            "trial_id": log.trial_id,
            "patient_id": log.patient_id,
            "severity_type": log.action_type,
            "event_term": log.new_value,
            "reported_by": log.changed_by,
            "timestamp": log.timestamp,
        }
        for log in ae_logs
    ]