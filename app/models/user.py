from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True)
    name = Column(String)
    avatar = Column(String)
    enterprise_id = Column(String, default="ent_default")
    created_at = Column(DateTime, default=datetime.utcnow)
