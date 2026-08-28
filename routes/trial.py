from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.db_models import ClinicalTrial as DBTrial
from models.user import TokenData
from middleware.auth import require_roles

router = APIRouter(prefix="/api/v1/trials", tags=["Clinical Trial Management"])

@router.post("/", status_code=status.HTTP_201_CREATED)
@router.post("", status_code=status.HTTP_201_CREATED)
def create_trial(
    trial_data: dict,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["Admin", "Investigator", "Sponsor"]))
):
    existing_trial = db.query(DBTrial).filter(
        DBTrial.ctri_registration_number == trial_data.get("ctri_registration_number")
    ).first()
    
    if existing_trial:
        raise HTTPException(status_code=400, detail="Trial with this CTRI number already exists")

    new_trial = DBTrial(
        ctri_registration_number=trial_data.get("ctri_registration_number"),
        trial_title=trial_data.get("trial_title"),
        phase=trial_data.get("phase"),
        sponsor_name=trial_data.get("sponsor_name", "AIIA"),
        status=trial_data.get("status", "On-Going"),
        start_date=trial_data.get("start_date")
    )
    db.add(new_trial)
    db.commit()
    db.refresh(new_trial)

    # Safely convert to dictionary response
    return {
        "id": new_trial.id,
        "ctri_registration_number": new_trial.ctri_registration_number,
        "trial_title": new_trial.trial_title,
        "phase": new_trial.phase,
        "sponsor_name": new_trial.sponsor_name,
        "status": new_trial.status,
        "start_date": str(new_trial.start_date) if new_trial.start_date else None
    }

@router.get("/", response_model=List[dict])
@router.get("", response_model=List[dict])
def list_trials(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["Admin", "Investigator", "Sponsor", "Auditor", "Ethics_Committee"]))
):
    trials = db.query(DBTrial).all()
    
    # Safely convert every database model object into a serializable dictionary
    result = []
    for t in trials:
        result.append({
            "id": getattr(t, "id", None),
            "ctri_registration_number": getattr(t, "ctri_registration_number", ""),
            "trial_title": getattr(t, "trial_title", ""),
            "phase": getattr(t, "phase", ""),
            "sponsor_name": getattr(t, "sponsor_name", ""),
            "status": getattr(t, "status", ""),
            "start_date": str(t.start_date) if getattr(t, "start_date", None) else None
        })
    return result