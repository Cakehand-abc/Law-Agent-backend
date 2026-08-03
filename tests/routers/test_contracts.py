import io
import pytest
from fastapi import status

def test_upload_contract_success(client, auth_headers):
    # Arrange: clean markdown file content
    file_content = b"# Test Contract\nThis is a standard compliant contract text for LawShield."
    files = {"file": ("test_contract.md", io.BytesIO(file_content), "text/markdown")}
    
    # Act
    response = client.post(
        "/api/v1/contracts/upload",
        files=files,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "passed_guardrails"
    assert "test_contract.md" not in data["contract_preview"]  # It should extract the actual file content
    assert "Test Contract" in data["contract_preview"]
    assert "task_id" in data

def test_upload_contract_invalid_extension(client, auth_headers):
    # Arrange: txt file is not allowed
    file_content = b"Some plain text"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    
    # Act
    response = client.post(
        "/api/v1/contracts/upload",
        files=files,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "非法文件类型" in response.json()["detail"]

def test_upload_contract_blocked_by_guardrails(client, auth_headers):
    # Arrange: content contains high-risk illegal word
    file_content = b"# Contract\nThis contract mentions illegal words like \xe6\xb4\x97\xe9\x92\xb1 (洗钱)."
    files = {"file": ("malicious.md", io.BytesIO(file_content), "text/markdown")}
    
    # Act
    response = client.post(
        "/api/v1/contracts/upload",
        files=files,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "安全合规性审计" in response.json()["detail"]

def test_upload_contract_unauthorized(client):
    # Arrange: request without auth headers
    file_content = b"Some content"
    files = {"file": ("test.md", io.BytesIO(file_content), "text/markdown")}
    
    # Act
    response = client.post(
        "/api/v1/contracts/upload",
        files=files
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
