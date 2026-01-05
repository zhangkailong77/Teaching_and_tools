from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.base_class import Base
from app.db.session import engine
from app.models import user, course, profile, content

# 1. 自动创建数据库表
# 当你运行项目时，SQLAlchemy 会检查 models 定义，并在 MySQL 中创建缺失的表 (如 users 表)
# 注意：在生产环境中通常使用 Alembic 进行迁移，但在开发初期这样最方便
Base.metadata.create_all(bind=engine)

# 2. 初始化 FastAPI 应用
app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# 3. 配置 CORS (跨域资源共享)
# 前端运行在 localhost:5173，后端在 localhost:8000
# 必须允许跨域，否则前端无法调用后端接口
origins = [
    "http://localhost:5173", # Vue 默认端口
    "http://127.0.0.1:5173",
    "http://ai.yz-cube.com:5173",
    "http://localhost:3000", # 备用
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 允许的来源列表
    allow_credentials=True,      # 允许携带 Cookie/Token
    allow_methods=["*"],         # 允许所有方法 (GET, POST, PUT, DELETE...)
    allow_headers=["*"],         # 允许所有 Header
)

upload_dirs = [
    "static/uploads/avatars", # 存头像
    "static/uploads/courses", # 存课程封面
    "static/uploads/common"   # 存通用图片
]

for dir_path in upload_dirs:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")

# 挂载静态目录
# 这样前端访问 http://127.0.0.1:8000/static/xxx.jpg 就能看到图片了
app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. 注册路由
# 将 app/api/v1/api.py 中汇总的所有接口挂载到 /api/v1 路径下
app.include_router(api_router, prefix=settings.api_v1_str)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 5. (可选) 本地调试入口
if __name__ == "__main__":
    import uvicorn
    # 这样你可以直接运行 python app/main.py 启动服务
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", access_log=True)