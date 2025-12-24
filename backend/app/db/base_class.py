from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # 自动生成表名：将类名 User 转换为表名 users (这里简化处理，直接用小写类名)
    # 也可以写成: return cls.__name__.lower() + "s" 来自动加s
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()