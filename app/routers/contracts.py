import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.core.security import get_current_user
from app.schemas.contract import ContractUploadResponse
from app.services.extractor import extract_text_from_file

router = APIRouter(prefix="/contracts", tags=["Contracts"])

async def validate_file_metadata(file: UploadFile) -> bool:
    # Size check (limit 10MB)
    MAX_SIZE = 10 * 1024 * 1024
    content = await file.read(MAX_SIZE + 1)
    await file.seek(0)
    if len(content) > MAX_SIZE:
        return False
        
    # Format check (limit to md, pdf, docx)
    filename = file.filename.lower()
    if not (filename.endswith(".md") or filename.endswith(".pdf") or filename.endswith(".docx")):
        return False
        
    return True

async def content_security_check(text: str) -> bool:
    # Local keyword check for toxicity (e.g. drug making, illegal activities)
    # Implemented by Roommate C
    illegal_words = ["制作毒品", "窃听", "洗钱"]
    for word in illegal_words:
        if word in text:
            return False
    return True

@router.post("/upload", response_model=ContractUploadResponse)
async def upload_contract(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # 1. Size & Format metadata check
    is_valid = await validate_file_metadata(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="非法文件类型或文件大小超出 10MB 限制"
        )
        
    # 2. Extract Text
    contract_text = await extract_text_from_file(file)
    
    # 3. Content Security Check
    is_safe = await content_security_check(contract_text)
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="文本内容未通过安全合规性审计，拒绝处理"
        )
        
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    # 4. Save contract in database (Roommate B)
    # await save_contract(task_id, contract_text, current_user["id"])
    
    preview_limit = 200
    return ContractUploadResponse(
        status="passed_guardrails",
        message="文件通过前置安全审计，已进入预处理队列",
        contract_preview=contract_text[:preview_limit],
        task_id=task_id
    )
