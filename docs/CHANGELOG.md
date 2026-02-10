# 项目进度记录 (CHANGELOG)

记录教学系统的重要功能更新和修改。

---

## 2026-02-10 - 教师端课程预览功能优化

### 📝 功能概述
优化教师端课程资源预览功能，未授权教师可预览第1章内容，所有课程卡片可见。

### ✨ 新增功能
- 未授权课程可查看第1章详细内容（PDF/PPT/视频可查看）
- 未授权课程可查看所有章节目录标题
- 课件资料和课程视频列表可见，第1章可播放
- 新建班级时课程下拉列表只显示已授权课程

### 🎨 UI调整
- 未授权课程使用蓝色主题（#1565c0）
- 移除所有表情符号图标
- 预览提示靠左对齐
- 移除"开通后查看"按钮，禁用状态显示

### 📦 修改的文件
| 文件 | 修改内容 |
|------|----------|
| `backend/app/api/v1/endpoints/content.py` | 预览章节数配置、章节API返回is_previewable字段 |
| `frontend/src/views/dashboard/teacher/courses.vue` | 课程卡片预览样式、预览课程按钮 |
| `frontend/src/views/dashboard/teacher/detail.vue` | 预览模式提示、课时/课件/视频权限控制 |
| `frontend/src/views/dashboard/teacher/classes.vue` | 新建班级使用getAvailableCourses |
| `frontend/src/api/content.ts` | 添加is_previewable字段 |

---

## 2026-02-10 - 新增课程视频播放功能

### 📝 功能概述
在学生端和教师端的课程详情页面新增"课程视频"功能模块，实现课程视频的在线播放和管理。

### ✨ 新增功能

#### 学生端 (`frontend/src/views/dashboard/student/course-detail.vue`)
- 新增"课程视频" Tab
- 视频播放器（左侧）
  - 简洁风格黑色主题
  - 原生 HTML5 video 控件
  - 自定义倍速控制：0.5x, 1x, 1.25x, 1.5x, 2x
  - 占位状态提示
- 视频列表（右侧）
  - 按章节组织显示
  - 悬停/激活状态效果
  - 播放中指示器
  - 视频时长显示（MM:SS 格式）
- 响应式布局
  - 大屏：左右布局
  - 小屏（<1024px）：上下布局

#### 教师端 (`frontend/src/views/dashboard/teacher/detail.vue`)
- 与学生端相同的视频播放功能
- 保持 UI/UX 一致性

### 🔧 技术实现

#### 前端状态
```typescript
// 视频播放相关状态
const currentVideo = ref<any>(null);     // 当前播放的视频
const videoRef = ref<HTMLVideoElement>(null);
const playbackSpeed = ref(1);              // 播放速度

// 视频章节列表（过滤 type='video' 的课时）
const videoChapterList = computed(() => {
  return chapterList.value
    .map(chapter => ({
      ...chapter,
      lessons: chapter.lessons.filter(l => l.type === 'video')
    }))
    .filter(chapter => chapter.lessons.length > 0);
});
```

#### 核心方法
- `playVideo(video)` - 播放选中的视频
- `setPlaybackSpeed(speed)` - 设置播放速度
- `formatDuration(seconds)` - 格式化视频时长

#### 样式设计
- 品牌色：`#00c9a7`（青绿色）
- 播放器：黑色背景 `#000`，圆角 12px
- 控制栏：深灰色 `#1a1a1a`
- 倍速按钮：激活状态使用品牌色

### 📁 视频文件存储

#### 存放位置
```
backend/static/uploads/materials/course_{课程ID}/chapter_{章节ID}/
├── lesson1.pdf
├── lesson1.pptx
└── lesson1.mp4    ← 视频文件
```

#### 导入方式
使用现有的 `import_course.py` 脚本自动导入：
```bash
cd backend
python import_course.py
```

支持的视频格式：`.mp4`, `.mov`

#### 数据库存储
- 表：`course_lessons`
- 字段：`file_url` 存储路径（如：`/static/uploads/materials/course_1/chapter_1/lesson1.mp4`）
- 字段：`resource_type = 'video'`

### 🎨 UI 设计规范
- **风格**：简洁、现代
- **颜色**：品牌色 #00c9a7
- **交互**：悬停反馈、激活状态高亮
- **无障碍**：清晰的视觉层次和对比度

### 📦 修改的文件
| 文件 | 修改内容 |
|------|----------|
| `frontend/src/views/dashboard/student/course-detail.vue` | 新增视频 Tab、播放器、列表 |
| `frontend/src/views/dashboard/teacher/detail.vue` | 新增视频 Tab、播放器、列表 |

### 🔗 相关文档
- [用户指南](./TEACHING_SYSTEM.md)
- [部署文档](./DEPLOYMENT.md)
- [Bug 修复记录](./bug_fixes.md)

---
