from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ProjectInfo(Base):
    __tablename__ = "projectinfo"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), nullable=False)
    test_style = Column(String(20), nullable=False)  # 'api', 'ui', 'performance'
    user_id = Column(Integer, ForeignKey("userinfo.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())