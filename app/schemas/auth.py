from pydantic import BaseModel

class GitHubLoginRequest(BaseModel):
    code: str
    state: str

class UserResponse(BaseModel):
    name: str
    avatar: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
