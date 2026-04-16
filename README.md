# 教学管理系统接手文档（README）

> 这份 README 以**第一次接手这个项目的人**为默认读者。  
> 目标不是介绍概念，而是让你能尽快完成：**部署、启动、本地调试、环境配置、日常运维、问题排查、资源导入和账号初始化**。

---

## 1. 项目是什么

这是一个 **教学管理系统 / 培训平台**，采用 **前后端分离** 架构：

- **前端**：Vue 3 + TypeScript + Vite + Element Plus
- **后端**：FastAPI + SQLAlchemy
- **数据库**：MySQL 8
- **缓存 / 队列**：Redis 7
- **部署方式**：Docker Compose + Nginx
- **特色能力**：集成 **ComfyUI AI 实训环境**，支持 GPU 资源分配、远程启动、代理访问、任务排队
- **扩展能力**：包含和“任务大厅 / skillmarket”的联邦 SSO 与用户同步配置

系统主要覆盖以下业务：

- 用户登录 / JWT 鉴权
- 学生端课程学习
- 教师端课程、班级、作业、考试、公告管理
- 课程资料上传 / 静态资源访问
- PDF/PPT/视频等教学资源展示
- ComfyUI 实训入口与排队代理
- 部分文件上传支持 MinIO 试点配置

---

## 2. 这份文档适合谁看

如果你现在要接手这个系统，通常你最关心的是：

1. **项目怎么跑起来**
2. **本地怎么调试**
3. **生产怎么部署 / 重启 / 看日志**
4. **环境变量到底哪些必须配**
5. **课程资源、账号、教师权限怎么处理**
6. **ComfyUI 为什么会不通 / 排队为什么异常**
7. **这个仓库里有哪些容易踩坑的地方**

这份 README 会按这个顺序来写。

---

## 3. 仓库结构（接手时先看这里）

```text
2026_teaching_system/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/endpoints/   # 各业务接口
│   │   ├── core/               # 配置、安全、Redis 等核心模块
│   │   ├── db/                 # 数据库连接与 Base
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic 模型
│   │   └── main.py             # 后端入口
│   ├── static/                 # 上传文件、课程资源、交互资源
│   ├── tests/                  # 后端测试
│   ├── .env.example            # 环境变量模板
│   ├── create_teacher.py       # 教师创建 / 批量导入
│   ├── create_user.py          # 用户创建脚本
│   ├── import_course.py        # 课程资源导入脚本
│   ├── manage_course.py        # 课程管理脚本
│   └── teacher_course_access.py# 教师课程授权脚本
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── router/
│   │   ├── stores/
│   │   ├── utils/
│   │   └── views/
│   ├── .env.development        # 前端开发环境变量
│   ├── .env.production         # 前端生产环境变量
│   ├── package.json
│   └── vite.config.ts          # 本地开发代理配置（这里有硬编码地址，后文会特别说明）
├── nginx/
│   └── nginx.conf              # 生产用反向代理配置
├── docs/                       # 辅助文档
├── docker-compose.yml          # 一键部署编排文件
├── Dockerfile.backend          # 后端镜像
├── Dockerfile.frontend         # 前端镜像
└── teaching_platform.sql       # MySQL 初始化数据
```

---

## 4. 核心架构与访问链路

### 4.1 正常访问链路

浏览器访问：

```text
用户浏览器
   ↓
Nginx / 前端容器（80 -> 宿主机 2026）
   ├── /            -> 前端静态页面
   ├── /api/        -> 转发给 FastAPI 后端
   ├── /static/     -> 前端静态资源
   ├── /static/uploads/ -> 转发给后端静态文件目录
   └── /comfyui/... -> 转发到 GPU 服务器上的 ComfyUI 对应端口
```

### 4.2 Docker 默认端口

| 服务 | 容器名 | 宿主机端口 | 说明 |
|---|---|---:|---|
| frontend + nginx | `teaching-frontend` | `2026` | 系统前台入口 |
| backend | `teaching-backend` | `8000` | FastAPI 接口 |
| mysql | `teaching-mysql` | `13306` | MySQL 数据库 |
| redis | `teaching-redis` | `6380` | Redis |

### 4.3 常用访问地址

| 地址 | 用途 |
|---|---|
| `http://localhost:2026` | 前端页面入口 |
| `http://localhost:8000/docs` | FastAPI Swagger 文档 |
| `http://localhost:8000/redoc` | FastAPI ReDoc |
| `http://localhost:13306` | MySQL 暴露端口（给本机客户端使用） |
| `http://localhost:6380` | Redis 暴露端口（给本机工具使用） |

---

## 5. 技术栈与实际依赖

### 5.1 前端

- Vue 3
- TypeScript
- Vite
- Element Plus
- Pinia
- Vue Router
- ECharts
- vue-pdf-embed
- xlsx
- v-calendar

### 5.2 后端

- Python 3.11（Dockerfile 使用 `python:3.11-slim`）
- FastAPI
- Uvicorn
- SQLAlchemy
- PyMySQL
- Redis
- Paramiko（用于远程操作 GPU 服务器）
- Pandas / openpyxl（用于 Excel 导入）
- MinIO SDK（头像 / 文件存储试点）

### 5.3 基础设施

- Docker / Docker Compose
- MySQL 8.0
- Redis 7
- Nginx
- 外部 GPU 主机（ComfyUI）

---

## 6. 功能模块速览

后端接口聚合入口在：`backend/app/api/v1/api.py`

当前主要模块：

- `auth`：登录鉴权
- `users`：用户信息
- `practice`：实训环境启动相关
- `course`：班级 / 课程管理
- `profile`：档案信息
- `upload`：上传能力
- `content`：课程内容、学习进度
- `homework`：作业
- `exam`：考试
- `announcement`：公告
- `comfy_proxy`：ComfyUI 工作流代理和排队
- `federation`：任务大厅联邦 SSO / 同步

如果你要快速定位问题，通常先看这几个文件：

- 后端入口：`backend/app/main.py`
- 后端配置：`backend/app/core/config.py`
- 前端请求封装：`frontend/src/utils/request.ts`
- 前端开发代理：`frontend/vite.config.ts`
- Nginx 转发：`nginx/nginx.conf`
- Docker 编排：`docker-compose.yml`

---

## 7. 环境变量说明（非常重要）

后端配置由 `backend/app/core/config.py` 读取，**固定读取 `backend/.env`**，不会跟随当前 shell 工作目录自动变化。

也就是说：

- 你需要确保 `backend/.env` 存在
- 不是根目录 `.env`
- 不是系统环境变量优先覆盖的那种随意模式
- 本项目默认就是读 `backend/.env`

### 7.1 推荐初始化方式

```bash
cp backend/.env.example backend/.env
```

然后按环境修改。

### 7.2 后端必配项

| 变量 | 是否必须 | 说明 |
|---|---|---|
| `PROJECT_NAME` | 是 | FastAPI 项目名 |
| `API_V1_STR` | 是 | API 前缀，默认 `/api/v1` |
| `SECRET_KEY` | 是 | JWT 签名密钥，生产务必替换 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 是 | Token 过期分钟数 |
| `DATABASE_URL` | 是 | MySQL 连接串 |
| `REDIS_HOST` | 是 | Redis 主机 |
| `REDIS_PORT` | 是 | Redis 端口 |
| `REDIS_DB` | 是 | Redis DB |
| `SCHOOL_ID` | 建议 | 单校配置标识 |
| `SCHOOL_NAME` | 建议 | 学校名，启动时会写入 `school_config` |
| `COMFY_GPU_HOST` | 如果启用 ComfyUI 则必配 | GPU 服务器地址 |
| `COMFY_GPU_USER` | 如果启用 ComfyUI 则必配 | SSH 用户 |
| `COMFY_GPU_PASSWORD` | 如果启用 ComfyUI 则必配 | SSH 密码 |
| `COMFY_BASE_PATH` | 如果启用 ComfyUI 则必配 | GPU 上 ComfyUI 根目录 |
| `COMFY_CONDA_INIT_SCRIPT` | 如果启用 ComfyUI 则必配 | conda 初始化脚本 |
| `COMFY_CONDA_ENV_NAME` | 如果启用 ComfyUI 则必配 | ComfyUI conda 环境名 |
| `COMFY_MAX_CONCURRENT` | 建议 | 开发并发数 |
| `COMFY_MAX_CONCURRENT_PROD` | 建议 | 生产并发数 |
| `SYNC_ENABLED` | 如果对接任务大厅则建议 | 是否启用联邦同步 |
| `TASK_HALL_WEB_URL` | 如果对接任务大厅则必配 | 任务大厅前端地址 |
| `TASK_HALL_API_BASE_URL` | 如果对接任务大厅则必配 | 任务大厅 API 地址 |
| `FEDERATION_SECRET` | 如果对接任务大厅则必配 | 双方共享密钥 |
| `MINIO_*` | 可选 | 文件存储试点配置 |

### 7.3 前端环境变量

开发环境：`frontend/.env.development`

生产环境：`frontend/.env.production`

当前已存在配置项：

| 变量 | 用途 |
|---|---|
| `VITE_API_URL` | 前端请求 API 的基础地址 |
| `VITE_IMG_BASE_URL` | 图片 / 文件资源基础地址 |
| `VITE_TASK_HALL_WEB_URL` | 任务大厅前端兜底地址 |

### 7.4 一个很关键的事实

虽然前端有 `.env.development`，但 `frontend/vite.config.ts` 里仍然存在**硬编码代理地址**：

- `/api` 代理到 `http://192.168.150.27:8000`
- `/static/js/comfyui-queue.js` 代理到 `http://192.168.150.27:5173`
- `/comfyui` 代理到 `http://edu.yanzhiedu.cn`

所以：

> **如果你在别的机器本地调试，这个文件通常必须先改。**

否则会出现：前端启动了，但请求打到了旧机器 / 旧内网地址。

---

## 8. 启动方式一：推荐接手人先用 Docker 跑通

如果你只是想先确认系统能起来，建议优先用 Docker Compose。

### 8.1 前提条件

本机已安装：

- Docker Desktop / Docker Engine
- Docker Compose v2+
- Git

### 8.2 启动前检查

```bash
docker --version
docker compose version
docker ps
```

### 8.3 启动步骤

```bash
# 1) 进入项目根目录
cd /Users/zhangkailong/workspace/交接/2026_teaching_system

# 2) 确认后端环境变量文件存在
cp -n backend/.env.example backend/.env

# 3) 构建并启动
docker compose up -d --build

# 4) 查看状态
docker compose ps
```

### 8.4 验证是否启动成功

```bash
# 前端首页
curl -I http://127.0.0.1:2026

# 后端健康验证（至少 Swagger 应该能打开）
curl -I http://127.0.0.1:8000/docs

# 查看后端日志
docker logs --tail 200 teaching-backend
```

### 8.5 停止 / 重启

```bash
# 停止
 docker compose down

# 重启全部
 docker compose restart

# 只重启后端
 docker restart teaching-backend

# 只重启前端
 docker restart teaching-frontend
```

---

## 9. 启动方式二：本地开发调试（前后端分开跑）

如果你要改代码、查接口、单步调试，推荐本地开发模式。


### 9.1 最实用的开发方式

**推荐模式：数据库和 Redis 用 Docker 跑，前后端代码在本机直接运行。**

原因：

- MySQL / Redis 省去安装麻烦
- 后端改代码热更新快
- 前端改页面即时刷新
- 排查日志也更方便

### 9.2 先启动 MySQL 和 Redis

如果你只想起基础依赖，可以只启动：

```bash
docker compose up -d mysql redis
```

此时你需要把 `backend/.env` 的数据库和 Redis 地址改成适合本机直连的形式，例如：

```env
DATABASE_URL=mysql+pymysql://root:teaching2024@127.0.0.1:13306/teaching_platform
REDIS_HOST=127.0.0.1
REDIS_PORT=6380
REDIS_DB=0
```

> 注意：`docker-compose.yml` 里容器内部端口是 `3306/6379`，映射到宿主机后变成 `13306/6380`。

### 9.3 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后访问：

- `http://127.0.0.1:8000/docs`

### 9.4 启动前端

```bash
cd frontend
npm install
npm run dev
```

默认开发端口：

- `http://127.0.0.1:5173`

### 9.5 本地开发最常见的坑

#### 坑 1：前端明明写了 `.env.development`，但接口还是请求到旧服务器

因为 `frontend/vite.config.ts` 里写死了：

- `target: 'http://192.168.150.27:8000'`
- `target: 'http://192.168.150.27:5173'`

**接手新环境时务必先改。**

建议本地调试改成：

```ts
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
    secure: false,
    ws: true,
  }
}
```

#### 坑 2：后端 `.env` 用的是 Docker 服务名，结果本地跑不通

例如：

```env
DATABASE_URL=mysql+pymysql://root:xxx@mysql:3306/teaching_platform
REDIS_HOST=redis
```

这只适用于 **容器内部互联**。  
如果后端是你本机直接启动，应该改成 `127.0.0.1` + 宿主机映射端口。

#### 坑 3：ComfyUI 地址能打开但工作流执行失败

ComfyUI 不是单纯 HTTP 页面代理，还涉及：

- 用户是否分配了 `comfyui_port`
- GPU 服务器是否可连通
- SSH 配置是否正确
- Redis 队列是否正常
- 端口映射 / 代理 URL 是否正确

只看页面能不能打开，不足以说明链路没问题。

---

## 10. Docker Compose 里实际部署了什么

当前 `docker-compose.yml` 启动 4 个核心服务：

1. `frontend`
2. `backend`
3. `mysql`
4. `redis`

### 10.1 前端服务

- 使用 `Dockerfile.frontend` 构建
- 先用 Node 20 构建前端产物
- 再用 Nginx 提供静态文件服务
- 暴露端口：`2026:80`

### 10.2 后端服务

- 使用 `Dockerfile.backend` 构建
- 运行命令：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- 暴露端口：`8000:8000`
- 挂载：
  - `./backend/static:/app/static`
  - `/root/teaching-course:/course-data`

`/course-data` 这个目录是课程资源导入时常见的挂载点，接手生产环境时要确认宿主机上它是否存在、是否有权限、内容是否还在。

### 10.3 MySQL 服务

- 镜像：`mysql:8.0`
- 端口：`13306:3306`
- 初始化 SQL：`./teaching_platform.sql`
- 数据卷：`mysql-data`

### 10.4 Redis 服务

- 镜像：`redis:7-alpine`
- 端口：`6380:6379`
- 数据卷：`redis-data`

---

## 11. Nginx 做了哪些事

生产环境的前端容器里运行的是 Nginx，配置文件：`nginx/nginx.conf`

它做了 4 件关键事情：

1. 提供前端静态页面
2. 把 `/api/` 转发给后端
3. 把 `/static/uploads/` 转发给后端静态文件目录
4. 把 `/comfyui/{username}/{port}/...` 转发到 GPU 主机上的对应端口

### 11.1 为什么 ComfyUI 能嵌在系统里

因为 Nginx 有这样一类规则：

```nginx
location ~ ^/comfyui/([^/]+)/(\d+)(.*)$ {
    proxy_pass http://edu.yanzhiedu.cn:$comfy_port$raw_path;
}
```

也就是说，前端访问：

```text
/comfyui/用户名/8189/...
```

Nginx 会代理成：

```text
http://edu.yanzhiedu.cn:8189/...
```

### 11.2 这意味着什么

如果 ComfyUI 打不开，排查要看三层：

1. Nginx 代理规则有没有问题
2. GPU 主机域名 `edu.yanzhiedu.cn` 是否可访问
3. 对应端口上的 ComfyUI 服务是否真的启动了

---

## 12. ComfyUI / GPU 实训链路说明

这是系统最容易出故障、也是最需要交接说明的模块。

### 12.1 功能目标

- 每个学生 / 用户分配一个 ComfyUI 端口
- 用户点击“启动实训环境”后，后端通过 SSH 到 GPU 服务器上启动对应实例
- 页面里通过 iframe / 代理路径访问 ComfyUI
- 执行工作流时由后端统一做代理和排队

### 12.2 关键依赖

- `COMFY_GPU_HOST`
- `COMFY_GPU_SSH_PORT`
- `COMFY_GPU_USER`
- `COMFY_GPU_PASSWORD`
- `COMFY_BASE_PATH`
- `COMFY_CONDA_INIT_SCRIPT`
- `COMFY_CONDA_ENV_NAME`
- Redis

### 12.3 队列相关 Redis 键

根据现有实现和文档，重点关注：

```text
comfy:processing_count   # 当前处理中任务数
comfy:queue             # 待执行任务队列
comfy:task:{task_id}    # 单任务状态
```

### 12.4 排查 ComfyUI 问题建议顺序

1. 看后端日志：`docker logs -f teaching-backend`
2. 确认 Redis 正常：队列键是否存在 / 是否堆积
3. 确认 GPU 主机能否访问：`edu.yanzhiedu.cn`
4. 确认 SSH 凭据没失效
5. 确认该用户是否已分配 `comfyui_port`
6. 确认 Nginx 代理路径是否正确
7. 如果页面能开但执行失败，重点查 `comfy_proxy` 接口和 Redis 队列

### 12.5 生产注意事项

当前仓库里默认并发值并不高：

- `COMFY_MAX_CONCURRENT=2`
- `COMFY_MAX_CONCURRENT_PROD=2`（compose 里也是 2）

如果你的真实生产要支持更多人同时执行，需要：

- 评估 GPU 实际承载能力
- 调整后端并发配置
- 验证 Redis 队列处理逻辑
- 验证前端排队提示是否仍准确

---

## 13. 课程资源与静态文件说明

### 13.1 后端静态目录

后端启动时会自动确保以下目录存在：

```text
static/uploads/avatars
static/uploads/courses
static/uploads/common
static/uploads/homework
static/uploads/materials
static/interactive
```

这些目录是：

- 头像
- 课程封面
- 通用图片
- 作业附件
- 课程资料
- 交互式课件资源

### 13.2 课程导入脚本

脚本：`backend/import_course.py`

这个脚本会做几件事：

- 根据 `SOURCE_DIR` 扫描课程源目录
- 清理旧课程文件和旧交互资源
- 清理数据库里该课程旧章节 / 课时数据
- 重新复制 PDF / PPT / 视频等资源
- 重新生成 `static/interactive/manifest.json`
- 清除课程章节缓存

### 13.3 一个必须知道的坑

`import_course.py` 里有一个**硬编码本机路径**：

```python
SOURCE_DIR = "/Users/zhangkailong/Documents/zkl7788/课程资源开发/comfyui/上传到系统的版本/"
```

这意味着：

> **这个脚本在别的机器上直接运行，大概率必挂。**

接手后请优先处理这个问题：

- 要么改成环境变量
- 要么改成命令行参数
- 要么至少在 README 里明确运行前必须手改

当前阶段如果只是临时使用，请先手工改 `SOURCE_DIR`。

### 13.4 资源导入命令

```bash
# 进入后端容器
docker exec -it teaching-backend bash

# 进入应用目录
cd /app

# 修改 import_course.py 中的 SOURCE_DIR
# 然后执行
python import_course.py
```

如果你是在本机直跑后端，也可以：

```bash
cd backend
source .venv/bin/activate
python import_course.py
```

---

## 14. 账号初始化与日常管理命令

### 14.1 创建教师账号（推荐用整合脚本）

```bash
docker exec -it teaching-backend python /app/create_teacher.py
```

支持交互式输入。

### 14.2 批量导入教师账号

```bash
# 先导出模板（如果脚本支持）
docker exec -it teaching-backend python /app/create_teacher.py --template

# 将 Excel 复制进容器
docker cp teachers_template.xlsx teaching-backend:/app/teachers_template.xlsx

# 批量导入
docker exec -it teaching-backend python /app/create_teacher.py --file /app/teachers_template.xlsx
```

Excel 关键列：

| 列名 | 说明 |
|---|---|
| `username` | 登录账号，一般手机号 |
| `password` | 初始密码 |
| `full_name` | 教师姓名 |
| `course_ids` | 授权课程 ID，多个用逗号分隔 |

### 14.3 创建学生 / 普通用户

```bash
docker exec -it teaching-backend python /app/create_user.py
```

### 14.4 查看课程列表 / 数据库内容

```bash
# 进入 MySQL
docker exec -it teaching-mysql mysql -uroot -pteaching2024 teaching_platform
```

或者本机客户端连接：

```bash
mysql -h 127.0.0.1 -P 13306 -uroot -pteaching2024 teaching_platform
```

---

## 15. 日常运维命令（建议收藏）

### 15.1 查看容器状态

```bash
docker ps
docker compose ps
```

### 15.2 看日志

```bash
# 后端
docker logs -f teaching-backend

# 前端 / Nginx
docker logs -f teaching-frontend

# MySQL
docker logs -f teaching-mysql

# Redis
docker logs -f teaching-redis
```

### 15.3 进入容器

```bash
docker exec -it teaching-backend bash
docker exec -it teaching-mysql bash
docker exec -it teaching-redis sh
```

### 15.4 重建服务

```bash
# 重新构建并启动
docker compose up -d --build

# 仅重建后端
docker compose up -d --build backend

# 仅重建前端
docker compose up -d --build frontend
```

### 15.5 清理并重启（谨慎）

```bash
docker compose down
```

如果你还执行带 `-v` 的删除，会把数据库卷也清掉，请务必慎用：

```bash
# 非必要不要执行
# docker compose down -v
```

---

## 16. 本地调试建议（非常实用）

### 16.1 改前端页面

```bash
cd frontend
npm install
npm run dev
```

重点文件常在：

- `frontend/src/views/`
- `frontend/src/components/`
- `frontend/src/stores/`
- `frontend/src/utils/request.ts`

### 16.2 改后端接口

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

重点文件常在：

- `backend/app/api/v1/endpoints/`
- `backend/app/models/`
- `backend/app/schemas/`
- `backend/app/core/`

### 16.3 联调优先级建议

如果你不知道先查前端还是后端，按这个顺序：

1. 浏览器控制台 Network
2. 前端请求 baseURL 是否对
3. Swagger 能否直接请求成功
4. 后端日志是否报错
5. 数据库是否有数据
6. Redis 是否异常

---

## 17. 测试、校验与建议执行命令

### 17.1 后端测试

仓库当前有一部分后端测试，主要集中在联邦 SSO / 辅助逻辑：

```bash
cd backend
source .venv/bin/activate
pytest
```

如果本机没有 `pytest`，需要自行安装（当前 `requirements.txt` 中未显式看到 pytest）。

### 17.2 前端构建校验

```bash
cd frontend
npm install
npm run build
```

### 17.3 建议交接后第一时间补充的校验动作

接手后建议补充以下标准化命令：

- 前端 lint
- 前端 typecheck
- 后端 pytest 固化
- 数据库迁移机制（目前是 `Base.metadata.create_all` 风格，更偏开发态）

当前代码里：

- 前端 `package.json` 只有 `dev / build / preview`
- 没有看到现成的 lint / test script
- 后端是启动即 `create_all`，不算严格的生产迁移方案

---

## 18. 已知注意事项 / 接手风险点

这一节最重要，建议认真看。

### 18.1 仓库里存在环境相关硬编码

已确认的典型例子：

- `frontend/vite.config.ts` 里有旧内网地址 `192.168.150.27`
- `backend/import_course.py` 里有本机绝对路径 `SOURCE_DIR`
- `nginx/nginx.conf` 和后端配置默认写了 `edu.yanzhiedu.cn`
- 任务大厅默认兜底地址使用 `127.0.0.1:3000` / `127.0.0.1:8001`

这意味着：

> 换机器、换环境、换服务器后，**不要以为只改 `.env` 就够了**。

### 18.2 仓库中出现了敏感配置示例

例如：

- 数据库 root 密码
- ComfyUI GPU SSH 账号密码
- 联邦共享密钥占位值

这些内容有的属于示例，有的看起来像真实值。  
**接手生产环境时，强烈建议：**

1. 统一重新梳理真实生产凭据
2. 尽量迁出仓库文件，改为安全配置下发
3. 立即确认这些凭据是否需要轮换

### 18.3 数据库初始化方式偏“开发态”

`backend/app/main.py` 中会直接执行：

```python
Base.metadata.create_all(bind=engine)
```

这在开发环境方便，但长期看更推荐：

- 明确 Alembic 迁移脚本
- 区分开发库和生产库
- 避免表结构变更靠应用启动隐式处理

### 18.4 前端和后端都混有“环境假设”

例如：

- 前端默认认为 API 在某个固定地址
- Nginx 默认认为 GPU 主机是固定域名
- 导入脚本默认认为课程目录挂载在固定位置

所以接手时最好先做一次“环境抽象清理”。

---

## 19. 建议的交接接手动作清单

如果你是新接手的人，建议按以下顺序完成：

### 第一天先做

- [ ] 拉代码并阅读本 README
- [ ] 检查 `backend/.env`、`frontend/.env.*`
- [ ] 用 `docker compose up -d --build` 跑起来
- [ ] 打开首页、Swagger、登录流程
- [ ] 确认 MySQL / Redis 可连通
- [ ] 查看后端日志、前端日志

### 第二步做本地开发验证

- [ ] 本地跑后端
- [ ] 本地跑前端
- [ ] 修正 `vite.config.ts` 中的开发代理地址
- [ ] 验证登录、课程列表、文件访问
- [ ] 验证教师/学生账号创建脚本

### 第三步做生产风险梳理

- [ ] 确认生产域名 / IP / GPU 主机信息
- [ ] 确认 ComfyUI SSH 凭据是否有效
- [ ] 确认课程资源真实挂载路径
- [ ] 确认任务大厅联邦配置是否仍在使用
- [ ] 确认敏感凭据是否需要轮换
- [ ] 确认是否需要补 Alembic / CI / lint / typecheck

---

## 20. 常见问题排查（按现象查）

### Q1：前端页面能开，但接口全 404 / 401 / 连不上

先查：

1. `frontend/.env.development` 是否正确
2. `frontend/vite.config.ts` 是否还指向旧地址
3. 后端是否实际在 `8000` 运行
4. 浏览器里请求打到哪里了

### Q2：Swagger 能开，但前端登录失败

先查：

1. 前端请求 baseURL 是否正确
2. 登录接口返回内容是否符合前端预期
3. 浏览器 localStorage 的 token 是否写入
4. 响应拦截器是否把 401 清掉并跳登录页

### Q3：图片 / 课程封面 / 作业附件加载失败

先查：

1. `VITE_IMG_BASE_URL` 是否配置正确
2. 后端 `/static/uploads/` 目录里是否真有文件
3. Nginx 是否正确代理 `/static/uploads/`
4. 返回给前端的是相对路径还是绝对路径

### Q4：ComfyUI 页面能开，执行工作流一直失败

先查：

1. Redis 队列是否异常
2. 后端 `comfy_proxy` 日志
3. GPU 主机和端口是否可用
4. 用户是否配置了 `comfyui_port`
5. 当前并发数是否已经满了

### Q5：课程导入脚本跑不起来

先查：

1. `SOURCE_DIR` 是否改成当前机器可用路径
2. 目标目录是否有权限
3. 数据库中课程 ID 是否存在
4. 容器内是否能访问对应挂载路径

### Q6：本地后端启动报数据库连接失败

大概率是 `.env` 里还在用 Docker 内部主机名：

- `mysql`
- `redis`

如果你是本机启动代码，应改成：

- `127.0.0.1:13306`
- `127.0.0.1:6380`

---

## 21. 相关文档

仓库里还有一些补充文档，建议按需看：

- `docs/DEPLOYMENT.md`：部署说明（旧版）
- `docs/ADMIN_MANUAL.md`：管理员常用操作（旧版）
- `docs/TEACHING_SYSTEM.md`：较长的技术说明
- `docs/bug_fixes.md`：历史问题记录
- `CLAUDE.md`：开发辅助说明

这份 README 已尽量把交接关键内容统一收拢；如果后续继续维护，建议把其他文档中的重复信息逐步合并，避免多份文档互相冲突。

---

## 22. 最后的交接建议（给接手人）

如果你只有半天时间接这个项目，请至少确认下面 6 件事：

1. **系统能不能完整启动**（Docker）
2. **登录是否正常**（前后端联调）
3. **数据库和 Redis 是否能连接**
4. **课程静态资源是否还在**
5. **ComfyUI 的 GPU 主机和 SSH 凭据是否仍有效**
6. **仓库里的硬编码地址是否需要替换**

如果这 6 件事没有核清楚，这个系统就还不算真正完成交接。

---

## 23. 当前维护建议（可作为后续优化 backlog）

建议后续维护时优先做下面几项：

- [ ] 去掉前端 `vite.config.ts` 里的硬编码地址
- [ ] 把 `import_course.py` 的 `SOURCE_DIR` 改成参数 / 环境变量
- [ ] 补全前端 lint / typecheck / test 命令
- [ ] 补上后端正式迁移方案（如 Alembic）
- [ ] 对敏感配置做安全治理
- [ ] 把部署信息、业务信息、运维信息继续收口到单一文档

---

如无特殊说明，以上内容以当前仓库代码和配置为准。
