# 项目进度记录 (CHANGELOG)

记录教学系统的重要功能更新和修改。

---

## 2026-02-10 - ComfyUI 课程资料抽屉交互优化

### 📝 功能概述
优化 ComfyUI 界面右侧课程资料抽屉的交互体验，实现抽屉打开时仍可操作 ComfyUI 节点，并新增 PDF 拖拽阅读功能。

### ✨ 新增功能
- 抽屉打开时不会阻止底层 ComfyUI 的操作（移除遮罩层拦截）
- PDF 支持鼠标拖拽移动，方便阅读放大后的内容
- 阅读模式工具栏右上角添加关闭按钮（X）

### 🐛 修复问题
- 修复 PDF 放大时工具栏被推到右边的问题
- 修复 PDF 放大后左边区域被截断无法拖拽的问题
- 修复默认 100% 时 PDF 不居中显示的问题

### 🔧 技术实现

#### 抽屉容器 pointer-events 设置
```typescript
// 打开抽屉时强制设置遮罩层不拦截点击事件
const modal = document.querySelector('.el-modal-drawer, .course-drawer-modal');
if (modal) {
  (modal as HTMLElement).style.pointerEvents = 'none';
}
```

#### PDF 拖拽功能
```typescript
// 拖拽状态管理
const isDragging = ref(false);
const dragStartX = ref(0);
const dragStartY = ref(0);
const scrollLeft = ref(0);
const scrollTop = ref(0);

// 拖拽事件处理
const onPdfMouseDown = (e: MouseEvent) => {
  isDragging.value = true;
  dragStartX.value = e.clientX - pdfScrollRef.value.offsetLeft;
  dragStartY.value = e.clientY - pdfScrollRef.value.offsetTop;
  // ...
};
```

#### CSS 样式优化
```scss
// 抽屉遮罩层不拦截点击
.el-modal-drawer,
.course-drawer-modal {
  pointer-events: none !important;
}

// PDF 容器优化布局
.read-content {
  min-width: 0;          // 防止 flex 子元素溢出
  overflow: hidden;      // 防止内容溢出影响工具栏

  .read-toolbar {
    min-width: 100%;     // 确保工具栏不被压缩
  }
}

// PDF 默认居中，放大后可正常滚动
.read-stage {
  align-items: flex-start;  // 左对齐避免左边被截断

  .pdf-canvas {
    margin: 0 auto;         // 默认水平居中
  }
}
```

### 📦 修改的文件
| 文件 | 修改内容 |
|------|----------|
| `frontend/src/views/dashboard/student/comfyui/index.vue` | 抽屉交互优化、PDF 拖拽功能、样式修复 |

### 🎯 改进效果
- ✅ 抽屉打开时可边看课程资料边操作 ComfyUI 节点
- ✅ PDF 放大后可通过拖拽查看任意区域
- ✅ 工具栏始终保持在可点击位置
- ✅ PDF 默认居中显示，放大后左右均可正常滚动
- ✅ 阅读模式可直接关闭抽屉

---

## 2026-02-10 - ComfyUI GPU 服务器使用 DDNS 域名

### 📝 功能概述
将 GPU 服务器的硬编码公网 IP 地址替换为 DDNS 动态域名，解决公网 IP 变化时需要手动更新配置的问题。

### ✨ 改进内容
- 所有 ComfyUI 请求使用 DDNS 域名 `edu.yanzhiedu.cn` 代替固定 IP
- 添加 DNS 解析器配置，支持动态 DNS 解析
- 无需手动更新配置，DDNS 自动跟随 IP 变化

### 🔧 技术实现

#### 后端配置
- 环境变量 `COMFY_GPU_HOST` 改为 `edu.yanzhiedu.cn`
- `config.py` 默认值更新为域名
- `comfy_runner.py` SSH 连接使用域名

#### Nginx 配置
- 添加 DNS resolver 指令：`resolver 8.8.8.8 8.8.4.4 valid=60s`
- 所有 `proxy_pass` 指令使用域名
- 支持动态 DNS 解析，自动刷新

#### 前端配置
- 开发环境 Vite 代理 target 改为域名
- ComfyUI 直接访问 URL 使用域名

### 📦 修改的文件
| 文件 | 修改内容 |
|------|----------|
| `docker-compose.yml` | `COMFY_GPU_HOST=edu.yanzhiedu.cn` |
| `nginx/nginx.conf` | 添加 DNS resolver，更新 proxy_pass |
| `nginx/comfyui_proxy.conf` | 更新所有 proxy_pass 为域名 |
| `backend/app/core/config.py` | 默认值改为域名 |
| `backend/app/utils/comfy_runner.py` | 默认值改为域名 |
| `backend/app/api/v1/endpoints/practice.py` | direct_url 改为域名 |
| `backend/app/api/v1/endpoints/comfy_proxy.py` | 更新注释 |
| `frontend/src/views/dashboard/student/comfyui/index.vue` | 开发环境 URL 改为域名 |
| `frontend/vite.config.ts` | ComfyUI 代理 target 改为域名 |
| `backend/.env.example` | 更新配置说明 |
| `backend/.env` | 更新为域名 |
| `backend/.env.local` | 更新为域名 |
| `backend/.env.temp` | 更新为域名，保留旧配置为注释 |

### 🎯 影响范围
- ✅ SSH 连接（启动/停止 ComfyUI）
- ✅ HTTP 请求（工作流提交、状态查询）
- ✅ Nginx 反向代理（前端访问）
- ✅ 排队机制（无影响，使用 Redis）

### 🧪 测试验证
- Docker 日志显示请求正确使用域名：`http://edu.yanzhiedu.cn:8189`
- 工作流提交和执行正常
- 排队机制工作正常

### 📝 注意事项
- 教学平台服务器 IP（192.168.150.27）保持不变
- 部署后需要重启 Docker 服务

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
