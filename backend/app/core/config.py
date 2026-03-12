from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # 定义字段（使用小写，符合 Python 规范）
    project_name: str
    api_v1_str: str = "/api/v1"
    secret_key: str
    access_token_expire_minutes: int = 60
    database_url: str
    base_url: str = "http://127.0.0.1:8000"

    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # ComfyUI队列配置
    comfy_gpu_host: str = "edu.yanzhiedu.cn"  # 使用DDNS域名，自动解析到动态IP
    comfy_max_concurrent: int = 1  # 测试环境最大并发
    comfy_max_concurrent_prod: int = 1  # 生产环境最大并发

    # MinIO 头像上传试点配置
    minio_avatar_enabled: bool = False
    minio_endpoint: Optional[str] = None
    minio_domain: Optional[str] = None
    minio_bucket: Optional[str] = None
    minio_access_key: Optional[str] = None
    minio_access_secret: Optional[str] = None
    minio_use_ssl: bool = False
    minio_avatar_prefix: str = "avatars"

    # Pydantic V2 配置
    model_config = SettingsConfigDict(
        env_file=".env",       # 指定读取的文件
        case_sensitive=False,  # 【关键】设为 False，这样 PROJECT_NAME 就能自动填入 project_name
        extra="ignore"         # 【关键】忽略 .env 中多余的未知字段，防止报错
    )

settings = Settings()
