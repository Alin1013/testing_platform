from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from app.database import Base


class APIInfo(Base):
    __tablename__ = "apiinfo"

    id = Column(Integer, primary_key=True, index=True)
    case_name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("projectinfo.id"))
    method = Column(String(10), nullable=False)
    url = Column(Text, nullable=False)
    headers = Column(JSON)
    params = Column(JSON)
    body = Column(JSON)
    expected_data = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())