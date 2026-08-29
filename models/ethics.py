from sqlalchemy import Column, Integer, String, Date
from database import Base

class EthicsApprovalDB(Base):
    __tablename__ = "ethics_approvals"

    id = Column(Integer, primary_key=True, index=True)
    protocol_number = Column(String, unique=True, index=True)
    committee_name = Column(String)
    regulatory_body = Column(String)
    approval_status = Column(String)
    submission_date = Column(Date)
    valid_until = Column(String)