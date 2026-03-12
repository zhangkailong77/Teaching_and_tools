# 教学系统技术文档

## 1 系统概述

### 1.1 项目简介

本教学系统是一个基于 Vue 3 和 FastAPI 构建的现代化在线教育平台，支持角色化访问控制（教师/学生），提供完整的课程管理、作业提交与批改、考试系统、消息通知以及 ComfyUI 实训环境等功能。系统采用 Docker 容器化部署，通过 Nginx 实现前端静态资源服务和后端 API 反向代理，同时集成了 GPU 服务器上的 ComfyUI 工作流执行环境。

系统的核心设计理念是将教学管理与 AI 实训环境深度融合，教师可以发布课程、布置作业、组织考试，学生可以在线学习、提交作业、参加考试，并能在实训环境中使用 ComfyUI 进行 AI 绘画创作。所有用户操作都经过 JWT 认证，确保数据安全与访问权限控制。

### 1.2 技术栈架构

系统采用前后端分离架构，整体技术栈如下所述。

后端技术栈以 Python 3.10+ 为运行环境，使用 FastAPI 作为 Web 框架，该框架原生支持异步编程，能够高效处理大量并发请求。数据库层面采用 MySQL 8.0 存储核心业务数据，使用 SQLAlchemy ORM 进行对象关系映射，简化数据库操作。缓存层使用 Redis 7.0，提供会话缓存、作业统计缓存以及 ComfyUI 队列状态存储等功能。认证方面采用 JWT（JSON Web Token）机制，支持 Token 过期自动刷新和用户角色验证。异步任务处理通过 Python 原生 asyncio 实现，结合 httpx 库进行 HTTP 客户端请求。

前端技术栈基于 Vue 3 框架，采用 Composition API 和 TypeScript 进行开发，确保类型安全和代码可维护性。构建工具使用 Vite 4.0，提供极速的开发体验和优化的生产构建。UI 组件库选用 Element Plus，提供丰富的表单、表格、弹窗等组件。状态管理采用 Pinia 框架，替代 Vuex 成为 Vue 3 官方推荐的状态管理方案。路由管理使用 Vue Router 4.0，支持嵌套路由和路由守卫。

部署层面采用 Docker Compose 进行容器编排，核心服务包括 Nginx（反向代理和静态资源服务）、MySQL（数据持久化）、Redis（缓存和队列）以及自定义的前后端服务镜像。

### 1.3 目录结构

```
2026_teaching_system/
├── backend/                          # 后端项目目录
│   ├── app/                          # FastAPI 应用主目录
│   │   ├── api/v1/endpoints/         # API 路由处理器
│   │   │   ├── auth.py               # 认证相关接口
│   │   │   ├── users.py              # 用户管理接口
│   │   │   ├── course.py             # 课程管理接口
│   │   │   ├── homework.py           # 作业管理接口
│   │   │   ├── exam.py               # 考试管理接口
│   │   │   ├── content.py            # 内容管理接口
│   │   │   ├── announcement.py       # 公告管理接口
│   │   │   ├── practice.py           # 实训管理接口
│   │   │   ├── upload.py             # 文件上传接口
│   │   │   └── comfy_proxy.py        # ComfyUI 代理接口
│   │   ├── core/                     # 核心配置模块
│   │   │   ├── config.py             # 应用配置
│   │   │   ├── security.py           # 安全相关（密码加密等）
│   │   │   └── redis.py              # Redis 操作封装
│   │   ├── models/                   # SQLAlchemy 数据模型
│   │   │   ├── user.py               # 用户模型
│   │   │   ├── course.py             # 课程模型
│   │   │   ├── class_model.py        # 班级模型
│   │   │   ├── content.py            # 内容模型
│   │   │   ├── exam.py               # 考试模型
│   │   │   ├── announcement.py       # 公告模型
│   │   │   └── profile.py            # 用户档案模型
│   │   ├── schemas/                  # Pydantic 数据模式
│   │   ├── db/                       # 数据库相关
│   │   │   ├── base_class.py         # 基础类
│   │   │   └── session.py            # 数据库会话
│   │   ├── api/api.py                # API 路由汇总
│   │   └── main.py                   # 应用入口
│   ├── static/                       # 静态文件目录
│   ├── requirements.txt              # Python 依赖
│   └── Dockerfile.backend            # 后端 Docker 镜像构建文件
│
├── frontend/                         # 前端项目目录
│   ├── src/                         # Vue 源码目录
│   │   ├── views/                   # 页面视图组件
│   │   │   ├── login/               # 登录页面
│   │   │   ├── dashboard/student/   # 学生端页面
│   │   │   └── dashboard/teacher/   # 教师端页面
│   │   ├── components/              # 公共组件
│   │   ├── api/                     # API 服务层
│   │   ├── stores/                  # Pinia 状态管理
│   │   ├── router/                  # 路由配置
│   │   └── App.vue                  # 根组件
│   ├── public/static/js/            # 公共静态 JS
│   │   └── comfyui-queue.js         # ComfyUI 队列拦截脚本
│   ├── Dockerfile.frontend          # 前端 Docker 镜像构建文件
│   └── package.json                 # NPM 依赖配置
│
├── nginx/                            # Nginx 配置目录
│   └── nginx.conf                   # Nginx 主配置文件
│
├── docs/                             # 文档目录
│   └── TEACHING_SYSTEM.md           # 本技术文档
│
├── docker-compose.yml               # Docker Compose 编排文件
└── README.md                        # 项目说明文件
```

## 2 功能模块说明

### 2.1 前端模块

前端采用 Vue 3 + TypeScript 开发，通过 Element Plus 组件库构建用户界面。整个前端应用按角色分为学生端和教师端两个主要分支，通过路由守卫实现访问控制。

学生端功能模块涵盖以下方面。首页仪表盘展示学生的课程概览、待办作业数量、最近考试等信息。课程学习页面提供课程列表查看、课程详情浏览、教学内容（PPT、PDF 等）在线预览功能。作业中心列出所有待完成作业，支持富文本编辑器提交作业内容，包含图片上传功能。考试系统提供在线考试入口，包含答题计时、题目导航、答案暂存（使用 Redis）、成绩查询等功能。消息中心用于接收教师发布的公告和系统通知。ComfyUI 实训室是系统的特色功能，学生可以在内嵌的 ComfyUI 界面中进行 AI 绘画创作，系统自动处理排队和并发控制。

教师端功能模块同样丰富。首页仪表盘展示教师所负责的班级概况、学生数量统计、作业批改统计等信息。课程管理支持创建、编辑、删除课程，发布课程公告，上传教学资料（PPT、PDF、视频等）。作业管理支持发布作业、设置截止时间、查看提交情况、对学生作业进行评分和反馈。考试管理提供创建考试、录入题库、组卷、自动判卷（支持客观题）和成绩分析功能。学生管理展示所有学生名单，支持查看学生详细信息。班级管理支持创建班级、添加学生、管理班级成员。

前端核心组件包括以下几类。HomeworkDrawer 组件提供作业提交和查看的抽屉式交互界面，支持富文本编辑和图片预览。CustomHomeworkDrawer 组件是 HomeworkDrawer 的增强版本，支持更复杂的作业批注功能。教师侧边栏（TeacherSidebar）和学生侧边栏（StudentSidebar）分别根据不同角色提供导航菜单。AssignmentStats 组件展示作业统计图表，帮助教师快速了解作业完成情况。

### 2.2 后端模块

后端基于 FastAPI 框架构建，采用 RESTful API 设计规范，所有接口均返回统一的 JSON 格式响应结构。应用启动时自动创建数据库表（开发环境）或通过 Alembic 迁移（生产环境）。

认证模块（auth.py）负责用户登录、Token 生成与验证、密码加密（使用 BCrypt 算法）等功能。登录接口接收用户名和密码，验证通过后生成 JWT Token 返回给前端，后续请求通过 Authorization Header 携带 Token 进行身份验证。模块还支持 Token 刷新和强制下线等功能。

用户模块（users.py）提供用户信息的查询和更新接口。普通用户可以查看和修改自己的基本信息，管理员（教师角色）可以查看所有用户列表。用户的 ComfyUI 端口（comfyui_port）字段用于标识用户在 GPU 服务器上运行的 ComfyUI 实例。

课程模块（course.py）处理课程信息的 CRUD 操作，包括课程创建、班级分配、学生选课等功能。课程与班级是多对多关系，一个课程可以分配给多个班级，一个班级可以学习多门课程。

作业模块（homework.py）是系统的核心功能之一。教师发布作业时需要指定作业标题、内容、截止时间、所属班级等信息。学生在截止日期前可以提交作业，系统支持多次提交覆盖旧版本。作业提交后状态变为"待批改"，教师批改后状态更新为"已批改"或"已打回"。

考试模块（exam.py）提供完整的考试管理功能。教师可以创建考试、录入题目、组卷、发布考试。学生参加考试时，系统会自动记录答题进度到 Redis（考试暂存功能），即使页面刷新也不会丢失答题数据。考试结束后系统自动判卷并计算成绩。

内容模块（content.py）管理教学资料的存储和访问，支持 PPT、PDF、视频等文件格式。文件上传接口（upload.py）提供图片、文档等文件的上传功能，上传的文件存储在 static/uploads 目录下。

公告模块（announcement.py）实现系统公告的发布和查看功能。教师可以发布面向班级或全局的公告，学生可以在消息中心查看公告内容。

ComfyUI 代理模块（comfy_proxy.py）是系统的重要功能模块，将在第三章详细说明。

### 2.3 数据库模块

数据库使用 MySQL 8.0，采用 InnoDB 存储引擎，支持事务和外键约束。SQLAlchemy ORM 负责数据库建模和操作，所有模型类都继承自 Base 类。

核心数据模型包括以下几类。

User 模型（user.py）是用户基础信息表，包含 id（主键）、username（用户名，唯一索引）、hashed_password（加密密码）、role（角色：student/teacher）、is_active（激活状态）、created_at（创建时间）、last_login（最后登录时间）、comfyui_port（ComfyUI 端口，唯一索引）、full_name（真实姓名）、student_number（学号）等字段。用户与教师档案、学生档案、班级、选课记录、作业提交记录之间存在关联关系。

Class 模型（class_model.py）表示班级信息，包含 id、name（班级名称）、teacher_id（班主任 ID，外键关联 User）、created_at 等字段。一个班级属于一位教师，一位教师可以管理多个班级。

Course 模型（content.py）表示课程信息，包含 id、title（课程标题）、description（课程描述）、cover_image（封面图片）等字段。课程与班级通过关联表实现多对多关系。

ClassAssignment 模型（course.py）表示作业信息，包含 id、class_id（班级 ID）、course_id（课程 ID）、title（作业标题）、content（作业内容）、deadline（截止时间）、status（状态：草稿/已发布）、created_at 等字段。

StudentSubmission 模型（course.py）表示学生提交的作业，包含 id、assignment_id（作业 ID）、student_id（学生 ID）、content（提交内容）、status（状态：待批改/已批改/已打回）、submitted_at（提交时间）、graded_at（批改时间）、score（分数）、feedback（教师评语）等字段。

Exam 和 Question 模型（exam.py）表示考试和题目信息，支持单选题、多选题、判断题、填空题、简答题等多种题型。

Announcement 模型（announcement.py）表示系统公告，包含 id、title、content、publisher_id、target_type（面向对象：个人/班级/全体）、created_at 等字段。

### 2.4 Redis 缓存模块

Redis 在系统中承担多重职责，包括会话缓存、数据缓存、ComfyUI 队列状态存储等。

基础缓存操作封装在 redis.py 文件中，提供了 get_cache、set_cache、delete_cache、delete_cache_pattern 等通用方法。缓存键采用命名空间设计，避免不同功能模块之间的键冲突。

考试暂存功能使用 Redis Hash 结构存储学生的答题进度。键的命名格式为 `exam_progress:{exam_id}:{student_id}`，field 命名格式为 `q_{question_id}`，value 存储题目答案。这种设计支持高效的单题保存和批量读取操作，且设置了 24 小时过期时间以保护考试数据。

用户信息缓存采用简单的 String 结构，键名为 `user:{username}`，存储用户基本信息的 JSON 序列化数据，过期时间设为 1 小时。每次用户请求时首先尝试从缓存读取，缓存未命中才查询数据库。

作业统计缓存用于缓存教师的作业统计数据，避免每次请求都进行复杂的数据库联表查询。缓存键名格式为 `teacher:{teacher_id}:homework_stats`，当作业状态发生变化时通过 delete_cache_pattern 批量清除相关缓存。

## 3 ComfyUI 排队机制

### 3.1 机制概述

ComfyUI 是基于节点的 AI 绘画界面，用户通过连接不同的节点构建图像生成工作流。由于 GPU 计算资源有限，系统实现了排队机制来控制并发执行的工作流数量。当同时提交的工作流数量超过限制时，后续请求会自动进入排队队列等待执行。

排队机制的核心设计目标包括以下几个方面。首先是资源限制，通过设置最大并发数（默认测试环境 2 个，生产环境 10 个）确保 GPU 资源不会被过度使用。其次是公平排队，采用先来先服务（FIFO）的队列策略，确保所有用户的请求按提交顺序执行。第三是状态透明，用户可以实时查看自己在队列中的位置和任务执行状态。第四是优雅降级，当 ComfyUI 服务器不可用时，系统能够正确处理异常并通知用户。

整个排队机制由后端 API、前端拦截脚本、Nginx 代理三个组件协同实现。后端 API 负责接收工作流请求、执行实际的 ComfyUI 调用、管理队列状态；前端拦截脚本负责捕获用户的工作流执行请求并转发到后端 API，同时展示排队状态；Nginx 负责将 ComfyUI 页面请求代理到 GPU 服务器，并通过 sub_filter 注入前端拦截脚本。

### 3.2 后端排队逻辑

排队逻辑的核心实现位于 backend/app/api/v1/endpoints/comfy_proxy.py 文件中。以下是关键的代码流程分析。

执行入口 API 为 `/api/v1/comfy_proxy/execute`，该接口接收用户提交的 ComfyUI 工作流数据（prompt_data），首先验证用户是否已启动 ComfyUI 实例（通过检查用户的 comfyui_port 字段），然后尝试获取执行槽位。

```python
@router.post("/execute")
async def execute_workflow(
    prompt_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    username = current_user.username
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.comfyui_port:
        raise HTTPException(status_code=404, detail="用户ComfyUI未启动，请先启动实训环境")

    port = user.comfyui_port
    comfy_url = f"http://{settings.comfy_gpu_host}:{port}/prompt"

    max_concurrent = get_comfy_max_concurrent()
    processing_count = get_comfy_processing_count()

    # 使用原子操作尝试获取执行槽位
    if not try_acquire_slot():
        # 槽位已满，加入队列
        task_id = enqueue_to_comfy_queue(username, prompt_data, port)
        queue_position = get_comfy_queue_position(task_id)
        return {
            "status": "queued",
            "task_id": task_id,
            "position": queue_position,
            "max_concurrent": max_concurrent,
            "message": f"系统繁忙，前方还有 {queue_position} 人排队"
        }

    # 获取槽位成功，直接执行
    return await execute_workflow_direct(comfy_url, prompt_data, username)
```

槽位获取使用 Redis 原子操作，通过 Lua 脚本确保并发安全。

```python
def try_acquire_slot() -> bool:
    """
    原子性地尝试获取一个执行槽位
    返回 True 表示获取成功，可以执行
    返回 False 表示槽位已满，需要排队
    """
    max_concurrent = get_comfy_max_concurrent()
    lua_script = """
    local current = tonumber(redis.call('GET', KEYS[1]) or '0')
    local max = tonumber(ARGV[1])
    if current < max then
        redis.call('INCR', KEYS[1])
        return 1
    else
        return 0
    end
    """
    result = redis_client.eval(lua_script, 1, "comfy:processing_count", max_concurrent)
    return result == 1
```

当槽位已满时，任务被加入 Redis 队列。队列使用 Redis List 结构，实现 FIFO 存储。

```python
def enqueue_to_comfy_queue(username: str, prompt_data: dict, port: int) -> str:
    """将工作流任务加入队列，返回 task_id"""
    task_id = f"comfy:task:{username}:{int(time.time()*1000)}"
    task_data = {
        "task_id": task_id,
        "username": username,
        "port": port,
        "prompt_data": prompt_data,
        "status": "queued",
        "created_at": datetime.now().isoformat()
    }
    redis_client.rpush("comfy:queue", json.dumps(task_data))
    redis_client.set(f"comfy:task:{task_id}", json.dumps(task_data), ex=3600)
    return task_id
```

直接执行工作流时，系统会同步等待 ComfyUI 完成工作流并返回结果。执行完成后会递减处理计数，并触发处理队列中的下一个任务。

```python
async def execute_workflow_direct(comfy_url, prompt_data, username, task_id=None):
    """直接执行 ComfyUI 工作流（同步等待完成）"""
    async with httpx.AsyncClient(timeout=600.0) as client:
        # 1. 提交工作流
        response = await client.post(comfy_url, json=prompt_data)
        prompt_result = response.json()
        prompt_id = prompt_result.get("prompt_id")

        # 2. 轮询等待工作流完成
        while True:
            await asyncio.sleep(1.0)
            history_response = await client.get(history_url)
            history = history_response.json()
            if prompt_id in history and history[prompt_id].get("outputs"):
                # 任务完成
                return {"status": "completed", "result": prompt_result, "prompt_id": prompt_id}
    # finally 块中递减计数并处理下一个任务
```

后台任务处理器（process_next_task）在每次任务完成时被调用，负责从队列中取出下一个任务并执行。

```python
async def process_next_task():
    """处理队列中的下一个任务（后台异步执行）"""
    max_concurrent = get_comfy_max_concurrent()
    processing_count = get_comfy_processing_count()

    if processing_count >= max_concurrent:
        return  # 没有空位

    if not try_acquire_slot():
        return  # 获取失败

    task = pop_comfy_queue()
    if not task:
        decr_comfy_processing_count()
        return

    # 更新状态并执行
    update_comfy_task_status(task_id, "processing")
    await execute_workflow_direct(comfy_url, prompt_data, username, task_id)
```

### 3.3 前端拦截脚本

前端拦截脚本（comfyui-queue.js）是一个立即执行函数表达式（IIFE），在页面加载时自动运行。它通过重写 window.fetch 函数来拦截所有 POST /prompt 请求（即用户点击"执行"按钮时触发的请求），将请求转发到教学系统的后端 API，而不是直接发送到 ComfyUI 服务器。

拦截逻辑的核心代码如下。

```javascript
(function() {
    const originalFetch = window.fetch;

    window.fetch = function(url, options) {
        // 只拦截 POST /prompt 请求（工作流执行）
        const isPromptRequest =
            typeof url === 'string' &&
            (url.endsWith('/prompt') || url === '/prompt') &&
            options &&
            options.method === 'POST';

        if (!isPromptRequest) {
            // 非 /prompt 请求，直接发送原始请求
            return originalFetch(url, options);
        }

        // 转发到教学系统后端代理 API
        const proxyUrl = `${CONFIG.API_BASE_URL}/comfy_proxy/execute`;

        return originalFetch(proxyUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
            body: options.body
        })
        .then(async response => {
            const data = await response.json();

            if (data.status === 'queued') {
                // 进入排队
                currentTaskId = data.task_id;
                startPolling(data.task_id);
                return new Response(JSON.stringify({
                    prompt_id: `queue_${data.task_id}`,
                    number: Math.floor(Math.random() * 1000000),
                    queue_info: data
                }), { status: 200, headers: { 'Content-Type': 'application/json' } });
            } else if (data.status === 'completed') {
                // 直接执行完成
                return new Response(JSON.stringify({
                    prompt_id: data.result?.prompt_id || `completed_${Date.now()}`,
                    number: data.result?.number || 0
                }), { status: 200 });
            }
        });
    };
})();
```

轮询机制用于实时获取任务状态。脚本使用 setInterval 每 2 秒查询一次后端的任务状态 API，根据返回的状态（queued/processing/completed/failed）更新用户界面。

```javascript
function startPolling(taskId) {
    pollTimer = setInterval(() => {
        pollTaskStatus(taskId);
    }, CONFIG.POLL_INTERVAL);  // 2000ms
}

async function pollTaskStatus(taskId) {
    const response = await originalFetch(`${CONFIG.API_BASE_URL}/comfy_proxy/status/${taskId}`);
    const data = await response.json();

    if (data.status === 'queued') {
        // 仍在排队，更新显示
        console.log(`前方还有 ${data.position} 人`);
    } else if (data.status === 'processing') {
        // 开始处理
        stopPolling();
        showProcessingNotification();
    } else if (data.status === 'completed') {
        // 完成
        stopPolling();
        hideAllNotifications();
        showNotification('success', '工作流执行完成！');
    } else if (data.status === 'failed') {
        // 失败
        stopPolling();
        showNotification('error', '执行失败: ' + (data.result?.error || '未知错误'));
    }
}
```

用户界面通过浮层通知展示排队状态。排队通知显示当前排队位置、最大并发数和进度条；处理中通知显示加载动画；完成通知显示成功图标和提示信息。所有通知都通过动态创建 DOM 元素实现，样式直接注入到页面中。

### 3.4 Nginx 代理配置

Nginx 在 ComfyUI 访问流程中承担代理和脚本注入的职责。当用户访问 `/comfyui/{username}/{port}/` 路径时，Nginx 将请求转发到 GPU 服务器上的 ComfyUI 实例，同时通过 sub_filter 指令将前端拦截脚本注入到 ComfyUI 返回的 HTML 页面中。

Nginx 配置的关键部分如下。

```nginx
location ~ ^/comfyui/([^/]+)/(\d+)(.*)$ {
    set $comfy_port $2;

    # 从原始请求 URI 中提取路径（保留编码）
    if ($request_uri ~* "^/comfyui/[^/]+/[0-9]+(.*)$") {
        set $raw_path $1;
    }

    # 转发请求到 GPU 服务器
    proxy_pass http://192.168.150.2:$comfy_port$raw_path;

    # WebSocket 支持
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # 超时设置（ComfyUI 执行可能耗时较长）
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;

    # 禁用缓冲
    proxy_buffering off;
    proxy_request_buffering off;

    # 注入队列脚本
    sub_filter '</head>' '<script src="/static/js/comfyui-queue.js"></script></head>';
    sub_filter_once on;
    sub_filter_types text/html;
}
```

配置要点说明如下。正则表达式 `^/comfyui/([^/]+)/(\d+)(.*)$` 用于捕获用户名和端口，提取剩余路径部分。关键技巧是从 `$request_uri`（原始请求 URI）中提取 `$raw_path`，因为 `$3` 已经被 URL 解码，可能导致特殊字符（如 `+`）处理不正确。WebSocket 支持对 ComfyUI 的实时通信至关重要，Nginx 必须正确处理 Upgrade 请求头。禁用缓冲确保流式响应能够实时传递给前端。sub_filter 指令将脚本注入到 HTML 的 `</head>` 标签前，使拦截脚本能够在页面加载时执行。

## 4 API 接口说明

### 4.1 认证接口

认证模块提供用户登录、Token 刷新、Token 验证等接口。所有接口位于 `/api/v1/auth/` 路径下。

登录接口路径为 `POST /api/v1/auth/login`，请求体包含 username（字符串）和 password（字符串），响应返回 access_token（JWT Token）和 token_type（Bearer）。该接口验证用户凭据，生成 JWT Token，有效期由 `ACCESS_TOKEN_EXPIRE_MINUTES` 环境变量配置（默认 60 分钟）。

Token 刷新接口路径为 `POST /api/v1/auth/refresh`，请求头携带旧 Token，响应返回新的 access_token。用于 Token 即将过期时自动续期，避免用户重新登录。

### 4.2 用户接口

用户管理接口位于 `/api/v1/users/` 路径下。

获取当前用户信息接口路径为 `GET /api/v1/users/me`，响应返回当前登录用户的完整信息，包括 id、username、role、full_name、student_number、comfyui_port 等字段。

更新用户信息接口路径为 `PUT /api/v1/users/me`，请求体包含要更新的字段，响应返回更新后的用户信息。学生可以更新自己的真实姓名和学号。

### 4.3 课程接口

课程管理接口位于 `/api/v1/course/` 路径下。

获取课程列表接口路径为 `GET /api/v1/course/list`，响应返回当前用户有权访问的所有课程列表。教师看到自己负责的课程，学生看到已选课的课程。

获取课程详情接口路径为 `GET /api/v1/course/{course_id}`，响应返回指定课程的详细信息，包括课程内容、作业列表等。

发布课程接口路径为 `POST /api/v1/course/create`，仅教师可用，请求体包含课程标题、描述、封面等信息。

### 4.4 作业接口

作业管理接口位于 `/api/v1/homework/` 路径下。

提交作业接口路径为 `POST /api/v1/homework/{assignment_id}/submit`，学生专用。请求体包含 content（富文本内容），系统检查截止时间后保存提交记录，支持多次提交覆盖旧版本。

获取我的作业待办列表接口路径为 `GET /api/v1/homework/my-todos`，学生专用。返回当前学生所有待完成作业列表，包含作业状态（已提交/未提交/已批改）和截止时间信息。结果会被缓存到 Redis 以提高响应速度。

### 4.5 考试接口

考试管理接口位于 `/api/v1/exam/` 路径下。

获取考试列表接口路径为 `GET /api/v1/exam/list`，根据用户角色返回相应考试列表。教师看到自己创建的所有考试，学生看到可以参加的考试。

开始考试接口路径为 `POST /api/v1/exam/{exam_id}/start`，学生专用。创建考试记录，返回考试题目列表。考试过程中的答题数据实时保存到 Redis。

提交答案接口路径为 `POST /api/v1/exam/{exam_id}/answer`，学生专用。保存单题答案到 Redis，考试过程中可以刷新页面继续作答。

提交试卷接口路径为 `POST /api/v1/exam/{exam_id}/submit`，学生专用。标记考试完成，触发自动判卷逻辑，计算成绩并保存到数据库。

### 4.6 ComfyUI 代理接口

ComfyUI 代理接口是系统的特色功能模块，所有接口位于 `/api/v1/comfy_proxy/` 路径下。

执行工作流接口路径为 `POST /api/v1/comfy_proxy/execute`。这是排队机制的核心入口，请求体为 ComfyUI 工作流数据（prompt JSON），响应根据情况返回以下内容之一：如果获取到执行槽位，返回执行结果（status: completed）；如果需要排队，返回排队信息（status: queued，包含 task_id、position、max_concurrent）。

查询任务状态接口路径为 `GET /api/v1/comfy_proxy/status/{task_id}`。参数为 task_id（路径参数），响应返回任务当前状态，包括 queued（排队中，额外返回 position）、processing（处理中）、completed（已完成，返回 result）、failed（失败，返回 error）。

获取队列状态接口路径为 `GET /api/v1/comfy_proxy/queue/status`。返回当前队列的整体状态，包含 queue_length（排队人数）、processing_count（正在执行人数）、max_concurrent（最大并发数）、available_slots（可用槽位）。

测试执行接口路径为 `POST /api/v1/comfy_proxy/test/execute`。仅用于测试的接口，不实际调用 ComfyUI，而是模拟执行指定时长后自动完成，用于验证排队逻辑是否正常工作。

重置队列接口路径为 `POST /api/v1/comfy_proxy/test/reset`。仅用于测试的接口，清空队列和计数，用于测试场景的队列状态重置。

获取 ComfyUI 页面接口路径为 `GET /api/v1/comfy_proxy/view/{username}`。代理获取 ComfyUI 首页 HTML，注入认证信息和 fetch 拦截脚本，返回处理后的 HTML 供 iframe 内嵌使用。

代理 API 接口路径为 `GET/POST /api/v1/comfy_proxy/view/{username}/{path:path}`。代理转发 ComfyUI 的所有 API 请求和静态资源请求到 GPU 服务器，添加 JWT 认证头，解决跨域和认证问题。

## 5 手动测试流程

### 5.1 测试环境准备

测试前需要确保所有服务正常运行。使用 Docker Compose 启动所有服务，执行命令 `docker-compose up -d`，然后检查各服务状态。

```bash
# 检查容器运行状态
docker-compose ps

# 查看后端日志
docker logs teaching-backend -f

# 查看 Redis 容器
docker exec -it teaching-redis redis-cli
```

确认以下服务已启动并正常运行。teaching-frontend 服务监听 2026 端口，Nginx 已正确配置。teaching-backend 服务监听 8000 端口，FastAPI 应用已启动。teaching-mysql 服务监听 3306 端口，数据库已初始化。teaching-redis 服务监听 6380 端口，Redis 已就绪。

使用浏览器访问 `http://localhost:2026`，确认前端页面可以正常加载。点击登录页面，使用测试账号（教师账号 teacher1，学生账号 student1）登录系统。

### 5.2 测试排队机制

测试排队机制需要模拟多个并发请求，以下是详细测试步骤。

第一步是测试直接执行。登录学生账号，进入 ComfyUI 实训页面。点击"执行"按钮运行一个简单工作流（如基础文本到图像）。观察浏览器控制台日志，确认请求被正确拦截并转发。首次执行应该直接完成，控制台显示 completed 日志。记录从点击到完成的时间作为基准。

第二步是测试排队逻辑。打开两个浏览器窗口（或使用无痕模式），分别登录两个不同的学生账号。在账号 A 提交一个执行时间较长的工作流（如高分辨率图像生成，预计耗时 30 秒以上）。在账号 B 立即提交另一个工作流。账号 B 应该收到排队响应，浏览器右上角显示排队通知。排队通知应显示"前方还有 1 人排队"。

第三步是验证后台处理。等待账号 A 的工作流完成（观察浏览器日志显示 completed）。观察账号 B 的状态变化：排队中 -> 开始处理 -> 执行完成。在账号 A 执行期间，尝试登录账号 C 提交工作流，账号 C 应该排在账号 B 之后。确认队列顺序符合 FIFO 原则。

第四步是验证队列状态 API。在后端服务器上执行以下命令获取队列状态。

```bash
# 获取队列状态
curl http://localhost:8000/api/v1/comfy_proxy/queue/status

# 返回示例
{
    "queue_length": 2,
    "processing_count": 1,
    "max_concurrent": 2,
    "available_slots": 1
}
```

第五步是测试异常处理。在账号执行工作流时，人工取消（如果支持）。验证任务失败后槽位被正确释放，后续排队任务能够继续执行。检查 Redis 中的队列状态是否正确更新。

### 5.3 使用测试 API

系统提供了专用的测试接口，方便验证排队逻辑而不需要实际运行 ComfyUI 工作流。

使用测试执行接口前，先重置队列状态。

```bash
curl -X POST http://localhost:8000/api/v1/comfy_proxy/test/reset \
  -H "Authorization: Bearer <teacher_token>"
```

然后启动一个长时间模拟执行任务。

```bash
curl -X POST "http://localhost:8000/api/v1/comfy_proxy/test/execute?mock_delay=30" \
  -H "Authorization: Bearer <student1_token>"
```

响应示例。

```json
{
    "status": "processing",
    "message": "开始模拟执行，将在 30 秒后完成",
    "mock_delay": 30,
    "processing_count": 1,
    "max_concurrent": 2
}
```

快速切换账号提交第二个请求，验证排队。

```bash
curl -X POST "http://localhost:8000/api/v1/comfy_proxy/test/execute?mock_delay=5" \
  -H "Authorization: Bearer <student2_token>"
```

响应应该显示排队状态。

```json
{
    "status": "queued",
    "task_id": "comfy:task:student2:1737999999999",
    "position": 1,
    "queue_length": 1,
    "max_concurrent": 2,
    "processing_count": 1,
    "message": "系统繁忙，前方还有 1 人排队"
}
```

查询排队任务状态。

```bash
curl http://localhost:8000/api/v1/comfy_proxy/status/<task_id> \
  -H "Authorization: Bearer <student2_token>"
```

### 5.4 Redis 状态验证

在测试过程中，可以通过 Redis CLI 直接查看队列状态。

```bash
# 进入 Redis 容器
docker exec -it teaching-redis redis-cli

# 查看队列长度
LLEN comfy:queue

# 查看队列中的所有任务
LRANGE comfy:queue 0 -1

# 查看正在执行的任务数
GET comfy:processing_count

# 查看特定任务的状态
GET "comfy:task:<task_id>"

# 删除队列（谨慎使用）
DEL comfy:queue
DEL comfy:processing_count
```

### 5.5 日志分析

通过分析后端日志可以了解排队机制的执行情况。

```bash
# 查看后端日志，过滤 ComfyUI 相关内容
docker logs teaching-backend 2>&1 | grep "ComfyUI Queue"
```

关键日志条目说明如下。`[ComfyUI Queue] 用户 xxx 请求执行工作流，当前并发: 1/2` 表示收到执行请求。`[ComfyUI Queue] 用户 xxx 进入队列，位置: 1` 表示请求进入排队。`[ComfyUI Queue] 从队列取出任务: xxx` 表示后台任务处理器开始处理排队任务。`[ComfyUI Queue] 工作流执行完成: xxx` 表示工作流执行成功。

## 6 部署配置

### 6.1 Docker Compose 配置

系统使用 Docker Compose 进行容器编排，核心配置如下。

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: teaching-frontend
    ports:
      - "2026:80"
    depends_on:
      - backend
    networks:
      - teaching-network
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: teaching-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://root:teaching2024@mysql:3306/teaching_platform
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
      - SECRET_KEY=your-secret-key-change-in-production
      - ACCESS_TOKEN_EXPIRE_MINUTES=60
      - COMFY_MAX_CONCURRENT=2
      - COMFY_MAX_CONCURRENT_PROD=2
      - COMFY_GPU_HOST=192.168.150.2
    depends_on:
      - mysql
      - redis
    volumes:
      - ./backend/static:/app/static
    networks:
      - teaching-network
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    container_name: teaching-mysql
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=teaching2024
      - MYSQL_DATABASE=teaching_platform
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - teaching-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: teaching-redis
    ports:
      - "6380:6379"
    volumes:
      - redis-data:/data
    networks:
      - teaching-network
    restart: unless-stopped

networks:
  teaching-network:
    driver: bridge

volumes:
  mysql-data:
  redis-data:
```

### 6.2 环境变量配置

后端支持通过 .env 文件或环境变量配置，以下是主要配置项说明。

数据库配置项包括 DATABASE_URL（MySQL 连接字符串，格式 mysql+pymysql://user:password@host:port/database）和相关认证信息。

Redis 配置项包括 REDIS_HOST（Redis 服务器地址）、REDIS_PORT（Redis 端口）、REDIS_DB（数据库编号，默认 0）、REDIS_PASSWORD（密码，可选）。

认证配置项包括 SECRET_KEY（JWT 密钥，生产环境必须修改）、ACCESS_TOKEN_EXPIRE_MINUTES（Token 有效期，默认 60 分钟）。

ComfyUI 队列配置项包括 COMFY_MAX_CONCURRENT（测试环境最大并发数，默认 2）、COMFY_MAX_CONCURRENT_PROD（生产环境最大并发数）、COMFY_GPU_HOST（GPU 服务器地址，用于 ComfyUI 代理）。

### 6.3 Nginx 配置

Nginx 作为前端入口和反向代理，核心配置包括静态资源服务、API 代理和 ComfyUI 代理三个部分。

静态资源服务部分将所有请求指向前端构建产物，支持 Vue Router 的 History 模式（通过 try_files 指令）。

API 代理部分将 `/api/` 路径的请求转发到后端服务（teaching-backend:8000），并设置必要的代理头（Host、X-Real-IP 等）。

ComfyUI 代理部分是系统的关键配置，使用正则表达式匹配用户访问路径，从 `$request_uri` 提取原始编码路径，转发到 GPU 服务器，并注入前端拦截脚本。

## 7 常见问题

### 7.1 队列相关问题

问题一：用户提交工作流后一直显示排队中。排查步骤包括以下内容。首先检查 Redis 是否正常运行（`docker exec teaching-redis redis-cli ping` 应返回 PONG）。然后检查 `comfy:processing_count` 的值是否正确（`GET comfy:processing_count`）。最后检查队列中是否有任务（`LLEN comfy:queue`），如果有任务说明后台任务处理器可能没有正确执行。

问题二：槽位获取失败，try_acquire_slot 总是返回 False。可能的原因包括 `comfy:processing_count` 的值被错误设置超过了最大值。解决方案是重置队列（`POST /api/v1/comfy_proxy/test/reset`）或手动设置 Redis 值（`SET comfy:processing_count 0`）。

问题三：前端拦截脚本未生效。可能的原因包括脚本路径不正确、sub_filter 未正确注入、脚本加载顺序问题。解决方案是检查浏览器开发者工具的网络标签页确认脚本是否加载成功，检查控制台是否有脚本错误输出，确认 Nginx 配置中 sub_filter_types 包含 text/html。

### 7.2 认证相关问题

问题一：Token 过期后请求返回 401。前端应实现 Token 自动刷新机制，或在检测到 401 后跳转到登录页面重新登录。用户也可以手动刷新 Token（如果实现了刷新接口）。

问题二：iframe 内嵌 ComfyUI 时认证失败。由于 iframe 请求不会自动携带 Cookie 或 Authorization 头，系统采用多源认证策略：优先从 URL 参数获取 token，其次从请求头获取，最后从 Cookie 获取。如果仍然无法认证，检查后端的 `get_current_user_optional` 函数实现。

### 7.3 性能相关问题

问题一：页面加载缓慢。可能的解决方案包括启用 Redis 缓存（目前部分接口已实现）、使用 CDN 加速静态资源、优化数据库查询（添加必要的索引）、考虑使用 uvicorn 的 workers 参数启用多进程。

问题二：ComfyUI 执行超时。默认超时设置为 10 分钟（600 秒），如果工作流需要更长时间，可以在 `execute_workflow_direct` 函数中调整 httpx.Timeout 参数。但需要注意，过长的超时时间会增加服务器资源占用。

## 8 附录

### 8.1 关键文件索引

| 文件路径 | 说明 |
|---------|------|
| backend/app/main.py | FastAPI 应用入口 |
| backend/app/api/v1/endpoints/comfy_proxy.py | ComfyUI 代理和排队逻辑 |
| backend/app/core/redis.py | Redis 操作封装 |
| backend/app/core/config.py | 应用配置 |
| backend/app/api/deps.py | 依赖注入（认证、会话） |
| frontend/public/static/js/comfyui-queue.js | 前端排队拦截脚本 |
| nginx/nginx.conf | Nginx 配置 |
| docker-compose.yml | Docker Compose 编排 |

### 8.2 Redis 键命名规范

| 键名模式 | 类型 | 说明 |
|---------|------|------|
| user:{username} | String | 用户信息缓存 |
| exam_progress:{exam_id}:{student_id} | Hash | 考试答题暂存 |
| teacher:{teacher_id}:homework_stats | String | 作业统计缓存 |
| comfy:queue | List | ComfyUI 任务队列 |
| comfy:processing_count | String | 正在执行的任务数 |
| comfy:task:{task_id} | String | 单个任务状态 |

### 8.3 API 响应格式

所有 API 成功响应遵循统一格式。

```json
{
    "success": true,
    "data": { ... },
    "meta": {
        "total": 100,
        "page": 1,
        "limit": 20
    }
}
```

错误响应格式如下。

```json
{
    "success": false,
    "error": "错误描述信息",
    "detail": "详细错误信息（可选）"
}
```

本文档最后更新于 2026 年 1 月。
