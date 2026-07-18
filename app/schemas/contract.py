from pydantic import BaseModel
from typing import List, Optional

class ContractUploadResponse(BaseModel):
    status: str
    message: str
    contract_preview: str
    task_id: str

class ContractChunk(BaseModel):
    chunk_id: str
    content_with_meta: str  # 拼接了上级标题路径的最终文本
    raw_content: str        # 原始切片文本
    parent_headers: List[str] # 隶属的各级标题链

class RoutedChunk(BaseModel):
    chunk_id: str
    content: str
    risk_tag: str  # "HIGH_RISK" 或 "LOW_COST"
    target_model: str
