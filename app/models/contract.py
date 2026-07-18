from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.core.database import Base
from datetime import datetime

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
