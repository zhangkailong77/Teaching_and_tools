# Redis缓存集成计划

## 一、什么是Redis缓存？（简单比喻）

**把Redis想象成一个"超级记事本"：**

```
没有缓存的情况：
用户请求 → 后端查询MySQL数据库 → 返回数据
(每次都查数据库，就像每次都要去仓库找东西)

有缓存的情况：
用户请求 → 先问Redis有没有 → 有就直接返回 → 没有才查MySQL并记到Redis
(就像在办公桌上放了一个常用物品的盒子，先在盒子里找，找不到再去仓库)
```

**为什么要加缓存？**
- MySQL数据库查询相对较慢（尤其是复杂查询）
- Redis数据存在内存中，读取速度极快
- 减少数据库压力，提高系统响应速度

---

## 二、需要修改/新增的文件

### 新增文件：
```
backend/
├── app/
│   └── core/
│       └── redis.py          # 新增：Redis连接和缓存工具函数
```

### 修改文件：
```
backend/
├── requirements.txt           # 添加Redis依赖
├── .env                       # 添加Redis配置
├── app/
│   ├── core/
│   │   └── config.py         # 添加Redis配置项
│   └── api/
│       ├── deps.py           # 在用户认证处添加缓存
│       └── v1/
│           └── endpoints/
│               ├── course.py      # 班级列表缓存
│               ├── homework.py    # 作业待办缓存
│               └── announcement.py # 公告缓存
```

---

## 三、具体实现步骤

### 步骤1：安装Redis服务
```bash
# Windows下载Redis
# 下载地址：https://github.com/microsoftarchive/redis/releases
# 或者使用Docker：docker run -d -p 6379:6379 redis
```

### 步骤2：添加Python依赖
在 `backend/requirements.txt` 添加：
```
redis==5.0.1
```

### 步骤3：配置Redis连接

**修改 `app/core/config.py`：**
```python
# 添加Redis配置
redis_host: str = Field(default="localhost", env="REDIS_HOST")
redis_port: int = Field(default=6379, env="REDIS_PORT")
redis_db: int = Field(default=0, env="REDIS_DB")
redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
```

**修改 `.env`：**
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# REDIS_PASSWORD=your_password  # 如果有密码
```

### 步骤4：创建Redis工具类

**新建 `app/core/redis.py`：**
```python
import redis
import json
from app.core.config import settings

# 创建Redis连接
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=True  # 自动将字节转为字符串
)

# 缓存装饰器
def cache(expire=300):
    """
    缓存装饰器
    expire: 缓存过期时间（秒），默认5分钟
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # 先尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # 缓存未命中，执行原函数
            result = func(*args, **kwargs)

            # 将结果存入缓存
            redis_client.setex(cache_key, expire, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

# 手动缓存操作函数
def get_cache(key: str):
    """获取缓存"""
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cache(key: str, value: any, expire: int = 300):
    """设置缓存"""
    redis_client.setex(key, expire, json.dumps(value, default=str))

def delete_cache(key: str):
    """删除缓存"""
    redis_client.delete(key)

def delete_cache_pattern(pattern: str):
    """删除匹配模式的所有缓存"""
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)
```

### 步骤5：在API中使用缓存

**示例1：缓存用户认证信息（修改 `app/api/deps.py`）**
```python
from app.core.redis import get_cache, set_cache

async def get_current_user(...):
    # 先尝试从缓存获取
    cache_key = f"user:{username}"
    cached_user = get_cache(cache_key)
    if cached_user:
        return cached_user

    # 缓存未命中，查数据库
    user = db.query(User).filter(User.username == username).first()

    # 存入缓存（1小时过期）
    if user:
        set_cache(cache_key, user, expire=3600)

    return user
```

**示例2：缓存班级列表（修改 `app/api/v1/endpoints/course.py`）**
```python
from app.core.redis import cache

@router.get("/my")
@cache(expire=1800)  # 缓存30分钟
def read_my_classes(...):
    # 原有查询逻辑不变
    ...
```

**示例3：写操作时清除缓存（修改 `app/api/v1/endpoints/homework.py`）**
```python
from app.core.redis import delete_cache_pattern

@router.post("/{assignment_id}/submit")
def submit_homework(...):
    # 提交作业逻辑
    ...

    # 清除相关缓存（让下次请求获取最新数据）
    delete_cache_pattern(f"student:{current_user.id}:*")
    delete_cache_pattern(f"teacher:{teacher_id}:*")
```

---

## 四、缓存策略建议

| 数据类型 | 缓存时间 | 说明 |
|---------|---------|------|
| 用户认证信息 | 1小时 | 变化频率低 |
| 班级列表 | 30分钟 | 教师创建班级时清除 |
| 课程章节内容 | 1小时 | 静态内容，变化少 |
| 作业待办列表 | 5分钟 | 需要较新的数据 |
| 统计数据 | 10分钟 | 聚合计算，缓存价值高 |
| 公告列表 | 10分钟 | 较短时间保证时效性 |

---

## 五、缓存键命名规范

```python
# 用户相关
"user:{user_id}"                    # 用户基本信息
"teacher:{teacher_id}:classes"      # 教师的班级列表
"student:{student_id}:todos"        # 学生的待办事项

# 作业相关
"homework:{assignment_id}"          # 作业详情
"student:{student_id}:submissions"  # 学生的提交记录

# 统计相关
"stats:teacher:{teacher_id}"        # 教师统计数据

# 通用模式
"{模块}:{资源ID}:{可选参数}"
```

---

## 六、测试验证

```bash
# 1. 确保Redis服务运行
redis-cli ping  # 应返回 PONG

# 2. 启动后端服务
cd backend
uvicorn app.main:app --reload

# 3. 观察缓存效果
redis-cli monitor  # 实时查看Redis操作

# 4. 测试API
# 第一次请求：会查数据库并写入缓存
# 第二次请求：直接从缓存返回，速度更快
```

---

## 七、注意事项

1. **缓存一致性**：写操作后记得清除相关缓存
2. **缓存雪崩**：给不同的键设置稍微不同的过期时间
3. **缓存穿透**：对不存在的数据也做缓存（存空值）
4. **Redis故障**：添加异常处理，Redis挂了不影响主流程
5. **数据序列化**：复杂对象需要用json.dumps的default参数处理

---

## 八、渐进式实施方案

**阶段1：基础搭建（本次实施）**
- 安装Redis和Python依赖
- 创建Redis工具类
- 在1-2个接口上试点缓存

**阶段2：全面应用（后续优化）**
- 在更多接口添加缓存
- 完善缓存失效逻辑
- 添加缓存监控

**阶段3：高级特性（可选）**
- 缓存预热（系统启动时预加载热数据）
- 分布式缓存（多服务器共享）
- 缓存击穿防护
