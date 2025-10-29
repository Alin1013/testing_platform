from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class TestReports(Base):
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("project_info.id"))
    test_type = Column(String(20))
    report_path = Column(String(255))
    status = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())