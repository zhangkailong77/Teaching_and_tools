from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. 创建数据库引擎
# 注意：这里必须使用 settings.database_url (小写)，因为我们在 config.py 里改成了小写
engine = create_engine(settings.database_url, pool_pre_ping=True)

# 2. 创建 SessionLocal 类
# 这是一个“工厂”，每次调用它都会产生一个新的数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)