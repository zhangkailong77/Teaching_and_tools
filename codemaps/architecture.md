# 系统架构概览

> 生成时间：2026-01-30

## 一、技术栈总览

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 前端框架 | Vue 3 + TypeScript | Composition API |
| 构建工具 | Vite | 开发服务器与打包 |
| UI 组件库 | Element Plus | 表单、表格、弹窗 |
| 状态管理 | Pinia | 用户认证状态 |
| 后端框架 | FastAPI | 异步 SQLAlchemy |
| 数据库 | MySQL 8.0 | 主数据存储 |
| 缓存层 | Redis 7 | API 缓存、队列状态 |
| 认证方式 | JWT | Token 鉴权 |

## 二、系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │ 教师端 SPA │  │ 学生端 SPA │  │ 登录页    │               │
│  └─────┬─────┘  └─────┬─────┘  └───────────┘               │
└────────┼──────────────┼─────────────────────────────────────┘
         │              │
         └────────┬─────┘
                  │ HTTPS
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     Nginx 反向代理                           │
│              (教学系统：ai.yz-cube.com)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   前端容器   │  │  后端容器   │  │   Redis     │
│ teaching-   │  │ teaching-   │  │ teaching-   │
│  frontend   │  │  backend    │  │   redis     │
│   :2026     │  │   :8000     │  │   :6379     │
└─────────────┘  └──────┬──────┘  └─────────────┘
                        │
                        ▼
               ┌────────────────┐
               │     MySQL      │
               │ teaching-      │
               │   mysql:3306   │
               └────────────────┘
```

## 三、前后端交互模式

### 3.1 请求流程

```
浏览器 → Nginx (:80/443) → 后端容器 (:8000) → MySQL/Redis
         ↘ 前端静态资源 (:2026)
```

### 3.2 API 版本策略

- 所有接口位于 `/api/v1/` 路径下
- 路由前缀通过 `app/core/config.py` 中 `api_v1_str` 配置
- 各模块路由在 `app/api/v1/api.py` 中汇总

### 3.3 认证流程

```
登录 → POST /api/v1/auth/login → 返回 JWT Token
请求 → Header: Authorization: Bearer <token>
验证 → 后端 deps.py 中 get_current_user 解析 Token
```

## 四、模块划分

### 4.1 后端模块

| 模块 | 路径 | 功能描述 |
|------|------|---------|
| 认证模块 | `endpoints/auth.py` | 登录、注册、Token 刷新 |
| 用户模块 | `endpoints/users.py` | 用户信息管理 |
| 课程模块 | `endpoints/course.py` | 班级、学生、选课管理 |
| 内容模块 | `endpoints/content.py` | 课程资源、章节、作业模板 |
| 作业模块 | `endpoints/homework.py` | 作业发布、提交、批改 |
| 考试模块 | `endpoints/exam.py` | 题库、试卷、考试、阅卷 |
| 公告模块 | `endpoints/announcement.py` | 师生公告发布与查看 |
| 档案模块 | `endpoints/profile.py` | 教师/学生档案管理 |
| 上传模块 | `endpoints/upload.py` | 头像、封面图片上传 |
| 练习模块 | `endpoints/practice.py` | 实训环境管理 |
| ComfyUI | `endpoints/comfy_proxy.py` | AI 绘画队列代理 |

### 4.2 前端模块

| 模块 | 路径 | 功能描述 |
|------|------|---------|
| 登录页 | `views/login/` | 用户登录入口 |
| 教师端 | `views/dashboard/teacher/` | 班级管理、学生管理、作业批改 |
| 学生端 | `views/dashboard/student/` | 我的课程、作业提交、考试 |
| 共享组件 | `components/` | 侧边栏、作业抽屉、公告组件 |

## 五、数据流向

### 5.1 课程数据流

```
管理员导入课程 → courses 表 → course_chapters 表 → course_lessons 表
       ↓                    ↓                    ↓
  teacher_course_access  (缓存 5 分钟)        (文件存储)
       ↓
教师创建班级 → class_course_bindings 表
       ↓
学生加入班级 → enrollments 表
```

### 5.2 作业数据流

```
课程模板作业 → course_tasks 表
       ↓
班级作业实例 → class_assignments 表 (引用 origin_task_id)
       ↓
学生提交 → student_submissions 表
       ↓
教师批改 → 更新 score、feedback、annotations
```

## 六、缓存策略

| 缓存对象 | Key 格式 | 过期时间 | 清除时机 |
|---------|---------|---------|---------|
| 课程章节 | `course:{id}:chapters` | 5 分钟 | import_course.py 执行后 |
| 教师班级列表 | `teacher:{id}:classes:{status}` | 30 分钟 | 班级操作后 |
| 学生列表 | `teacher:{id}:students:{class_id}:{keyword}:{page}` | 10 分钟 | 学生操作后 |
| 教师统计 | `teacher:{id}:homework_stats` | 10 分钟 | 批改作业后 |

## 七、外部服务依赖

| 服务 | 地址 | 用途 |
|------|------|------|
| ComfyUI GPU | 120.41.127.61:22 | AI 绘画任务执行 |
| 图片存储 | `/static/uploads/` | 头像、封面、作业附件 |
