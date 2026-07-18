from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.core.security import get_current_user
from app.schemas.audit import HumanSignOffRequest # placeholder import
from pydantic import BaseModel
from app.services.pdf_generator import render_legal_contract_to_pdf
from app.schemas.metrics import MetricsDashboardResponse, ModelUsageSummary

router = APIRouter(prefix="/reports", tags=["Reports & Operations"])

class ExportReportRequest(BaseModel):
    task_id: str
    final_contract_text: str

@router.post("/export/pdf")
async def export_contract_pdf(
    payload: ExportReportRequest,
    current_user: dict = Depends(get_current_user)
):
    watermark_text = "【律盾系统提示：此合同由 AI 辅助初审生成，仅供参考，具体责任由人类最终拍板人承担】"
    pdf_filename = f"contract_{payload.task_id}.pdf"
    pdf_output_path = f"./{pdf_filename}"
    
    success = await render_legal_contract_to_pdf(
        text=payload.final_contract_text,
        watermark=watermark_text,
        output_path=pdf_output_path
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="PDF 渲染引擎故障，报告生成失败")
        
    return FileResponse(
        path=pdf_output_path, 
        filename=pdf_filename, 
        media_type="application/pdf"
    )

@router.get("/token/metrics", response_model=MetricsDashboardResponse)
async def get_token_metrics(current_user: dict = Depends(get_current_user)):
    # Mock data aggregate (Roommate B)
    # Select from token_audit_logs group by model_name
    usage_list = [
        ModelUsageSummary(model_name="deepseek-v4", total_calls=45, total_tokens=5420000),
        ModelUsageSummary(model_name="qwen-2.5-7b-instruct", total_calls=88, total_tokens=1240000)
    ]
    return MetricsDashboardResponse(
        total_spent_rmb=12.456,
        usage_summary=usage_list
    )
