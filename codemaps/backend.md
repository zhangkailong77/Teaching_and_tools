# 后端架构详解

> 生成时间：2026-01-30

## 一、目录结构

```
backend/
├── app/
│   ├── main.py              # 应用入口 FastAPI 实例
│   ├── api/
│   │   ├── v1/
│   │   │   ├── api.py       # 路由汇总入口
│   │   │   └── endpoints/   # 各功能模块路由
│   │   └── deps.py          # 依赖注入（认证中间件）
│   ├── core/
│   │   ├── config.py        # Pydantic Settings 配置
│   │   ├── security.py      # JWT、BCrypt 工具
│   │   └── redis.py         # Redis 缓存操作封装
│   ├── db/
│   │   ├── session.py       # SQLAlchemy SessionLocal
│   │   └── base_class.py    # Base 元类
│   ├── models/              # SQLAlchemy ORM 模型
│   ├── schemas/             # Pydantic 数据校验
│   ├── utils/               # 工具函数
│   └── utils/
├── requirements.txt
└── scripts/
```

## 二、核心文件说明

### 2.1 应用入口（main.py）

- 初始化 FastAPI 实例
- 配置 CORS 中间件
- 挂载静态文件目录 `/static`
- 注册路由聚合器 `api_router`
- 启动时自动创建数据库表

### 2.2 路由注册（api.py）

```python
# 挂载格式
api_router.include_router(module.router, prefix="/模块路径", tags=["模块名"])
```

当前已注册模块：

| 前缀 | 模块 | 主要功能 |
|------|------|---------|
| `/auth` | auth.py | 登录、注册、Token |
| `/users` | users.py | 用户信息 |
| `/classes` | course.py | 班级、学生、选课 |
| `/profiles` | profile.py | 教师/学生档案 |
| `/upload` | upload.py | 文件上传 |
| `/content` | content.py | 课程资源、章节 |
| `/homeworks` | homework.py | 作业管理 |
| `/exam` | exam.py | 考试系统 |
| `/announcements` | announcement.py | 公告 |
| `/practice` | practice.py | 实训 |
| `/comfy_proxy` | comfy_proxy.py | AI 绘画队列 |

### 2.3 依赖注入（deps.py）

```python
def get_db() -> Generator:
    """数据库会话依赖"""

def get_current_user() -> User:
    """JWT Token 解析依赖"""
```

所有需要鉴权的接口通过 `Depends(get_current_user)` 获取当前用户。

## 三、API 端点清单

### 3.1 认证模块（/auth）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` | 用户登录 |
| POST | `/auth/register` | 用户注册 |

### 3.2 课程内容模块（/content）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/content/courses/me` | 获取课程资源库（含锁定状态） |
| GET | `/content/courses/available` | 获取可选课程（仅已授权） |
| GET | `/content/courses/{id}` | 获取课程详情 |
| GET | `/content/courses/{id}/chapters` | 获取章节大纲（缓存 5 分钟） |
| GET | `/content/courses/{id}/tasks` | 获取作业模板列表 |

### 3.3 班级管理模块（/classes）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/classes/my-classes` | 获取教师班级列表 |
| POST | `/classes/` | 创建班级 |
| PUT | `/classes/{id}` | 更新班级信息 |
| PUT | `/classes/{id}/status` | 切换班级状态 |
| DELETE | `/classes/{id}` | 删除班级 |
| GET | `/classes/{id}/students` | 获取班级学生列表 |
| POST | `/classes/{id}/students` | 添加学生 |
| DELETE | `/classes/{id}/students/{student_id}` | 移除学生 |
| POST | `/classes/{id}/students/batch` | 批量导入学生 |
| GET | `/classes/my-students` | 获取教师所有学生 |
| POST | `/classes/{id}/bind` | 绑定课程资源包 |

### 3.4 作业模块（/homeworks）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/homeworks/teacher/stats` | 教师作业统计 |
| GET | `/homeworks/teacher/list` | 教师作业列表 |
| GET | `/homeworks/student/todos` | 学生待办作业 |
| POST | `/homeworks/{id}/publish` | 发布作业 |
| POST | `/homeworks/{assignment_id}/submit` | 学生提交作业 |
| POST | `/homeworks/submissions/{submission_id}/grade` | 教师批改 |

## 四、配置管理

### 4.1 环境变量（.env）

```python
# settings.py 自动读取 .env 文件
DATABASE_URL = "mysql+pymysql://root:password@host:3306/dbname"
SECRET_KEY = "jwt-secret-key"
REDIS_HOST = "redis"
REDIS_PORT = 6379
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

### 4.2 Docker 环境变量（docker-compose.yml）

```yaml
environment:
  - DATABASE_URL=mysql+pymysql://root:teaching2024@mysql:3306/teaching_platform
  - REDIS_HOST=redis
  - REDIS_PORT=6379
```

## 五、脚本工具

| 脚本 | 用途 |
|------|------|
| `create_user.py` | 创建单个用户（教师/学生） |
| `create_teacher.py` | 创建教师并授权课程 |
| `import_course.py` | 导入课程章节和 PDF 文件 |
| `teacher_course_access.py` | 批量授权课程给教师 |
| `test_redis.py` | Redis 连接测试 |

## 六、部署相关

### 6.1 Docker 服务

| 容器名 | 端口 | 说明 |
|--------|------|------|
| teaching-backend | 8000 | FastAPI 服务 |
| teaching-mysql | 3306 | MySQL 数据库 |
| teaching-redis | 6379 | Redis 缓存 |
| teaching-frontend | 2026 | Nginx 前端 |

### 6.2 数据持久化

```yaml
volumes:
  - mysql-data:/var/lib/mysql    # MySQL 数据
  - redis-data:/data             # Redis 数据
  - ./backend/static:/app/static # 上传文件
```
