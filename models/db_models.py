from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey, Enum, BigInteger
from datetime import datetime, timezone
import enum
from database import Base

class UserRole(str, enum.Enum):
    INVESTIGATOR = "Investigator"
    SPONSOR = "Sponsor"
    AUDITOR = "Auditor"
    ETHICS_COMMITTEE = "Ethics_Committee"
    ADMIN = "Admin"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ClinicalTrial(Base):
    __tablename__ = "clinical_trials"

    trial_id = Column(Integer, primary_key=True, index=True)
    ctri_registration_number = Column(String(100), unique=True, nullable=False)
    trial_title = Column(Text, nullable=False)
    phase = Column(String(50), nullable=False)
    sponsor_name = Column(String(255), default="AIIA")
    status = Column(String(50), default="On-Going")
    start_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class TrialPatient(Base):
    __tablename__ = "trial_patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    trial_id = Column(Integer, ForeignKey("clinical_trials.trial_id", ondelete="RESTRICT"))
    subject_id = Column(String(100), unique=True, nullable=False)
    enrollment_date = Column(Date, nullable=False)
    status = Column(String(50), default="Active")

class ClinicalAuditTrail(Base):
    __tablename__ = "clinical_audit_trail"

    log_id = Column(BigInteger, primary_key=True, index=True)
    trial_id = Column(Integer, ForeignKey("clinical_trials.trial_id", ondelete="RESTRICT"))
    patient_id = Column(String(100), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"))
    action_type = Column(String(50), nullable=False)
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))