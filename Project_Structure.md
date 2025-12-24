backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # APP 初始化入口
│   ├── api/                     # API 路由层
│   │   ├── __init__.py
│   │   └── v1/                  # 版本控制 v1
│   │       ├── __init__.py
│   │       ├── api.py           # 路由汇总
│   │       └── endpoints/       # 具体业务接口
│   │           ├── __init__.py
│   │           ├── auth.py      # 登录/认证接口
│   │           └── users.py     # 用户管理接口
│   ├── core/                    # 核心配置与安全
│   │   ├── __init__.py
│   │   ├── config.py            # 环境变量配置 (Pydantic Settings)
│   │   └── security.py          # JWT 和 密码加密逻辑
│   ├── db/                      # 数据库相关
│   │   ├── __init__.py
│   │   ├── base.py              # 导入所有 Model 供 Alembic 使用
│   │   └── session.py           # 数据库 Session 管理
│   ├── models/                  # ORM 模型 (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── class_model.py
│   └── schemas/                 # 数据传输模型 (Pydantic)
│       ├── __init__.py
│       ├── token.py
│       └── user.py
├── .env                         # 环境变量文件 (不上传git)
└── requirements.txt



frontend/
├── tsconfig.json            # 【TS配置】TypeScript 配置文件
├── vite.config.ts           # 【Vite配置】使用 TS 编写的配置
├── package.json
├── index.html
├── env.d.ts                 # 【类型声明】Vite 注入的环境变量类型声明
│
└── src/
    ├── main.ts              # 【入口】注意是 .ts 后缀
    ├── App.vue
    │
    ├── api/                 # 【API 层】
    │   ├── auth.ts          # 登录接口定义 (定义请求参数 interface)
    │   └── user.ts          # 用户接口定义
    │
    ├── types/               # 【类型定义】(新增) 存放全局通用的 TS 接口/类型
    │   ├── api.d.ts         # 后端通用响应结构 (如 code, msg, data)
    │   └── user.d.ts        # 用户模型定义 (User, LoginParams)
    │
    ├── utils/               # 【工具层】
    │   ├── request.ts       # Axios 封装 (泛型支持，推导返回类型)
    │   └── storage.ts       # 本地存储封装 (强类型)
    │
    ├── stores/              # 【状态层】
    │   ├── index.ts
    │   └── modules/
    │       └── user.ts      # Pinia Store (定义 State 的 Interface)
    │
    ├── router/              # 【路由层】
    │   ├── index.ts         # 路由定义 (RouteRecordRaw 类型)
    │   └── permission.ts    # 路由守卫
    │
    ├── views/               # 【视图层】
    │   ├── login/
    │   │   └── index.vue    # <script setup lang="ts">
    │   └── error/
    │       └── 404.vue
    │
    └── styles/
        └── index.scss