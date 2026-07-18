from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth import GitHubLoginRequest, TokenResponse, UserResponse
from app.core.security import create_access_token
import httpx
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/github/login", response_model=TokenResponse)
async def github_oauth_callback(payload: GitHubLoginRequest):
    # 1. 校验 state (防止 CSRF, 实际走 Redis)
    # state_valid = verify_state_from_redis(payload.state)
    # if not state_valid: raise HTTPException(status_code=400, detail="State 校验失败，请求不安全")
    
    # 2. 异步向 GitHub 换取 Access Token
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        # Dev fallback: Return mock user if credentials not configured
        mock_user = UserResponse(name="Dev Leader", avatar="https://github.com/identicons/git.png")
        jwt_token = create_access_token(data={"sub": "1"})
        return TokenResponse(access_token=jwt_token, token_type="bearer", user=mock_user)

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": payload.code
            }
        )
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=401, detail="GitHub 授权凭证过期或无效")
            
        # 3. 获取用户信息
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )
        github_user_info = user_response.json()
        
    # 4. User database registration (to be written by Roommate B)
    # user_record = await get_or_create_github_user(github_user_info)
    # jwt_token = create_access_token(data={"sub": str(user_record.id)})
    
    user_name = github_user_info.get("name") or github_user_info.get("login", "GitHub User")
    avatar_url = github_user_info.get("avatar_url", "https://github.com/identicons/git.png")
    
    jwt_token = create_access_token(data={"sub": str(github_user_info.get("id", 9999))})
    
    return TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        user=UserResponse(name=user_name, avatar=avatar_url)
    )
