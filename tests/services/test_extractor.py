import pytest
from io import BytesIO
from app.services.extractor import parse_and_chunk_document, extract_text_from_file

@pytest.mark.asyncio
async def test_parse_and_chunk_document():
    # Arrange: Create sample Markdown content with headers and body paragraphs
    markdown_content = """# 租赁合同
## 第一条 标的物
这是关于房屋租赁的第一条内容。

## 第二条 租金支付
### 支付时间
租金应于每月5日前支付。
    """
    
    # Act
    chunks = await parse_and_chunk_document(markdown_content)
    
    # Assert
    assert len(chunks) > 0
    # First chunk checks
    assert chunks[0].chunk_id == "chk_1"  # "chk_0" is likely skipped or is empty or startswith header
    assert chunks[0].raw_content == "这是关于房屋租赁的第一条内容。"
    assert "租赁合同" in chunks[0].parent_headers
    assert "第一条 标的物" in chunks[0].parent_headers
    
    # Check that context path is prepended
    assert "[上下文路径:" in chunks[0].content_with_meta

@pytest.mark.asyncio
async def test_extract_text_from_file():
    # Arrange: Create a mock file object
    class MockFile:
        def __init__(self, content: bytes, filename: str):
            self.content = content
            self.filename = filename
        
        async def read(self):
            return self.content
            
    mock_file = MockFile(b"Hello LawShield", "test.md")
    
    # Act
    extracted = await extract_text_from_file(mock_file)
    
    # Assert
    assert extracted == "Hello LawShield"
