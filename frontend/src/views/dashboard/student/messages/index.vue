<template>
  <div class="dashboard-container">
    <StudentSidebar />

    <main class="main-content">
      <!-- 头部 -->
      <header class="page-header">
        <div class="header-left">
          <h2>消息通知</h2>
          <p>查看班级公告与系统提醒</p>
        </div>
        <div class="header-right">
          <!-- 筛选 Tab -->
          <div class="filter-tabs">
            <span :class="{ active: filterType === 'all' }" @click="filterType = 'all'">全部</span>
            <span :class="{ active: filterType === 'unread' }" @click="filterType = 'unread'">
              未读 <i v-if="unreadCount > 0" class="badge-dot"></i>
            </span>
          </div>
        </div>
      </header>

      <!-- 消息列表 (Grid 布局) -->
      <div class="msg-grid" v-loading="loading">
        <!-- 空状态 -->
        <div v-if="filteredList.length === 0" class="empty-state">
          <p>暂无相关消息</p>
        </div>

        <!-- 消息卡片 -->
        <div 
          v-else 
          class="msg-card" 
          v-for="item in filteredList" 
          :key="item.id"
          :class="{ 'is-read': item.is_read, 'is-urgent': item.type === 'urgent' }"
          @click="openDetail(item)"
        >
          <div class="card-header">
            <span class="type-tag" :class="item.type">{{ getTypeLabel(item.type) }}</span>
            <span class="time">{{ formatTime(item.created_at) }}</span>
          </div>
          
          <div class="card-body">
            <h3 class="title" :title="item.title">
              <span v-if="!item.is_read" class="dot"></span>
              {{ item.title }}
            </h3>
            <p class="summary">{{ item.content }}</p>
          </div>

          <div class="card-footer">
            <div class="publisher">
              <el-icon><User /></el-icon> {{ item.publisher_name }}
            </div>
            <div class="status">
              <span v-if="!item.is_read" class="unread-text">未读</span>
              <el-icon v-else class="read-icon"><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 详情弹窗 (保持简约风格) -->
    <el-dialog
      v-model="showDialog"
      width="600px"
      class="premium-dialog"
      :show-close="false" 
      align-center
      destroy-on-close
    >
      <!-- 自定义头部 -->
      <template #header="{ close }">
        <div class="dialog-header">
          <span class="header-title">公告详情</span>
          <div class="close-btn" @click="close">×</div>
        </div>
      </template>

      <!-- 内容区域 -->
      <div class="dialog-content">
        <!-- 标题区 -->
        <div class="msg-head">
          <el-tag :type="getTypeTagType(currentMsg.type)" effect="dark" size="small" class="type-badge">
            {{ getTypeLabel(currentMsg.type) }}
          </el-tag>
          <h3 class="full-title">{{ currentMsg.title }}</h3>
        </div>

        <!-- 元数据区 -->
        <div class="msg-meta">
          <div class="meta-item">
            <el-icon><User /></el-icon> <span>{{ currentMsg.publisher_name }}</span>
          </div>
          <div class="meta-item">
            <el-icon><Clock /></el-icon> <span>{{ formatTimeFull(currentMsg.created_at) }}</span>
          </div>
        </div>
        
        <div class="divider"></div>

        <!-- 正文区 -->
        <div class="msg-body">
          {{ currentMsg.content }}
        </div>
      </div>

      <!-- 底部 -->
      <template #footer>
        <div class="dialog-footer">
          <button class="btn-confirm" @click="showDialog = false">我已知晓</button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import StudentSidebar from '@/components/StudentSidebar.vue';
import { getStudentAnnouncements, markAnnouncementRead, type AnnouncementItem } from '@/api/announcement';
import { User, Check, Clock } from '@element-plus/icons-vue';

const loading = ref(false);
const list = ref<AnnouncementItem[]>([]);
const filterType = ref('all');
const showDialog = ref(false);
const currentMsg = ref<Partial<AnnouncementItem>>({});

onMounted(() => {
  fetchData();
});

const fetchData = async () => {
  loading.value = true;
  try {
    const res = await getStudentAnnouncements();
    list.value = res;
  } finally {
    loading.value = false;
  }
};

const unreadCount = computed(() => list.value.filter(i => !i.is_read).length);

const filteredList = computed(() => {
  if (filterType.value === 'unread') {
    return list.value.filter(i => !i.is_read);
  }
  return list.value;
});

const openDetail = async (item: AnnouncementItem) => {
  currentMsg.value = item;
  showDialog.value = true;

  if (!item.is_read) {
    try {
      await markAnnouncementRead(item.id);
      item.is_read = true; // 前端即时更新
    } catch (e) {
      console.error(e);
    }
  }
};

// 工具函数
const formatTime = (t: string) => t ? new Date(t).toLocaleDateString() : '';
const formatTimeFull = (t: string) => t ? new Date(t).toLocaleString() : '';

const getTypeLabel = (type: string) => ({ urgent: '紧急', normal: '通知', course: '课程', tip: '提示' }[type] || '公告');

const getTypeTagType = (type: string) => ({ urgent: 'danger', normal: 'primary', course: 'success', tip: 'warning' }[type] || 'info');
</script>

<style scoped lang="scss">
$bg-color: #f5f6fa;
$primary: #00c9a7;
$text-main: #2c3e50;

.dashboard-container { display: flex; width: 100vw; height: 100vh; background-color: $bg-color; overflow: hidden; }
.main-content { flex: 1; padding: 30px 40px; overflow-y: auto; }

.page-header {
  display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px;
  h2 { font-size: 24px; color: $text-main; margin: 0; }
  p { font-size: 14px; color: #999; margin-top: 5px; }
}

/* 筛选 Tabs */
.filter-tabs {
  display: flex; background: #e0e0e0; padding: 4px; border-radius: 20px;
  span {
    padding: 6px 20px; font-size: 13px; cursor: pointer; border-radius: 16px; color: #666; position: relative; transition: all 0.3s;
    &.active { background: white; color: $text-main; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .badge-dot { position: absolute; top: 6px; right: 8px; width: 6px; height: 6px; background: #ff4d4f; border-radius: 50%; }
  }
}

/* 网格布局 */
.msg-grid {
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
  gap: 20px;
}

/* 卡片样式 */
.msg-card {
  background: white; border-radius: 16px; padding: 20px; 
  display: flex; flex-direction: column; height: 180px;
  border: 1px solid #f0f0f0; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer; position: relative; overflow: hidden;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    border-color: $primary;
  }

  /* 紧急公告特殊样式 */
  &.is-urgent { border-top: 4px solid #ff4d4f; }
  
  /* 已读状态 */
  &.is-read {
    opacity: 0.8; background: #fafafa;
    .title { color: #666; font-weight: normal; }
  }

  .card-header {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
    .type-tag {
      font-size: 11px; padding: 2px 8px; border-radius: 6px; font-weight: bold;
      &.urgent { background: #fef0f0; color: #ff4d4f; }
      &.normal { background: #ecf5ff; color: #409eff; }
      &.course { background: #f0f9eb; color: #67c23a; }
      &.tip { background: #fdf6ec; color: #e6a23c; }
    }
    .time { font-size: 12px; color: #999; }
  }

  .card-body {
    flex: 1; overflow: hidden;
    .title { 
      font-size: 16px; margin: 0 0 8px; color: $text-main; 
      display: flex; align-items: center; gap: 6px;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      
      .dot { width: 8px; height: 8px; background: #ff4d4f; border-radius: 50%; flex-shrink: 0; }
    }
    .summary {
      font-size: 13px; color: #666; line-height: 1.6;
      display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
    }
  }

  .card-footer {
    border-top: 1px dashed #eee; padding-top: 12px; margin-top: 12px;
    display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #999;
    
    .publisher { display: flex; align-items: center; gap: 4px; }
    .status {
      .unread-text { color: #ff4d4f; font-weight: bold; }
      .read-icon { color: $primary; font-size: 16px; }
    }
  }
}

.empty-state { grid-column: 1 / -1; text-align: center; padding: 60px; color: #999; img { opacity: 0.6; margin-bottom: 15px; } }

/* 弹窗整体样式覆盖 */
:deep(.premium-dialog) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  
  .el-dialog__header {
    padding: 0;
    margin: 0;
  }
  
  .el-dialog__body {
    padding: 0;
  }
  
  .el-dialog__footer {
    padding: 0;
  }
}

.dialog-header {
  padding: 20px 25px;
  border-bottom: 1px solid #f5f5f5;
  display: flex; justify-content: space-between; align-items: center;
  
  .header-title { font-size: 16px; font-weight: bold; color: #333; }
  .close-btn { 
    font-size: 24px; color: #ccc; cursor: pointer; line-height: 1; 
    &:hover { color: #333; }
  }
}

.dialog-content {
  padding: 25px;
  
  .msg-head {
    display: flex; align-items: flex-start; gap: 10px; margin-bottom: 15px;
    .type-badge { flex-shrink: 0; margin-top: 4px; border: none; }
    .full-title { font-size: 20px; font-weight: bold; color: #2c3e50; line-height: 1.4; margin: 0; }
  }

  .msg-meta {
    display: flex; gap: 20px; font-size: 13px; color: #999; margin-bottom: 20px;
    .meta-item { display: flex; align-items: center; gap: 5px; }
  }

  .divider { height: 1px; background: #f0f0f0; margin-bottom: 20px; }

  .msg-body {
    font-size: 15px;
    line-height: 1.8;
    color: #4a5568;
    white-space: pre-wrap; /* 保留换行 */
    min-height: 120px;
    background: #fcfcfc; /* 极淡的背景突出正文 */
    padding: 15px;
    border-radius: 8px;
  }
}

.dialog-footer {
  padding: 15px 25px 25px;
  display: flex; justify-content: flex-end;
  
  .btn-confirm {
    background: $primary; /* 青绿色 */
    color: white;
    border: none;
    padding: 10px 28px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 201, 167, 0.3);
    transition: all 0.2s;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 201, 167, 0.4);
      filter: brightness(1.05);
    }
    
    &:active { transform: translateY(0); }
  }
}
</style>