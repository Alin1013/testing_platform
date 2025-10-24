from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from datetime import datetime
from app.database import Base
from sqlalchemy.sql import func


class ProjectInfo(Base):
    __tablename__ = "projectinfo"
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), index=True, nullable=False)
    test_style = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("userinfo.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())