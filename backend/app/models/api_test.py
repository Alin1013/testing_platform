from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class APIInfo(Base):
    __tablename__ = "api_info"  # 统一使用小写和下划线

    id = Column(Integer, primary_key=True, index=True)
    case_name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("project_info.id"))
    method = Column(String(10), nullable=False)
    url = Column(Text, nullable=False)
    headers = Column(JSON)
    params = Column(JSON)
    body = Column(JSON)
    expected_data = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())

class APIBusinessFlow(Base):
    __tablename__ = "api_business_flow"

    id = Column(Integer, primary_key=True, index=True)
    flow_name = Column(String(255), nullable=False)
    project_id = Column(Integer, nullable=False)
    case_ids = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class APIReport(Base):
    __tablename__ = "api_report"

    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), nullable=False)
    project_id = Column(Integer, nullable=False)
    status = Column(String(50), default="pending")
    report_path = Column(String(500))
    created_at = Column(DateTime, default=func.now())