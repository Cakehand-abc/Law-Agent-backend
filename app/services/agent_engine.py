from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from app.services.gateway import CostAwareGateway

class ContractAppState(TypedDict):
    contract_id: str
    current_chunk: str
    target_model: str
    retrieved_laws: List[Dict[str, Any]]
    review_suggestions: List[Dict[str, Any]]
    audit_log_tree: List[Dict[str, Any]]
    loop_count: int

# Nodes
async def retrieve_agent_node(state: ContractAppState) -> Dict[str, Any]:
    """
    RetrieveAgentNode (检索体) - PostgreSQL + PGVector 混合检索
    """
    chunk_text = state["current_chunk"]
    
    # Mock retrieve result
    retrieved_result = [
        {"title": "某市地方性劳动条例", "level": 4, "content": "违约金可设为30%"},
        {"title": "中华人民共和国劳动合同法", "level": 2, "content": "违约金不得违反劳动者法定权益"}
    ]
    return {"retrieved_laws": retrieved_result, "loop_count": state.get("loop_count", 0) + 1}

async def reflect_resolve_node(state: ContractAppState) -> Dict[str, Any]:
    """
    ReflectResolveNode (冲突审视体) - 效力位阶过滤
    """
    laws = state["retrieved_laws"]
    suggestions = []
    
    # 效力位阶冲突消解 (宪法 > 法律 > 行政法规 > 地方性法规)
    # level 2 = 法律, level 4 = 地方性法规
    has_conflict = any(l["level"] == 4 for l in laws) and any(l["level"] == 2 for l in laws)
    
    if has_conflict:
        # 硬编码过滤：保留 level 2
        final_law = [l for l in laws if l["level"] == 2][0]
        suggestions = [{
            "risk_tag": "RED",
            "clause_raw": "违约金30%",
            "law_basis": final_law["title"],
            "suggestion": "地方性法规违反上位法《劳动合同法》强制性规定，建议修改违约金比例为不超过法定限制。"
        }]
    else:
        # 默认逻辑
        suggestions = [{
            "risk_tag": "YELLOW",
            "clause_raw": "一般合规条款",
            "law_basis": "中华人民共和国合同法",
            "suggestion": "正常条款，注意保存履约记录。"
        }]
    return {"review_suggestions": suggestions}

async def audit_trail_node(state: ContractAppState) -> Dict[str, Any]:
    """
    AuditTrailNode (审计体) - 留痕树
    """
    snapshot_log = {
        "step": state["loop_count"],
        "retrieved_laws_count": len(state["retrieved_laws"]),
        "resolved_conflicts": True,
        "nodes_traveled": ["RetrieveAgentNode", "ReflectResolveNode"]
    }
    current_tree = state.get("audit_log_tree", [])
    current_tree.append(snapshot_log)
    return {"audit_log_tree": current_tree}

# Router condition
def should_continue_loop(state: ContractAppState):
    if state.get("loop_count", 0) > 5:
        return "force_end"
    return "continue"

workflow = StateGraph(ContractAppState)

workflow.add_node("RetrieveAgent", retrieve_agent_node)
workflow.add_node("ReflectResolve", reflect_resolve_node)
workflow.add_node("AuditTrail", audit_trail_node)

workflow.set_entry_point("RetrieveAgent")
workflow.add_edge("RetrieveAgent", "ReflectResolve")
workflow.add_edge("ReflectResolve", "AuditTrail")

workflow.add_conditional_edges(
    "AuditTrail",
    should_continue_loop,
    {
        "force_end": END,
        "continue": END  # Directly to END for waiting HITL signature in MVP
    }
)

langgraph_engine = workflow.compile()
