# 教学系统部署文档

## 目录

- [1. 环境准备](#1-环境准备)
- [2. 快速部署](#2-快速部署)
- [3. 配置文件参数说明](#3-配置文件参数说明)
  - [3.1 docker-compose.yml](#31-docker-composeyml)
  - [3.2 后端 .env](#32-后端-env)
  - [3.3 Nginx 配置](#33-nginx-配置)
- [4. 服务管理](#4-服务管理)
- [5. 验证部署](#5-验证部署)
- [6. 常见问题](#6-常见问题)

---

## 1. 环境准备

### 1.1 必需软件

| 软件 | 版本要求 | 用途 |
|------|----------|------|
| Docker Desktop | >= 4.0 | 容器编排 |
| Docker Compose | >= 2.0 | 多容器部署 |
| Git | 任意版本 | 版本控制 |

### 1.2 检查 Docker 状态

```bash
# 检查 Docker 是否运行
docker --version
docker-compose --version

# 确认 Docker 服务正常运行
docker ps
```

### 1.3 目录结构

```
2026_teaching_system/
├── backend/                 # 后端代码
│   ├── app/                # FastAPI 应用
│   ├── .env                # 后端环境变量
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端代码
│   ├── src/               # Vue 3 源码
│   └── public/            # 静态资源
├── nginx/                  # Nginx 配置
│   └── nginx.conf         # Nginx 配置文件
├── docker-compose.yml     # Docker Compose 配置
├── Dockerfile.frontend    # 前端构建脚本
├── Dockerfile.backend     # 后端构建脚本
└── docs/                  # 文档目录
```

---

## 2. 快速部署

### 2.1 克隆项目

```bash
git clone <repository-url>
cd 2026_teaching_system
```

### 2.2 配置环境变量

**后端配置** (`backend/.env`)：

```bash
# 复制模板
cp backend/.env.example backend/.env

# 编辑配置（根据需要修改）
vim backend/.env
```

**前端配置** (`frontend/.env.development`)：

```bash
# 开发环境
cp frontend/.env.example frontend/.env.development
```

### 2.3 构建并启动服务

```bash
# 构建所有服务
docker-compose build

# 启动所有服务（后台运行）
docker-compose up -d

# 查看启动状态
docker-compose ps
```

### 2.4 访问系统

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:2026 | 教学系统前端 |
| 后端 API | http://localhost:8000 | API 服务 |
| API 文档 | http://localhost:8000/docs | FastAPI 文档 |

---

## 3. 配置文件参数说明

### 3.1 docker-compose.yml

#### 服务配置

```yaml
version: '3.8'

services:
  # ========== 前端 + Nginx 代理 ==========
  frontend:
    build:
      context: .                    # 构建上下文
      dockerfile: Dockerfile.frontend  # Dockerfile 路径
    container_name: teaching-frontend  # 容器名称
    ports:
      - "2026:80"                  # 映射端口：宿主机:容器
    depends_on:
      - backend                    # 依赖服务
    networks:
      - teaching-network           # 网络配置
    restart: unless-stopped        # 重启策略

  # ========== 后端 API ==========
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: teaching-backend
    ports:
      - "8000:8000"
    environment:                   # 环境变量
      - DATABASE_URL=mysql+pymysql://root:teaching2024@mysql:3306/teaching_platform
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
      - SECRET_KEY=your-secret-key-change-in-production
      - ACCESS_TOKEN_EXPIRE_MINUTES=60
      - COMFY_MAX_CONCURRENT=2    # ComfyUI 最大并发数
      - COMFY_MAX_CONCURRENT_PROD=2
      - COMFY_GPU_HOST=192.168.150.2  # GPU 服务器地址
    depends_on:
      - mysql
      - redis
    volumes:
      - ./backend/static:/app/static  # 挂载静态文件
    networks:
      - teaching-network
    restart: unless-stopped

  # ========== MySQL 数据库 ==========
  mysql:
    image: mysql:8.0
    container_name: teaching-mysql
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=teaching2024  # root 密码
      - MYSQL_DATABASE=teaching_platform  # 数据库名
      - MYSQL_CHARSET=utf8mb4            # 字符集
      - MYSQL_COLLATION=utf8mb4_unicode_ci
    volumes:
      - mysql-data:/var/lib/mysql        # 数据持久化
      - ./teaching_platform.sql:/docker-entrypoint-initdb.d/teaching_platform.sql
    networks:
      - teaching-network
    restart: unless-stopped

  # ========== Redis 缓存 ==========
  redis:
    image: redis:7-alpine
    container_name: teaching-redis
    ports:
      - "6380:6379"
    volumes:
      - redis-data:/data                 # 数据持久化
    networks:
      - teaching-network
    restart: unless-stopped
```

#### 网络配置

```yaml
networks:
  teaching-network:
    driver: bridge    # 桥接网络模式

volumes:
  mysql-data:        # MySQL 数据卷
  redis-data:        # Redis 数据卷
```

#### 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | MySQL 连接字符串 | - |
| `REDIS_HOST` | Redis 主机名 | redis |
| `REDIS_PORT` | Redis 端口 | 6379 |
| `REDIS_DB` | Redis 数据库编号 | 0 |
| `SECRET_KEY` | JWT 密钥 | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间(分钟) | 60 |
| `COMFY_MAX_CONCURRENT` | ComfyUI 最大并发数(开发) | 2 |
| `COMFY_MAX_CONCURRENT_PROD` | ComfyUI 最大并发数(生产) | 10 |
| `COMFY_GPU_HOST` | GPU 服务器地址 | - |

---

### 3.2 后端 .env

#### 基础配置

```bash
# ========== 基础配置 ==========
PROJECT_NAME=TeachingPlatform      # 项目名称
API_V1_STR=/api/v1                 # API 版本前缀
SECRET_KEY=change-this-secret-key-in-production  # JWT 密钥
ACCESS_TOKEN_EXPIRE_MINUTES=60     # Token 过期时间(分钟)
```

#### 数据库配置

```bash
# ========== 数据库配置 ==========
# Docker Compose 环境使用服务名，单独运行使用 localhost
DATABASE_URL=mysql+pymysql://root:teaching2024@mysql:3306/teaching_platform
# 格式: dialect+driver://username:password@host:port/database_name
# - dialect: mysql
# - driver: pymysql
# - username: root
# - password: teaching2024
# - host: mysql (Docker) 或 localhost (本地)
# - port: 3306
# - database: teaching_platform
```

#### Redis 配置

```bash
# ========== Redis 配置 ==========
REDIS_HOST=redis          # Redis 主机
REDIS_PORT=6379           # Redis 端口
REDIS_DB=0                # Redis 数据库编号 (0-15)
REDIS_PASSWORD=           # Redis 密码（无密码为空）
```

#### ComfyUI 队列配置

```bash
# ========== ComfyUI 队列配置 ==========
COMFY_MAX_CONCURRENT=2    # 开发环境最大并发数
COMFY_MAX_CONCURRENT_PROD=10  # 生产环境最大并发数
COMFY_GPU_HOST=192.168.150.2  # GPU 服务器地址
```

---

### 3.3 Nginx 配置

#### Server 配置

```nginx
server {
    listen 80;
    server_name localhost;

    # ========== 前端静态文件 ==========
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # ========== 静态资源 ==========
    location /static/ {
        alias /usr/share/nginx/html/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # ========== API 代理 ==========
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # ========== ComfyUI 代理 ==========
    # URL格式: /comfyui/{username}/{port}/{path}
    location ~ ^/comfyui/([^/]+)/(\d+)(.*)$ {
        set $comfy_port $2;
        set $comfy_path $3;

        proxy_pass http://192.168.150.2:$comfy_port$comfy_path$is_args$args;

        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;

        # 不缓冲
        proxy_buffering off;
        proxy_request_buffering off;

        # 注入队列脚本（只对 HTML 页面）
        sub_filter '</head>'
            '<script src="/static/js/comfyui-queue.js"></script></head>';
        sub_filter_once on;
        sub_filter_types text/html;

        # CORS 头
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";

        if ($request_method = OPTIONS) {
            return 204;
        }
    }
}
```

#### Nginx 参数说明

| 参数 | 说明 |
|------|------|
| `proxy_pass` | 上游服务器地址 |
| `proxy_set_header` | 设置代理请求头 |
| `proxy_connect_timeout` | 连接超时时间 |
| `proxy_send_timeout` | 发送超时时间 |
| `proxy_read_timeout` | 读取超时时间 |
| `proxy_buffering` | 启用代理缓冲 |
| `sub_filter` | 响应内容替换 |

---

## 4. 服务管理

### 4.1 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 启动并查看日志
docker-compose up -d && docker-compose logs -f
```

### 4.2 停止服务

```bash
# 停止所有服务（保留数据卷）
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 4.3 重启服务

```bash
# 重启单个服务
docker-compose restart backend

# 重启所有服务
docker-compose restart
```

### 4.4 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看后端日志
docker-compose logs -f backend

# 查看最近 100 行日志
docker-compose logs --tail=100 backend
```

### 4.5 进入容器

```bash
# 进入后端容器
docker exec -it teaching-backend /bin/bash

# 进入数据库容器
docker exec -it teaching-mysql /bin/bash

# 进入 Redis 容器
docker exec -it teaching-redis redis-cli
```

---

## 5. 验证部署

### 5.1 检查服务状态

```bash
docker-compose ps
```

预期输出：
```
NAME                 STATUS    PORTS
teaching-backend     Up        0.0.0.0:8000->8000/tcp
teaching-frontend    Up        0.0.0.0:2026->80/tcp
teaching-mysql       Up        0.0.0.0:3306->3306/tcp
teaching-redis       Up        0.0.0.0:6380->6379/tcp
```

### 5.2 验证 API 接口

```bash
# 测试后端健康检查
curl http://localhost:8000/health

# 测试队列状态
curl http://localhost:8000/api/v1/comfy_proxy/queue/status

# 预期输出：
# {"queue_length": 0, "processing_count": 0, "max_concurrent": 2, "available_slots": 2}
```

### 5.3 验证前端

打开浏览器访问 http://localhost:2026，确认页面正常加载。

---

## 6. 常见问题

### 6.1 Docker 相关

**Q: Docker 容器无法启动**

```bash
# 查看详细错误
docker-compose logs <service-name>

# 常见原因：端口被占用
netstat -ano | findstr :8000
```

**Q: 构建失败**

```bash
# 清理 Docker 缓存，重新构建
docker-compose build --no-cache
```

### 6.2 数据库相关

**Q: 连接数据库失败**

```bash
# 检查 MySQL 容器状态
docker exec teaching-mysql mysql -u root -pteaching2024 -e "SHOW DATABASES;"
```

**Q: 数据丢失**

检查是否执行了 `docker-compose down -v`，该命令会删除数据卷。

### 6.3 队列相关

**Q: 排队功能不生效**

```bash
# 检查 Redis 连接
docker exec teaching-redis redis-cli ping

# 检查 processing_count 值
docker exec teaching-redis redis-cli GET comfy:processing_count

# 检查队列长度
docker exec teaching-redis redis-cli LLEN comfy:queue
```

**Q: processing_count 异常（负数）**

```bash
# 重置 processing_count
docker exec teaching-redis redis-cli SET comfy:processing_count 0

# 清空队列
docker exec teaching-redis redis-cli DEL comfy:queue
```

### 6.4 性能相关

**Q: 前端加载缓慢**

```bash
# 检查 Nginx 配置的静态文件路径
# 确保静态文件已正确挂载
ls -la backend/static/
```

---

## 附录：快速参考命令

```bash
# 完整部署流程
git pull
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
docker-compose ps

# 查看服务状态
docker-compose ps

# 查看后端日志
docker-compose logs -f backend

# 重启单个服务
docker-compose restart backend

# 进入后端容器
docker exec -it teaching-backend //bin//bash

# 检查 Redis
docker exec teaching-redis redis-cli

# 测试 API
curl http://localhost:8000/api/v1/comfy_proxy/queue/status
```
