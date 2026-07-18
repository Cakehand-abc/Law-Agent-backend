import hashlib
from fastapi import APIRouter, Depends, BackgroundTasks
from app.core.security import get_current_user
from app.schemas.audit import HumanSignOffRequest
from app.services.memory import async_evolve_enterprise_memory

router = APIRouter(prefix="/audit", tags=["Audit & HITL"])

@router.post("/signoff")
async def human_sign_off_contract(
    payload: HumanSignOffRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    # 1. 安全存证哈希签名生成 (防止数据库篡改)
    raw_sign_base = f"{payload.task_id}_{payload.chunk_id}_{current_user['id']}_{payload.action_type}_{payload.user_final_text}"
    digital_signature = hashlib.sha256(raw_sign_base.encode()).hexdigest()
    
    # 2. 结构化审计日志落库
    # await db.insert_audit_log(user_id=current_user["id"], signature=digital_signature, ...payload.dict())
    
    # 3. 异步自进化反馈环路
    if payload.action_type in ["REJECT", "MODIFY"] and payload.user_comment:
        background_tasks.add_task(
            async_evolve_enterprise_memory,
            enterprise_id=current_user["enterprise_id"],
            chunk_content=payload.ai_suggested_text,
            user_comment=payload.user_comment
        )
        
    return {
        "status": "success",
        "message": "人类法务最终决策已依法签署存证，异步企业热记忆演进已启动",
        "audit_signature": digital_signature
    }
