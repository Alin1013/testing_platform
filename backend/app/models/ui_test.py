from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class UIInfo(Base):
    __tablename__ = "ui_info"

    id = Column(Integer, primary_key=True, index=True)
    case_name = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey("project_info.id"))
    base_url = Column(String(500))
    script_content = Column(Text)
    steps = Column(JSON)
    record = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UIBusinessFlow(Base):
    __tablename__ = "ui_business_flow"

    id = Column(Integer, primary_key=True, index=True)
    flow_name = Column(String(255), nullable=False)
    project_id = Column(Integer, nullable=False)
    case_ids = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UIReport(Base):
    __tablename__ = "ui_report"

    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), nullable=False)
    project_id = Column(Integer, nullable=False)
    status = Column(String(50), default="pending")
    report_path = Column(String(500))
    created_at = Column(DateTime, default=func.now())