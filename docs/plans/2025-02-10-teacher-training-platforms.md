# 实现计划：教师端工作台添加8个实训入口

**创建日期**: 2026-02-10  
**状态**: 待实现  
**优先级**: MEDIUM

---

## 需求背景

当前系统中：
- **学生端**：有完整的 ComfyUI 页面 (`/dashboard/student/comfyui`)，可以启动和使用 ComfyUI
- **教师端**：没有对应的实训平台入口，无法直接使用 ComfyUI 功能

**业务需求**：
- 系统有8个课程资源，每个课程对应一个实训平台
- 第1门课程对应 ComfyUI（AI 绘图实训）
- 需要在教师工作台提供8个实训平台入口
- 其他7个平台后续扩展

---

## 设计方案

### UI 布局

在教师端工作台的"数据概览卡片"（DashboardStats）下方添加实训平台入口区域：

```
┌─────────────────────────────────────────────────────────┐
│  教师工作台                                    + 创建班级  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ 学生总数    │  │ 执教班级    │  │ 待办事项    │      │
│  │ [图表]      │  │ [班级列表]  │  │ [任务通道]  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│  实训平台入口                                             │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                   │
│  │ComfyUI│ │ 平台2 │ │ 平台3 │ │ 平台4 │                   │
│  │AI绘图 │ │ ???  │ │ ???  │ │ ???  │                   │
│  └──────┘ └──────┘ └──────┘ └──────┘                   │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                   │
│  │ 平台5 │ │ 平台6 │ │ 平台7 │ │ 平台8 │                   │
│  │ ???  │ │ ???  │ │ ???  │ │ ???  │                   │
│  └──────┘ └──────┘ └──────┘ └──────┘                   │
├─────────────────────────────────────────────────────────┤
│  我管理的班级与课程                                       │
│  ...                                                     │
└─────────────────────────────────────────────────────────┘
```

### 卡片设计

**实训入口卡片规格**：
- 布局：4列 × 2行网格
- 尺寸：约 140px × 100px
- 样式：带图标、名称、描述
- 状态：
  - `available`：已实现，正常可点击
  - `coming-soon`：待开发，灰色禁用状态，显示"敬请期待"

### 卡片样式预览

**已实现状态**（ComfyUI）：
```
┌──────────────────────┐
│       🎨             │
│    ComfyUI           │
│   AI 绘图实训         │
│                      │
│   [进入 →]           │
└──────────────────────┘
```
- 白色背景
- 彩色图标
- 可点击跳转
- 悬停上浮效果

**敬请期待状态**（其他平台）：
```
┌──────────────────────┐
│       🔧             │
│      平台2           │
│     敬请期待          │
│                      │
│    [即将上线]         │
└──────────────────────┘
```
- 灰色背景
- 灰色图标
- 禁用状态
- 无悬停效果

---

## 技术实现

### Phase 1: 创建实训平台配置

**文件**: `frontend/src/config/training-platforms.ts`

```typescript
export interface TrainingPlatform {
  id: string;           // 平台ID
  name: string;         // 平台名称
  description: string;  // 描述
  icon: string;         // 图标（emoji或图片URL）
  route?: string;       // 路由路径（已实现）
  status: 'available' | 'coming-soon'; // 状态
  courseKeyword?: string; // 对应课程关键词
}

export const TRAINING_PLATFORMS: TrainingPlatform[] = [
  {
    id: 'comfyui',
    name: 'ComfyUI',
    description: 'AI 绘图实训',
    icon: '🎨',
    route: '/dashboard/teacher/comfyui',
    status: 'available',
    courseKeyword: 'AI'
  },
  {
    id: 'platform2',
    name: '平台2',
    description: '敬请期待',
    icon: '🔧',
    status: 'coming-soon'
  },
  // TODO: 添加其他6个平台
];
```

### Phase 2: 创建实训平台入口组件

**文件**: `frontend/src/views/dashboard/teacher/components/TrainingPlatforms.vue`

**功能**：
- 显示8个实训平台卡片
- 4×2网格布局
- 点击已实现的平台跳转
- 未实现的平台显示禁用状态
- 响应式设计（小屏幕自适应）

**核心代码结构**：
```vue
<template>
  <div class="training-platforms-section">
    <div class="section-header">
      <h3>实训平台入口</h3>
    </div>
    <div class="platforms-grid">
      <div 
        v-for="platform in TRAINING_PLATFORMS" 
        :key="platform.id"
        class="platform-card"
        :class="{ disabled: platform.status === 'coming-soon' }"
        @click="handlePlatformClick(platform)"
      >
        <div class="card-icon">{{ platform.icon }}</div>
        <div class="card-name">{{ platform.name }}</div>
        <div class="card-desc">{{ platform.description }}</div>
        <div class="card-action">
          <span v-if="platform.status === 'available'">进入 →</span>
          <span v-else>即将上线</span>
        </div>
      </div>
    </div>
  </div>
</template>
```

### Phase 3: 集成到工作台

**修改文件**: `frontend/src/views/dashboard/teacher/index.vue`

**位置**: 在 `<DashboardStats>` 下方添加

```vue
<template>
  <!-- ... -->
  <!-- 数据概览卡片 -->
  <DashboardStats :data="stats" />

  <!-- 新增：实训平台入口 -->
  <TrainingPlatforms />

  <!-- 执教课程列表 -->
  <!-- ... -->
</template>

<script setup lang="ts">
import TrainingPlatforms from './components/TrainingPlatforms.vue';
// ...
</script>
```

### Phase 4: 添加教师端 ComfyUI 路由和页面

#### 4.1 添加路由

**修改文件**: `frontend/src/router/index.ts`

```typescript
{
  path: 'teacher/comfyui',
  name: 'TeacherComfyUI',
  component: () => import('@/views/dashboard/teacher/comfyui/index.vue'),
  meta: { requiresAuth: true, role: 'teacher', hideSidebar: true }
}
```

#### 4.2 创建教师端 ComfyUI 页面

**新建文件**: `frontend/src/views/dashboard/teacher/comfyui/index.vue`

**实现方式**：
1. 复制学生端页面代码作为基础
2. 调整差异部分（页面标题等）
3. 保持所有核心功能

**核心功能保持一致**：
- ComfyUI 环境启动
- iframe 嵌入
- 课程资料抽屉
- 排队状态显示
- PDF 拖拽阅读

**可能的调整**：
- 页面标题保持不变或改为"教师实训环境"
- 课程资料加载逻辑（与学生相同或调整）

---

## 文件清单

### 新建文件
- [ ] `frontend/src/config/training-platforms.ts` - 实训平台配置
- [ ] `frontend/src/views/dashboard/teacher/components/TrainingPlatforms.vue` - 实训平台入口组件
- [ ] `frontend/src/views/dashboard/teacher/comfyui/index.vue` - 教师端 ComfyUI 页面

### 修改文件
- [ ] `frontend/src/views/dashboard/teacher/index.vue` - 集成实训平台入口
- [ ] `frontend/src/router/index.ts` - 添加教师 ComfyUI 路由

### 无需修改
- ✅ 后端 API (`practice.py`, `comfy_proxy.py`) - 已支持教师
- ✅ Nginx 配置 - 已支持通用代理
- ✅ Docker 配置 - 无需修改

---

## 复杂度评估

**总体复杂度：LOW-MEDIUM**

| 任务 | 工作量 |
|------|--------|
| 创建配置文件 | 0.5 小时 |
| 创建入口组件 | 1.5 小时 |
| 集成到工作台 | 0.5 小时 |
| 复制 ComfyUI 页面 | 1 小时 |
| 添加路由配置 | 0.5 小时 |
| 样式调整 | 1 小时 |
| 测试验证 | 0.5 小时 |

**总计**: 约 5-6 小时

---

## 待确认问题

### 1. 8个实训平台的具体信息

除了 ComfyUI，其他7个平台的：
- **平台名称**：如 "视频剪辑平台"、"3D建模平台" 等
- **对应课程**：哪些课程需要这些平台？
- **关键词匹配**：用什么关键词关联课程？

### 2. 卡片图标设计

- 使用 emoji 图标（简单，无需额外资源）
- 还是使用自定义图片图标（更美观，需要设计资源）？

### 3. 课程与平台的关联方式

- **关键词匹配**：按课程名称关键词（如 "AI" → ComfyUI）
- **ID 匹配**：按课程 ID 精确匹配
- **权限控制**：教师需要先有对应课程的授权才能使用平台吗？

### 4. 其他实训平台的技术栈

后续7个平台是否需要：
- 独立的后端服务？
- 独立的 GPU 服务器？
- 与 ComfyUI 类似的代理架构？

---

## 后续扩展方向

1. **平台状态管理**：添加平台维护状态、负载状态显示
2. **使用统计**：记录各平台的使用时长、次数
3. **快捷入口**：根据教师教授的课程动态显示相关平台
4. **平台通知**：平台更新、维护公告推送

---

## 相关文档

- [ComfyUI 排队机制分析](../comfyui-queue-feasibility-analysis.md)
- [CHANGELOG](../CHANGELOG.md)
- [部署文档](../DEPLOYMENT.md)
