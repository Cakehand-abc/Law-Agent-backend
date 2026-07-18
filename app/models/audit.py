from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True)
    chunk_id = Column(String)
    user_id = Column(Integer)
    ai_suggested_text = Column(Text)
    ai_risk_level = Column(String)
    ai_reasoning_tree_snapshot = Column(Text)
    action_type = Column(String)  # ADOPT, REJECT, MODIFY
    user_final_text = Column(Text)
    user_comment = Column(Text)
    digital_signature = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
