from sqlalchemy import Column, Integer, String, Boolean,DateTime
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime


class UserInfo(Base):
    __tablename__ = "userinfo"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_path = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)