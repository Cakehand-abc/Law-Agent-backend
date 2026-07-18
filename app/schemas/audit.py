from pydantic import BaseModel
from typing import Optional

class HumanSignOffRequest(BaseModel):
    task_id: str
    chunk_id: str
    ai_suggested_text: str
    ai_risk_level: str
    ai_reasoning_tree_snapshot: str  # JSON string
    action_type: str  # ADOPT / REJECT / MODIFY
    user_final_text: str
    user_comment: Optional[str] = None
