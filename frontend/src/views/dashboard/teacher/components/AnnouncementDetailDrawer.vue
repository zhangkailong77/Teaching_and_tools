<template>
  <el-drawer
    v-model="visible"
    title="公告详情"
    size="650px"
    direction="rtl"
  >
    <div v-loading="loading" class="detail-container">
      <template v-if="detail">
        <!-- 公告头部信息 -->
        <div class="ann-header">
          <div class="title-row">
            <span class="tag" :class="detail.type">{{ getTypeLabel(detail.type) }}</span>
            <h2 class="title">{{ detail.title }}</h2>
            <span class="pin" v-if="detail.is_pinned">📌 置顶</span>
          </div>
          <div class="meta-row">
            <span>发布者: {{ detail.publisher_name }}</span>
            <span>发布时间: {{ formatDateTime(detail.created_at) }}</span>
          </div>
          <div class="meta-row">
            <span>发布范围: {{ detail.class_names.join(', ') }}</span>
            <span class="read-stat">
              阅读情况: <strong>{{ detail.read_count }}</strong>/{{ detail.total_count }}
              <span :class="readRate >= 80 ? 'good' : readRate >= 50 ? 'normal' : 'low'">
                ({{ readRate }}%)
              </span>
            </span>
          </div>
        </div>

        <!-- 公告内容 -->
        <div class="ann-content">
          <h3>公告内容</h3>
          <div class="content-body" v-html="detail.content"></div>
        </div>

        <!-- 阅读统计 -->
        <div class="read-stats">
          <h3>
            阅读统计
            <span class="count-info">
              已读 {{ detail.read_count }} 人 / 未读 {{ detail.total_count - detail.read_count }} 人
            </span>
          </h3>
          <div class="student-list">
            <div
              v-for="stu in detail.students"
              :key="stu.id"
              class="student-item"
              :class="{ read: stu.is_read }"
            >
              <div class="stu-info">
                <span class="name">{{ stu.name }}</span>
                <span class="number">{{ stu.student_number }}</span>
              </div>
              <span class="status">
                <el-icon v-if="stu.is_read" color="#67c23a"><CircleCheck /></el-icon>
                <el-icon v-else color="#ccc"><CircleClose /></el-icon>
                {{ stu.is_read ? '已读' : '未读' }}
              </span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { getAnnouncementDetail } from '@/api/announcement'

interface Props {
  modelValue: boolean
  announcementId: number | null
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const detail = ref<any>(null)

const readRate = computed(() => {
  if (!detail.value || detail.value.total_count === 0) return 0
  return Math.round((detail.value.read_count / detail.value.total_count) * 100)
})

watch(() => props.announcementId, (id) => {
  if (id && props.modelValue) {
    fetchDetail(id)
  }
}, { immediate: true })

const fetchDetail = async (id: number) => {
  loading.value = true
  try {
    detail.value = await getAnnouncementDetail(id)
  } finally {
    loading.value = false
  }
}

const formatDateTime = (date: string) => {
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const getTypeLabel = (type: string) => {
  const map: any = { urgent: '紧急', normal: '通知', course: '课件', tip: '提示' }
  return map[type] || '公告'
}
</script>

<style scoped lang="scss">
$primary: #00c9a7;

.detail-container {
  padding: 0 10px;
}

.ann-header {
  background: linear-gradient(135deg, #f5f7fa 0%, #e3f2fd 100%);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;

  .title-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;

    .tag {
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 4px;
      white-space: nowrap;
      &.urgent { background: #fef0f0; color: #f56c6c; border: 1px solid #fab6b6; }
      &.normal { background: #ecf5ff; color: #409eff; border: 1px solid #b3d8ff; }
      &.course { background: #f0f9eb; color: #67c23a; border: 1px solid #c2e7b0; }
      &.tip { background: #fdf6ec; color: #e6a23c; border: 1px solid #f5dab1; }
    }

    .title {
      flex: 1;
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }

    .pin {
      font-size: 14px;
      color: #f56c6c;
    }
  }

  .meta-row {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: #666;
    margin-top: 8px;

    .read-stat {
      strong { color: $primary; }
      .good { color: #67c23a; }
      .normal { color: #e6a23c; }
      .low { color: #f56c6c; }
    }
  }
}

.ann-content {
  margin-bottom: 24px;

  h3 {
    font-size: 15px;
    font-weight: 600;
    color: #333;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #f0f0f0;
  }

  .content-body {
    font-size: 14px;
    line-height: 1.8;
    color: #555;
    white-space: pre-wrap;
    word-break: break-word;
  }
}

.read-stats {
  h3 {
    font-size: 15px;
    font-weight: 600;
    color: #333;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .count-info {
      font-size: 13px;
      font-weight: 400;
      color: #999;
    }
  }

  .student-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 400px;
    overflow-y: auto;

    .student-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 14px;
      background: #f9fafc;
      border-radius: 8px;
      border: 1px solid #e8eaed;
      transition: all 0.2s;

      &.read {
        background: #f0f9eb;
        border-color: #c2e7b0;
      }

      &:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      }

      .stu-info {
        display: flex;
        align-items: center;
        gap: 12px;

        .name {
          font-size: 14px;
          font-weight: 500;
          color: #333;
        }

        .number {
          font-size: 12px;
          color: #999;
        }
      }

      .status {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        color: #666;
      }
    }
  }
}
</style>