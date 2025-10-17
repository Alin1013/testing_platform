from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class UIInfo(Base):
    __tablename__ = "uiinfo"

    id = Column(Integer, primary_key=True, index=True)
    case_name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("projectinfo.id"))
    script_content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())