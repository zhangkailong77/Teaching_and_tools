# 前端架构详解

> 生成时间：2026-01-30

## 一、目录结构

```
frontend/
├── src/
│   ├── main.ts              # 应用入口
│   ├── App.vue              # 根组件
│   ├── router/index.ts      # Vue Router 配置
│   ├── stores/modules/      # Pinia 状态管理
│   ├── utils/
│   │   ├── request.ts       # Axios 封装
│   │   └── index.ts         # 工具函数
│   ├── api/                 # API 服务层
│   ├── components/          # 共享组件
│   └── views/dashboard/     # 页面视图
│       ├── teacher/         # 教师端页面
│       └── student/         # 学生端页面
├── public/
├── index.html
└── package.json
```

## 二、核心文件说明

### 2.1 入口文件

| 文件 | 功能描述 |
|------|---------|
| `main.ts` | 初始化 Vue 应用、Router、Pinia |
| `App.vue` | 根组件，处理路由视图渲染 |
| `router/index.ts` | 路由配置，角色权限守卫 |

### 2.2 路由配置（router/index.ts）

```typescript
// 路由守卫逻辑
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})
```

### 2.3 请求封装（utils/request.ts）

- 基于 Axios 封装
- 自动携带 JWT Token
- 统一错误处理
- 响应拦截器处理状态码

## 三、页面视图结构

### 3.1 教师端（views/dashboard/teacher/）

| 文件 | 路由 | 功能 |
|------|------|------|
| `index.vue` | `/dashboard/teacher` | 教师工作台、统计、创建班级 |
| `classes.vue` | `/dashboard/teacher/classes` | 班级列表管理 |
| `students.vue` | `/dashboard/teacher/students` | 学生名单管理 |
| `courses.vue` | `/dashboard/teacher/courses` | 课程资源库展示 |
| `detail.vue` | `/dashboard/teacher/courses/:id` | 课程章节管理 |
| `homeworksManager.vue` | `/dashboard/teacher/homeworks` | 作业发布管理 |
| `homeworksGrading.vue` | `/dashboard/teacher/grading` | 作业批改 |
| `exams/index.vue` | `/dashboard/teacher/exams` | 考试管理 |
| `exams/components/*` | - | 试卷编辑、题库、阅卷等组件 |

### 3.2 学生端（views/dashboard/student/）

| 文件 | 路由 | 功能 |
|------|------|------|
| `index.vue` | `/dashboard/student` | 学生工作台 |
| `my-class.vue` | `/dashboard/student/my-class` | 我的班级 |
| `course-detail.vue` | `/dashboard/student/courses/:id` | 课程学习页 |
| `homeworks.vue` | `/dashboard/student/homeworks` | 我的作业 |
| `exams/index.vue` | `/dashboard/student/exams` | 考试列表 |
| `exams/take.vue` | `/dashboard/student/exams/:id/take` | 在线考试 |
| `exams/analysis.vue` | `/dashboard/student/exams/:id/analysis` | 考试成绩 |
| `messages/index.vue` | `/dashboard/student/messages` | 消息通知 |

### 3.3 登录页（views/login/）

| 文件 | 路由 | 功能 |
|------|------|------|
| `index.vue` | `/login` | 用户登录 |

## 四、共享组件（components/）

| 组件 | 功能描述 |
|------|---------|
| `TeacherSidebar.vue` | 教师端侧边导航 |
| `StudentSidebar.vue` | 学生端侧边导航 |
| `HomeworkDrawer.vue` | 作业提交/批改抽屉 |
| `CustomHomeworkDrawer.vue` | 自定义作业抽屉 |
| `AssignmentStats.vue` | 作业统计卡片 |
| `SettingsModal.vue` | 设置弹窗 |
| `AnnouncementWidget.vue` | 公告组件 |
| `AnnouncementDetailDrawer.vue` | 公告详情抽屉 |

## 五、API 服务层（api/）

| 文件 | 对应后端模块 |
|------|-------------|
| `auth.ts` | /auth |
| `course.ts` | /classes |
| `content.ts` | /content |
| `homework.ts` | /homeworks |
| `exam.ts` | /exam |
| `announcement.ts` | /announcements |
| `profile.ts` | /profiles |
| `common.ts` | /upload |

## 六、状态管理（stores/modules/user.ts）

```typescript
// 用户状态
interface UserState {
  token: string | null
  userInfo: UserInfo | null
  role: 'student' | 'teacher' | null
}

// Actions
login(credentials) → 设置 token 和 userInfo
logout() → 清除状态，跳转登录
```

## 七、类型定义

### 7.1 课程相关类型（api/content.ts）

```typescript
interface CourseItem {
  id: number
  name: string
  cover?: string
  intro?: string
  is_locked: boolean      // 是否未授权
  public_id: string       // 加密 ID
}

interface CourseChapterItem {
  id: number
  title: string
  isOpen: boolean
  lessons: CourseLessonItem[]
}

interface CourseLessonItem {
  id: number
  title: string
  type: string           // pdf, video, ppt
  file_url: string
  status: number         // 0:未开始, 1:进行中, 2:已完成
  assignment?: { ... }   // 作业信息
}
```

### 7.2 班级相关类型（api/course.ts）

```typescript
interface ClassItem {
  id: number
  name: string
  description?: string
  cover_image?: string
  student_count: number
  course_count: number
  status: number
}
```

## 八、样式规范

- 使用 SCSS 预处理器
- 组件级样式使用 `scoped`
- 主色调：`#00c9a7`（青色）
- 背景色：`#f5f6fa`（浅灰）
- 字体：Inter、sans-serif

## 九、开发规范

### 9.1 API 函数命名

```typescript
// 获取列表
export function getXxxList() { ... }

// 获取详情
export function getXxxDetail(id: string) { ... }

// 创建
export function createXxx(data) { ... }

// 更新
export function updateXxx(id, data) { ... }

// 删除
export function deleteXxx(id) { ... }
```

### 9.2 组件导入顺序

1. Vue 核心（ref、onMounted 等）
2. Vue Router
3. Pinia Store
4. API 函数
5. 组件
6. 工具函数

### 9.3 响应式数据初始化

```typescript
// 推荐：明确类型
const courseList = ref<CourseItem[]>([])

// 不推荐：隐式 any
const courseList = ref([])
```
