from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 定义字段（使用小写，符合 Python 规范）
    project_name: str
    api_v1_str: str = "/api/v1"
    secret_key: str
    access_token_expire_minutes: int = 60
    database_url: str
    base_url: str = "http://127.0.0.1:8000"

    # Pydantic V2 配置
    model_config = SettingsConfigDict(
        env_file=".env",       # 指定读取的文件
        case_sensitive=False,  # 【关键】设为 False，这样 PROJECT_NAME 就能自动填入 project_name
        extra="ignore"         # 【关键】忽略 .env 中多余的未知字段，防止报错
    )

settings = Settings()