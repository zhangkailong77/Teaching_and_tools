# 数据模型与 schemas

> 生成时间：2026-01-30

## 一、核心实体关系图

```
User (用户)
├── TeacherProfile (教师档案)
├── StudentProfile (学生档案)
├── Class (教学的班级) ←──┐
│   ├── Enrollment (学生选课) ←── Student
│   ├── ClassCourseBinding (班级课程绑定) ←── Course
│   └── ClassAssignment (班级作业实例)
│       └── StudentSubmission (学生提交)
├── Course (课程资源包) ──┐
│   ├── CourseChapter (章节)
│   │   └── CourseLesson (课时)
│   └── CourseTask (作业模板)
└── TeacherCourseAccess (教师课程授权)
```

## 二、数据库模型（models/）

### 2.1 用户模型（user.py）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String(50) | 登录账号（手机号） |
| hashed_password | String(100) | BCrypt 加密密码 |
| role | String(20) | student / teacher |
| is_active | Boolean | 账户状态 |
| created_at | DateTime | 注册时间 |
| last_login | DateTime | 最后登录 |
| full_name | String(50) | 真实姓名 |
| student_number | String(30) | 学号 |
| comfyui_port | Integer | ComfyUI 端口 |

**关联关系：**
- `teacher_profile` → TeacherProfile（一对一）
- `teaching_classes` → Class（反向）
- `enrollments` → Enrollment（反向）
- `submissions` → StudentSubmission（反向）

### 2.2 班级模型（course.py）

**Class（班级）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 班级名称 |
| description | Text | 班级描述 |
| teacher_id | Integer | 所属教师（FK） |
| cover_image | String(255) | 封面图 |
| start_date | DateTime | 开课日期 |
| end_date | DateTime | 结课日期 |
| status | Integer | 状态（0:进行中, 1:已结束） |

**Enrollment（选课关联）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| class_id | Integer | 班级 ID（FK） |
| student_id | Integer | 学生 ID（FK） |
| joined_at | DateTime | 加入时间 |

**ClassAssignment（班级作业实例）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| class_id | Integer | 班级 ID（FK） |
| origin_task_id | Integer | 模板来源 ID（FK，可空） |
| title | String(255) | 作业标题 |
| content | Text | 作业内容 |
| deadline | DateTime | 截止时间 |
| status | Integer | 状态（0:待发布, 1:进行中, 2:已截止） |
| max_score | Integer | 满分（默认 100） |

**StudentSubmission（学生提交）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| assignment_id | Integer | 作业 ID（FK） |
| student_id | Integer | 学生 ID（FK） |
| content | Text | 提交内容（富文本 HTML） |
| score | Integer | 分数 |
| feedback | Text | 教师评语 |
| status | Integer | 状态（0:已提交, 1:已批改, 2:被打回） |
| submitted_at | DateTime | 提交时间 |
| graded_at | DateTime | 批改时间 |
| annotations | JSON | 批注数据 |

### 2.3 内容模型（content.py）

**Course（课程资源包）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 课程名称 |
| cover | String(255) | 封面图 |
| intro | Text | 简介 |
| task_count | Integer | 作业数量 |
| total_duration | Integer | 总时长 |
| lesson_count | Integer | 课时数 |
| course_type | String(50) | 课程类型 |

**CourseChapter（章节）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| course_id | Integer | 所属课程（FK） |
| title | String(255) | 章节标题 |
| sort_order | Integer | 排序 |

**CourseLesson（课时）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| chapter_id | Integer | 所属章节（FK） |
| title | String(255) | 课时标题 |
| resource_type | String(20) | 资源类型（pdf/ppt/video） |
| file_url | String(500) | 文件路径 |
| duration | String(50) | 时长/页数 |
| is_free | Boolean | 是否试看 |
| sort_order | Integer | 排序 |

**TeacherCourseAccess（教师课程授权）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| teacher_id | Integer | 教师 ID（FK） |
| course_id | Integer | 课程 ID（FK） |
| created_at | DateTime | 授权时间 |

**ClassCourseBinding（班级课程绑定）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| class_id | Integer | 班级 ID（FK） |
| course_id | Integer | 课程 ID（FK） |
| bound_at | DateTime | 绑定时间 |

**StudentLearningProgress（学习进度）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| student_id | Integer | 学生 ID（FK） |
| lesson_id | Integer | 课时 ID（FK） |
| status | Integer | 状态（0:未开始, 1:进行中, 2:已完成） |
| last_position | Integer | 最后阅读位置 |

**CourseTask（作业模板）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| course_id | Integer | 所属课程（FK） |
| lesson_id | Integer | 关联课时（FK，可空） |
| title | String(255) | 作业标题 |
| content | Text | 作业要求 |
| sort_order | Integer | 排序 |

## 三、Schemas（Pydantic 校验）

### 3.1 用户相关（schemas/user.py）

```python
class UserBase(BaseModel):
    username: str
    role: str = "student"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime]
    last_login: Optional[datetime]
    full_name: Optional[str]
```

### 3.2 课程相关（schemas/content.py）

```python
class CourseOut(BaseModel):
    id: int
    name: str
    cover: Optional[str]
    intro: Optional[str]
    task_count: int
    total_duration: int
    lesson_count: int
    course_type: str
    created_at: datetime
    public_id: Optional[str]
    is_locked: bool = False  # 是否未授权
```

### 3.3 作业相关（schemas/homework.py）

```python
class HomeworkSubmit(BaseModel):
    content: str  # 富文本 HTML 或图片 URL

class HomeworkGrade(BaseModel):
    score: int
    feedback: Optional[str]
    annotated_content: Optional[str]
    annotations: Optional[dict]
```

## 四、枚举值说明

### 4.1 角色类型

| 值 | 说明 |
|---|------|
| student | 学生 |
| teacher | 教师 |

### 4.2 学习进度

| 值 | 说明 |
|---|------|
| 0 | 未开始 |
| 1 | 进行中 |
| 2 | 已完成 |

### 4.3 作业状态

| 值 | 说明 |
|---|------|
| 0 | 待发布 |
| 1 | 进行中 |
| 2 | 已截止 |

### 4.4 提交状态

| 值 | 说明 |
|---|------|
| 0 | 已提交/未批改 |
| 1 | 已批改 |
| 2 | 被打回 |

### 4.5 资源类型

| 值 | 说明 |
|---|------|
| pdf | PDF 文档 |
| ppt | PPT 演示文稿 |
| video | 视频 |

## 五、ID 加密策略

系统使用 `encode_id()` 和 `decode_id()` 对外暴露的 ID 进行加密：

```python
# 内部 ID（数据库）
course.id = 1

# 对外 ID（API、URL）
course.public_id = encode_id(1)  # 生成加密字符串
```

作用：防止外部直接遍历 ID 获取数据。
