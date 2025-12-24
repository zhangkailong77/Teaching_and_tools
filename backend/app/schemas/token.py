from typing import Optional
from pydantic import BaseModel

# 用于响应登录接口 (返回给前端的)
class Token(BaseModel):
    access_token: str
    token_type: str

# 用于解析 Token 内容 (后端内部使用的)
class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None