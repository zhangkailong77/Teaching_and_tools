# 教学管理系统 (Teaching System)

一个基于 Vue 3 + FastAPI 的教育培训平台，支持学生和教师双角色，提供课程学习、作业提交、AI实训等功能。

## 技术栈

### 前端
- **Vue 3** - Composition API + TypeScript
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **vue-pdf-embed** - PDF 预览与学习

### 后端
- **FastAPI** - Python Web 框架
- **SQLAlchemy** - ORM
- **MySQL** - 主数据库
- **Redis** - 缓存
- **JWT** - 认证

## 项目结构

```
.
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/    # API 路由
│   │   │   ├── content.py    # 课程内容接口
│   │   │   ├── comfy_proxy.py # ComfyUI 代理与排队
│   │   │   └── practice.py   # 实训管理
│   │   ├── core/      # 配置、Redis、安全
│   │   ├── models/    # 数据库模型
│   │   └── schemas/   # Pydantic 模型
│   └── scripts/       # 管理脚本
├── frontend/           # Vue 3 前端
│   ├── src/
│   │   ├── views/     # 页面视图
│   │   │   ├── dashboard/student/  # 学生端
│   │   │   │   ├── course-detail.vue # 课程学习
│   │   │   │   └── comfyui/         # AI实训
│   │   │   └── dashboard/teacher/   # 教师端
│   │   ├── components/# 组件
│   │   ├── api/       # API 服务
│   │   └── stores/    # Pinia 状态
├── docs/              # 文档
├── nginx/             # Nginx 配置
└── docker-compose.yml # Docker 部署
```

## 功能特性

### 学生端
- [x] 浏览课程目录
- [x] PDF 课程学习（支持断点续读）
- [x] 滚动进度自动保存，95% 自动标记完成
- [x] 作业提交与查看
- [x] **ComfyUI AI 实训环境**（支持 GPU 并发）

### 教师端
- [x] 班级管理
- [x] 课程资源管理
- [x] 学生进度查看
- [x] 作业批改

## 特色功能

### ComfyUI AI 实训平台

系统集成了 ComfyUI AI 绘图实训环境，提供完整的 GPU 资源管理和排队调度机制。

#### 功能特点

- **GPU 资源分配**：每位学生分配独立的 ComfyUI 容器端口
- **动态资源启动**：按需启动 GPU 环境（30-60秒冷启动）
- **iframe 内嵌访问**：在教学系统中直接使用 ComfyUI

#### 并发控制与排队机制

```
┌─────────────────────────────────────────────────────────┐
│                    排队调度流程                          │
├─────────────────────────────────────────────────────────┤
│  1. 用户点击"执行工作流"                                 │
│              ↓                                          │
│  2. 检查当前并发数                                        │
│     ├─ 未达上限 → 直接执行                               │
│     └─ 已达上限 → 进入 Redis 队列                        │
│              ↓                                          │
│  3. 前一个任务完成                                        │
│              ↓                                          │
│  4. 异步取出队列中的下一个任务                            │
│              ↓                                          │
│  5. 继续执行直到队列清空                                  │
└─────────────────────────────────────────────────────────┘
```

**核心特性：**
- 最多支持 10 人同时执行（生产环境）
- 自动排队，超限请求进入等待队列
- 实时队列状态监控
- 后台异步任务处理
- 用户可见排队位置和预计等待时间

**Redis 队列数据结构：**
```
comfy:processing_count  # 当前并发数
comfy:queue             # 待执行任务列表 (RPUSH/LPOP)
comfy:task:{task_id}    # 任务状态
```

**前端队列状态展示：**
```
✅ 系统空闲，可用名额: 3/10
⏳ 系统繁忙，当前排队: 2 人
🔴 系统繁忙，正在处理: 10/10
```

#### API 端点

| 端点 | 描述 |
|------|------|
| `POST /comfy_proxy/execute` | 执行工作流（自动排队）|
| `GET /comfy_proxy/queue/status` | 获取队列状态 |
| `GET /comfy_proxy/status/{task_id}` | 查询任务状态 |
| `POST /practice/start-practice` | 启动实训环境 |

### PDF 断点续读

学生退出后重新进入课程时，自动恢复到上次离开的位置。

**技术方案：**
- 滚动位置保存为 0-100 百分比
- 重新打开时，等待 PDF 完全懒加载
- 监控 scrollHeight 稳定后再滚动到目标位置
- 5秒后才允许保存新位置（避免覆盖）

## 快速开始

### 本地开发

**后端**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端**
```bash
cd frontend
npm install
npm run dev
```

### Docker 部署

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker logs -f teaching-backend

# 重启服务
docker restart teaching-backend
```

## 管理脚本

```bash
# 创建教师账号（交互模式）
docker exec -it teaching-backend python /app/create_teacher.py

# 批量导入教师账号
docker exec -it teaching-backend python /app/create_teacher.py --file teachers.xlsx

# 导入课程内容
docker exec -it teaching-backend python /app/import_course.py
```

## 环境变量

> **注意**：敏感配置请参考 `.env.example` 或咨询管理员获取。

### 必需配置项

| 配置项 | 说明 |
|--------|------|
| `DATABASE_URL` | MySQL 连接字符串 |
| `SECRET_KEY` | JWT 签名密钥 |
| `REDIS_HOST` | Redis 服务器地址 |
| `REDIS_PORT` | Redis 端口 |
| `COMFY_GPU_HOST` | GPU 服务器地址 |

## API 端点

| 端点 | 描述 |
|------|------|
| `GET /api/v1/content/courses/me` | 学生获取已授权课程 |
| `GET /api/v1/content/courses/available` | 获取可选课程（建班用）|
| `GET /api/v1/content/courses/{id}/chapters` | 获取课程章节 |
| `PUT /api/v1/content/progress` | 更新学习进度 |

## 文档

- [CLAUDE.md](./CLAUDE.md) - Claude Code 开发指南
- [docs/BUG_FIXES.md](./docs/BUG_FIXES.md) - Bug 修复记录
