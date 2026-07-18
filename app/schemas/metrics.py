from pydantic import BaseModel
from typing import List

class ModelUsageSummary(BaseModel):
    model_name: str
    total_calls: int
    total_tokens: int

class MetricsDashboardResponse(BaseModel):
    total_spent_rmb: float
    usage_summary: List[ModelUsageSummary]
