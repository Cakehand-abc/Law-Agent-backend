import re
from typing import List
from app.schemas.contract.py import ContractChunk if False else None # dynamic import bypass for stub
from app.schemas.contract import ContractChunk

async def parse_and_chunk_document(raw_text: str) -> List[ContractChunk]:
    """
    室友 C / 队长 负责实现的 Markdown 层次化切片算法
    """
    markdown_text = raw_text.strip()
    
    current_headers = {1: "未分类主标题", 2: "通用条款", 3: "普通子项"}
    
    # 递归字符分割：优先按段落，其次换行，再次句号
    raw_chunks = re.split(r'\n\n|\n', markdown_text)
    
    processed_chunks = []
    for idx, raw_chunk in enumerate(raw_chunks):
        if not raw_chunk.strip():
            continue
            
        # 动态更新标题树上下文
        if raw_chunk.startswith("# "):
            current_headers[1] = raw_chunk.replace("# ", "")
            continue
        elif raw_chunk.startswith("## "):
            current_headers[2] = raw_chunk.replace("## ", "")
            continue
        elif raw_chunk.startswith("### "):
            current_headers[3] = raw_chunk.replace("### ", "")
            continue
            
        # 语义增强：反向标题拼接
        header_path = f"[上下文路径: {current_headers[1]} -> {current_headers[2]} -> {current_headers[3]}]\n"
        enriched_content = header_path + raw_chunk
        
        chunk_node = ContractChunk(
            chunk_id=f"chk_{idx}",
            content_with_meta=enriched_content,
            raw_content=raw_chunk,
            parent_headers=[current_headers[1], current_headers[2], current_headers[3]]
        )
        processed_chunks.append(chunk_node)
        
    return processed_chunks

async def extract_text_from_file(file) -> str:
    """
    提取 Docx, PDF, MD 中的文字
    """
    # Mock text reading, to be implemented by Roommate C
    filename = getattr(file, "filename", "contract.md")
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    return text
