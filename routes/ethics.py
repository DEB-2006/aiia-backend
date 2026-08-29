from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from pydantic import BaseModel
from database import get_db
from models.ethics import EthicsApprovalDB

router = APIRouter(prefix="/api/v1/ethics", tags=["Ethics & Regulatory"])

class EthicsCreate(BaseModel):
    protocol_number: str
    committee_name: str
    regulatory_body: str
    approval_status: str
    submission_date: date
    valid_until: Optional[str] = "Pending"

class EthicsResponse(EthicsCreate):
    id: int

    class Config:
        orm_mode = True

@router.get("/", response_model=List[EthicsResponse])
def list_ethics_approvals(db: Session = Depends(get_db)):
    return db.query(EthicsApprovalDB).all()

@router.post("/", response_model=EthicsResponse, status_code=201)
def create_ethics_approval(payload: EthicsCreate, db: Session = Depends(get_db)):
    existing = db.query(EthicsApprovalDB).filter(EthicsApprovalDB.protocol_number == payload.protocol_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Protocol number already registered.")
    
    new_record = EthicsApprovalDB(**payload.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record