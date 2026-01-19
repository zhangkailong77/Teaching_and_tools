<template>
  <div class="announcement-widget">
    <div class="widget-header">
      <h4>📢 班级公告</h4>
      <div class="add-btn" @click="showPublish = true">
        <el-icon><Plus /></el-icon> 发布
      </div>
    </div>

    <div class="widget-body" v-loading="loading">
      <div v-if="list.length === 0" class="empty-mini">
        暂无公告
      </div>
      
      <div v-else class="ann-list">
        <div v-for="item in list" :key="item.id" class="ann-item" @click="handleView(item)">
          <div class="ann-top">
            <span class="tag" :class="item.type">{{ getTypeLabel(item.type) }}</span>
            <span class="title">{{ item.title }}</span>
            <span class="pin" v-if="item.is_pinned">📌</span>
          </div>
          <div class="ann-meta">
            <span class="time">{{ formatDate(item.created_at) }}</span>
            <span class="read-stat">
              <el-icon><View /></el-icon> {{ item.read_count }}/{{ item.total_count }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 引用发布弹窗 -->
    <PublishAnnouncementDrawer v-model="showPublish" @success="fetchData" />

    <!-- 引用详情抽屉 -->
    <AnnouncementDetailDrawer v-model="showDetail" :announcement-id="currentId" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, View } from '@element-plus/icons-vue'
import { getTeacherAnnouncements, type AnnouncementItem } from '@/api/announcement'
import PublishAnnouncementDrawer from './PublishAnnouncementDrawer.vue'
import AnnouncementDetailDrawer from './AnnouncementDetailDrawer.vue'

const loading = ref(false)
const list = ref<AnnouncementItem[]>([])
const showPublish = ref(false)
const showDetail = ref(false)
const currentId = ref<number | null>(null)

onMounted(() => {
  fetchData()
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getTeacherAnnouncements()
    list.value = res
  } finally {
    loading.value = false
  }
}

const handleView = (item: AnnouncementItem) => {
  currentId.value = item.id
  showDetail.value = true
}

const formatDate = (date: string) => {
  const d = new Date(date)
  return `${d.getMonth() + 1}-${d.getDate()}` // 仅显示 MM-DD
}

const getTypeLabel = (type: string) => {
  const map: any = { urgent: '紧急', normal: '通知', course: '课件', tip: '提示' }
  return map[type] || '公告'
}
</script>

<style scoped lang="scss">
$primary: #00c9a7;

.announcement-widget {
  margin-top: 30px; /* 与上方日程拉开距离 */
}

.widget-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;
  h4 { margin: 0; font-size: 14px; color: #333; font-weight: 700; }
  
  /* 精致的发布小按钮 */
  .add-btn {
    display: flex; align-items: center; gap: 4px;
    font-size: 12px; color: $primary; cursor: pointer;
    background: rgba(0, 201, 167, 0.1);
    padding: 4px 10px; border-radius: 12px;
    transition: all 0.2s;
    &:hover { background: $primary; color: white; }
  }
}

.ann-list {
  display: flex; flex-direction: column; gap: 12px;
  
  .ann-item {
    background: #f9fafc; padding: 10px 12px; border-radius: 8px; cursor: pointer; transition: all 0.2s;
    border: 1px solid transparent;
    
    &:hover { background: white; border-color: $primary; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

    .ann-top {
      display: flex; align-items: center; gap: 6px; margin-bottom: 6px;
      .title { font-size: 13px; color: #333; font-weight: 500; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .pin { font-size: 12px; }
      
      .tag {
        font-size: 10px; padding: 1px 4px; border-radius: 4px; white-space: nowrap;
        &.urgent { background: #fef0f0; color: #f56c6c; border: 1px solid #fab6b6; }
        &.normal { background: #ecf5ff; color: #409eff; border: 1px solid #b3d8ff; }
        &.course { background: #f0f9eb; color: #67c23a; border: 1px solid #c2e7b0; }
        &.tip { background: #fdf6ec; color: #e6a23c; border: 1px solid #f5dab1; }
      }
    }

    .ann-meta {
      display: flex; justify-content: space-between; font-size: 11px; color: #999;
      .read-stat { display: flex; align-items: center; gap: 3px; }
    }
  }
}

.empty-mini { text-align: center; color: #ccc; font-size: 12px; padding: 10px 0; }
</style>