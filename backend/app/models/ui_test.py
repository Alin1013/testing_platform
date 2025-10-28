from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey,Boolean,DateTime
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class UIInfo(Base):
    __tablename__ = "uiinfo"

    id = Column(Integer, primary_key=True, index=True)
    case_name = Column(String(255))
    project_id = Column(Integer, ForeignKey("projectinfo.id"))
    base_url = Column(String(500))
    script_content = Column(Text)
    steps = Column(Text)  # 存储为JSON字符串
    record = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)