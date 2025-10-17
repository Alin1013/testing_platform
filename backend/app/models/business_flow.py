from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class BusinessFlow(Base):
    __tablename__ = "business_flow"

    id = Column(Integer, primary_key=True, index=True)
    flow_name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("projectinfo.id"))
    test_type = Column(String(20))  # 'api', 'ui'
    case_ids = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())