from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.dashboard import DashboardKPIs
from models.db_models import TrialPatient, ClinicalTrial, ClinicalAuditTrail
from middleware.auth import get_current_user
from models.user import TokenData

router = APIRouter(prefix="/api/v1/dashboard", tags=["Executive Dashboard & KPIs"])

@router.get("/kpis", response_model=DashboardKPIs)
@router.get("/kpis/", response_model=DashboardKPIs)
def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    # 1. Fetch patients from PostgreSQL
    patients = db.query(TrialPatient).all()
    total_patients = len(patients)

    # Dosha distribution (Defaulting for database records)
    dosha_counts = {}
    for p in patients:
        # Fallback to 'Vata' if not stored in db model core
        d_type = getattr(p, "prakriti_baseline", None) or "Vata"
        dosha_counts[d_type] = dosha_counts.get(d_type, 0) + 1

    # 2. Active trials and safety counts from PostgreSQL (matching both 'Active' & 'On-Going')
    active_trials = db.query(ClinicalTrial).filter(
        ClinicalTrial.status.in_(["Active", "On-Going"])
    ).count()
    
    ae_count = db.query(ClinicalAuditTrail).filter(
        ClinicalAuditTrail.action_type == "REPORT_ADVERSE_EVENT"
    ).count()
    sae_count = db.query(ClinicalAuditTrail).filter(
        ClinicalAuditTrail.action_type == "REPORT_SERIOUS_ADVERSE_EVENT"
    ).count()

    # 3. CTRI compliance rate calculation
    ctri_compliant = db.query(TrialPatient).filter(TrialPatient.trial_id.isnot(None)).count()
    compliance_rate = (ctri_compliant / total_patients * 100) if total_patients > 0 else 100.0

    return {
        "total_patients_enrolled": total_patients,
        "active_interventions": active_trials,
        "total_adverse_events": ae_count,
        "serious_adverse_events": sae_count,
        "ctri_compliance_rate": round(compliance_rate, 2),
        "dosha_breakdown": dosha_counts
    }