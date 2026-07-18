import json
import asyncio
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from app.core.security import get_current_user
from app.services.agent_engine import langgraph_engine
from app.services.extractor import parse_and_chunk_document
from app.services.gateway import CostAwareGateway

router = APIRouter(prefix="/contracts", tags=["Agent Engine"])

@router.get("/review/stream")
async def review_contract_stream(
    task_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """
    流式向前端渲染 Agent Loop 思考痕迹 (Server-Sent Events)
    """
    async def event_generator():
        # Mock fetching the contract text from DB using task_id
        mock_contract_text = """
# 商业合作外包合同
## 违约责任
### 己方违约
乙方违约金需支付总金额的 30%。
"""
        
        # 1. Chunking
        chunks = await parse_and_chunk_document(mock_contract_text)
        gateway = CostAwareGateway()
        
        # 2. Process chunks
        for idx, chunk in enumerate(chunks):
            # Route chunk (high/low risk target models)
            routed = await gateway.route_chunk(chunk)
            
            # Retrieve node event
            yield f"event: retrieve\ndata: {json.dumps({'status': 'searching', 'node': 'RetrieveAgentNode', 'message': f'正在并发检索 PostgreSQL+PGVector 混合法条库 (分片 {idx+1}/{len(chunks)})...'})}\n\n"
            await asyncio.sleep(1.0)
            
            # State Graph execution
            initial_state = {
                "contract_id": task_id,
                "current_chunk": routed.content,
                "target_model": routed.target_model,
                "retrieved_laws": [],
                "review_suggestions": [],
                "audit_log_tree": [],
                "loop_count": 0
            }
            
            # Compile and run
            state_result = await langgraph_engine.ainvoke(initial_state)
            
            # SSE Reflection Event
            yield f"event: reflect\ndata: {json.dumps({'status': 'analyzing', 'node': 'ReflectResolveNode', 'message': f'正在对分片 {idx+1} 进行效力位阶核验与冲突消解...'})}\n\n"
            await asyncio.sleep(1.0)
            
            # Final result format
            audit_result = {
                "task_id": task_id,
                "chunk_id": chunk.chunk_id,
                "loop_count": state_result.get("loop_count", 1),
                "risk_suggestions": state_result.get("review_suggestions", []),
                "token_usage": {
                    "model_name": routed.target_model,
                    "prompt_tokens": 1200 + (idx * 110),
                    "completion_tokens": 300 + (idx * 50),
                    "total_tokens": 1500 + (idx * 160),
                    "cost_rmb": round(0.003 + (idx * 0.001), 5)
                }
            }
            yield f"event: audit_complete\ndata: {json.dumps(audit_result)}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
