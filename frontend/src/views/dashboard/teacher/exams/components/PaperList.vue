<template>
  <div class="paper-list-container">
    
    <!-- 1. 顶部操作 -->
    <div class="toolbar">
      <div class="left">
        <el-input 
          placeholder="搜索试卷名称..." 
          prefix-icon="Search"
          style="width: 240px"
        />
        <el-select placeholder="状态" style="width: 120px; margin-left: 10px;">
          <el-option label="全部" value="" />
          <el-option label="进行中" :value="1" />
          <el-option label="已结束" :value="2" />
        </el-select>
      </div>
      <div class="right">
        <!-- 替换原来的 el-button -->
        <button class="btn-premium" @click="handleCreate">
          <el-icon style="margin-right: 4px"><Plus /></el-icon>
          新建试卷
        </button>
      </div>
    </div>

    <!-- 2. 试卷卡片列表 -->
    <div class="grid-list" v-loading="loading">
      
      <!-- 新建卡片 (快捷入口) -->
      <div class="paper-card add-card" @click="handleCreate">
        <el-icon class="icon"><Plus /></el-icon>
        <span>创建新试卷</span>
      </div>

      <!-- 数据卡片 -->
      <div class="paper-card" v-for="item in list" :key="item.id">
        <div class="status-dot" :class="getStatusClass(item.status)"></div>
        <div class="card-body">
          <h3 class="title" :title="item.title">{{ item.title }}</h3>
          <div class="class-tags">
            <el-tag 
              v-for="name in item.class_names" 
              :key="name" 
              size="small" 
              class="c-tag"
            >
              {{ name }}
            </el-tag>
            <span v-if="!item.class_names || item.class_names.length === 0" class="no-class">未设置班级</span>
          </div>
          <div class="meta">
            <span>📝 {{ item.question_count }} 题</span>
            <span class="divider">|</span>
            <span>⏱ {{ item.duration }} 分钟</span>
            <span class="divider">|</span>
            <span>💯 {{ item.total_score }} 分</span>
          </div>
          <div class="time">创建于 {{ formatDate(item.created_at) }}</div>
        </div>

        <div class="card-footer">
          <div class="footer-btns">
            <el-button link class="link-btn primary" @click="emit('edit', item)">编辑</el-button>
            <el-button link class="link-btn view" @click="handleViewResults(item)">成绩查看</el-button>
            <el-button link class="link-btn danger" @click="handleDelete(item.id)">删除</el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="list.length === 0 && !loading" class="empty-box">
        <p>暂无试卷，快去创建一个吧</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getExams, deleteExam, type ExamItem } from '@/api/exam'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'

const loading = ref(false)
const list = ref<ExamItem[]>([])

const emit = defineEmits(['create', 'edit', 'view-results'])

onMounted(() => {
  fetchData()
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getExams()
    list.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  // 触发父组件打开创建弹窗
  emit('create')
}

const handleDelete = async (id: number) => {
  try {
    // 1. 确认框
    await ElMessageBox.confirm('试卷删除后无法找回，确定要删除吗？', '重要提示', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'btn-danger-confirm' // 可以在 CSS 里美化确认按钮
    })
    
    // 2. 调用接口
    await deleteExam(id)
    ElMessage.success('试卷已成功移除')
    
    // 3. 刷新列表
    fetchData()
  } catch (e) {
    // 用户取消或接口报错
  }
}

const handleViewResults = (item: any) => {
  console.log('子组件触发查看成绩:', item.id) // ✅ 加个打印调试
  emit('view-results', item.id) 
}

const getStatusClass = (s: number) => ['draft', 'published', 'ended'][s] || 'draft'
const formatDate = (s: string) => s.split('T')[0]

defineExpose({ fetchData })
</script>

<style scoped lang="scss">
$primary: #00c9a7;

.toolbar {
  display: flex; justify-content: space-between; margin-bottom: 20px;
}

.grid-list {
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
  gap: 20px;
}

.paper-card {
  background: white; border: 1px solid #eee; border-radius: 12px; 
  position: relative; overflow: hidden; transition: all 0.3s;
  display: flex; flex-direction: column; min-height: 200px;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    border-color: $primary;
  }

  .status-dot {
    position: absolute; top: 15px; right: 15px; width: 8px; height: 8px; border-radius: 50%;
    &.draft { background: #ccc; box-shadow: 0 0 0 4px rgba(200,200,200,0.2); }
    &.published { background: $primary; box-shadow: 0 0 0 4px rgba(0,201,167,0.2); }
    &.ended { background: #ff4d4f; }
  }

  .card-body {
    flex: 1; padding: 20px;
    .title { font-size: 16px; margin: 0 0 10px; color: #333; line-height: 1.4; height: 44px; overflow: hidden; }
    .meta { font-size: 12px; color: #666; margin-bottom: 15px; .divider { margin: 0 5px; color: #ddd; } }
    .time { font-size: 12px; color: #999; }
  }

  .card-footer {
  border-top: 1px solid #f5f5f5;
  padding: 12px 20px;
  background: #fafafa;
  
  .footer-btns {
    display: flex;
    justify-content: space-between; /* ✅ 让三个按钮平分空间 */
    align-items: center;
    width: 100%;
  }

  .link-btn {
    font-size: 13px;
    font-weight: 600;
    padding: 0;
    
    /* 各个按钮的颜色 */
    &.primary { color: $primary; }           /* 编辑：青绿色 */
    &.view { color: #606266; }              /* 查看：深灰色 */
    &.danger { color: #f56c6c; }            /* 删除：红色 */
    
    &:hover {
      opacity: 0.7;
      text-decoration: underline;
    }
  }
}
}

.add-card {
  border: 2px dashed #e0e0e0; background: transparent; cursor: pointer;
  align-items: center; justify-content: center; color: #999;
  &:hover { border-color: $primary; color: $primary; background: rgba(0,201,167,0.02); }
  .icon { font-size: 32px; margin-bottom: 10px; }
}

.empty-box { text-align: center; padding: 60px; color: #999; }

.class-tags {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 24px;

  .c-tag {
    background-color: rgba(0, 201, 167, 0.08) !important;
    border-color: rgba(0, 201, 167, 0.2) !important;
    color: $primary !important;
    font-size: 10px;
    font-weight: 600;
  }
}

.btn-premium {
  background: $primary;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 201, 167, 0.3);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 201, 167, 0.4);
    filter: brightness(1.05);
  }

  &:active {
    transform: translateY(0);
  }
}
</style>