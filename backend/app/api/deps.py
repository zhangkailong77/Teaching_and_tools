from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core import security
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload
from app.core.redis import get_cache, set_cache

# 定义认证入口，如果Token无效，让前端去哪个URL登录（Swagger文档用）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_str}/auth/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 JWT Token
        payload = jwt.decode(token, settings.secret_key, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(sub=username, role=payload.get("role"))
    except JWTError:
        raise credentials_exception

    # 缓存未命中，查数据库
    user = db.query(User).filter(User.username == token_data.sub).first()
    if user is None:
        raise credentials_exception

    # 存入缓存（只存基本字段，1小时过期）
    cache_key = f"user:{username}"
    user_dict = {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "student_number": user.student_number,
    }
    set_cache(cache_key, user_dict, expire=3600)

    return user


def get_current_user_optional(
    db: Session = Depends(get_db),
    request: Request = None,
    token: Optional[str] = None,
) -> Optional[User]:
    """
    可选的用户认证，如果token有效返回用户，否则返回None
    用于需要支持匿名访问但又需要获取用户信息的场景

    支持三种token获取方式：
    1. 查询参数 ?token=xxx
    2. Authorization头 Bearer xxx
    3. Cookie中的token
    """
    # 尝试从多个来源获取token
    auth_token = token

    if not auth_token and request:
        # 尝试从Authorization头获取
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header[7:]  # 去掉 "Bearer " 前缀

        if not auth_token:
            # 尝试从查询参数获取
            auth_token = request.query_params.get("token")

        if not auth_token:
            # 尝试从Cookie获取
            auth_token = request.cookies.get("access_token")
            if auth_token and auth_token.startswith("Bearer%3D"):
                auth_token = auth_token[9:]  # 去掉 URL编码的 "Bearer=" 前缀
            elif auth_token and auth_token.startswith("Bearer="):
                auth_token = auth_token[7:]

    if not auth_token:
        return None

    try:
        payload = jwt.decode(auth_token, settings.secret_key, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        user = db.query(User).filter(User.username == username).first()
        return user
    except JWTError:
        return None