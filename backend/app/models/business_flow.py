from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base

class BusinessFlow(Base):
    __tablename__ = "business_flow"

    id = Column(Integer, primary_key=True, index=True)
    flow_name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("project_info.id"))
    test_type = Column(String(20))
    case_ids = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())