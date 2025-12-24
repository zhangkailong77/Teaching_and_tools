from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 加密算法
ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 注意：这里使用小写的 access_token_expire_minutes，对应 config.py
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    # 将数据放入 Token
    to_encode = {"exp": expire, **subject}
    
    # 注意：这里使用小写的 secret_key，对应 config.py
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

# --- 之前缺失的函数是下面这个 ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码和数据库里的哈希密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """将明文密码转换为哈希值 (用于注册)"""
    return pwd_context.hash(password)