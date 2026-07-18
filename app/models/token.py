from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base
from datetime import datetime

class TokenAuditLog(Base):
    __tablename__ = "token_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True)
    model_name = Column(String)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    cost_rmb = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
