from datetime import date, datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth import get_current_user, require_roles
from models.db_models import ClinicalAuditTrail as DBAudit
from models.db_models import ClinicalTrial as DBTrial
from models.db_models import TrialPatient as DBPatient
from models.patient import FHIRObservation, PatientRegister, PatientResponse
from models.user import TokenData

router = APIRouter(
    prefix="/api/v1/patients", tags=["Patient Management & CDISC/FHIR"]
)


@router.post("/enroll", status_code=status.HTTP_201_CREATED)
def enroll_patient(
    patient_data: PatientRegister,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(
        require_roles(["Investigator", "Admin"])
    ),
):
    # 1. Fetch target trial using ctri_number
    trial = (
        db.query(DBTrial)
        .filter(
            DBTrial.ctri_registration_number == patient_data.ctri_number
        )
        .first()
    )

    if not trial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trial with CTRI number '{patient_data.ctri_number}' not found.",
        )

    # 2. Convert Pydantic datetime to Python date object
    enrollment_date_val = (
        patient_data.consent_date.date()
        if patient_data.consent_date
        else date.today()
    )

    # 3. Insert patient record with explicit enrollment_date
    new_patient = DBPatient(
        trial_id=trial.trial_id,
        subject_id=patient_data.subject_identifier,
        enrollment_date=enrollment_date_val,
        status="Active",
    )
    db.add(new_patient)
    db.flush()  # Generates patient_id before commit

    # 4. Create GCP audit trail entry
    audit_entry = DBAudit(
        trial_id=trial.trial_id,
        patient_id=new_patient.subject_id,
        changed_by=current_user.user_id,
        action_type="ENROLL_PATIENT",
        field_name="subject_id",
        old_value=None,
        new_value=new_patient.subject_id,
        ip_address="127.0.0.1",
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(new_patient)

    return {
        "message": "Patient enrolled successfully",
        "patient_id": new_patient.patient_id,
        "subject_id": new_patient.subject_id,
        "enrollment_date": str(new_patient.enrollment_date),
    }


@router.get("/", response_model=List[dict])
@router.get("", response_model=List[dict])
def list_patients(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    patients = db.query(DBPatient).all()
    
    result = []
    for p in patients:
        enrollment_date_str = None
        if hasattr(p, "enrollment_date") and p.enrollment_date:
            enrollment_date_str = str(p.enrollment_date)

        result.append({
            "id": getattr(p, "patient_id", None) or getattr(p, "id", None),
            "patient_id": getattr(p, "patient_id", None),
            "subject_id": getattr(p, "subject_id", ""),
            "name": getattr(p, "subject_id", "") or f"Patient #{getattr(p, 'patient_id', '')}",
            "trial_id": getattr(p, "trial_id", None),
            "enrollment_date": enrollment_date_str,
            "status": getattr(p, "status", "Active"),
        })
    return result


@router.post("/fhir/observation", status_code=status.HTTP_201_CREATED)
def record_fhir_observation(
    observation: FHIRObservation,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(
        require_roles(["Investigator", "Admin"])
    ),
):
    patient = (
        db.query(DBPatient)
        .filter(DBPatient.patient_id == observation.patient_id)
        .first()
    )
    if not patient:
        raise HTTPException(
            status_code=404, detail="Patient record not found."
        )

    obs_record = observation.model_dump()
    return {
        "message": "CDISC/FHIR Observation logged successfully",
        "data": obs_record,
    }