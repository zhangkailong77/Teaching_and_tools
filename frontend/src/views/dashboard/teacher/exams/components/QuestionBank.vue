<template>
  <el-config-provider :locale="zhCn">
  <div class="question-bank">
    <!-- 数据看板 -->
    <div class="stats-overview">
      
      <!-- 卡片1：总题量 -->
      <div class="stat-card total-card">
        <div class="icon-wrapper">📚</div>
        <div class="info">
          <div class="label">题库总题量</div>
          <div class="num">{{ stats.total }} <small>题</small></div>
        </div>
      </div>

      <!-- 卡片2：题型分布 -->
      <div class="stat-card">
        <div class="card-title">题型分布</div>
        <div class="tags-group">
          <div class="mini-stat">
            <span class="l">单选</span><span class="v">{{ stats.type_counts.single || 0 }}</span>
          </div>
          <div class="mini-stat">
            <span class="l">多选</span><span class="v">{{ stats.type_counts.multiple || 0 }}</span>
          </div>
          <div class="mini-stat">
            <span class="l">判断</span><span class="v">{{ stats.type_counts.judge || 0 }}</span>
          </div>
          <div class="mini-stat">
            <span class="l">填空</span><span class="v">{{ stats.type_counts.blank || 0 }}</span>
          </div>
          <div class="mini-stat">
            <span class="l">简答</span><span class="v">{{ stats.type_counts.essay || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- 卡片3：难度概况 -->
      <div class="stat-card">
        <div class="card-title">难度概况</div>
        <div class="progress-group">
          <div class="p-row">
            <span class="label">简单</span>
            <el-progress :percentage="calcPercent(stats.difficulty_counts['1'], stats.total)" :color="'#52c41a'" :stroke-width="8" style="width: 120px" />
            <span class="val">{{ stats.difficulty_counts['1'] || 0 }}</span>
          </div>
          <div class="p-row">
            <span class="label">中等</span>
            <el-progress :percentage="calcPercent(stats.difficulty_counts['2'], stats.total)" :color="'#fa8c16'" :stroke-width="8" style="width: 120px" />
            <span class="val">{{ stats.difficulty_counts['2'] || 0 }}</span>
          </div>
          <div class="p-row">
            <span class="label">困难</span>
            <el-progress :percentage="calcPercent(stats.difficulty_counts['3'], stats.total)" :color="'#f5222d'" :stroke-width="8" style="width: 120px" />
            <span class="val">{{ stats.difficulty_counts['3'] || 0 }}</span>
          </div>
        </div>
      </div>

    </div>
    
    <!-- 1. 顶部操作栏 -->
    <div class="toolbar">
      <div class="filters">
        <el-input 
          v-model="filter.keyword" 
          placeholder="搜索题目内容..." 
          prefix-icon="Search"
          clearable
          style="width: 200px" 
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />

         <el-select v-model="filter.type" placeholder="题型" clearable style="width: 120px" @change="handleSearch">
          <el-option label="单选题" value="single" />
          <el-option label="多选题" value="multiple" />
          <el-option label="判断题" value="judge" />
          <el-option label="填空题" value="blank" />
          <el-option label="简答题" value="essay" />
        </el-select>
        
        <el-select v-model="filter.difficulty" placeholder="难度" clearable style="width: 120px" @change="handleSearch">
          <el-option label="简单" :value="1" />
          <el-option label="中等" :value="2" />
          <el-option label="困难" :value="3" />
        </el-select>

        <el-select v-model="filter.tag" placeholder="知识点" clearable style="width: 140px" @change="handleSearch">
          <el-option v-for="t in tagOptions" :key="t" :label="t" :value="t" />
        </el-select>
        
        <el-button type="primary" plain @click="handleSearch">查询</el-button>
      </div>

      <div class="actions">
        <el-button type="success" plain @click="showImportDrawer = true">导入题目</el-button>
        <el-button type="primary" icon="Plus" @click="handleCreate">录入新题</el-button>
      </div>
    </div>

    <!-- ✅ 新增：全选工具栏 (列表头部) -->
    <div class="list-header-bar" v-if="questions.length > 0">
      <el-checkbox 
        v-model="checkAll" 
        :indeterminate="isIndeterminate" 
        @change="handleCheckAllChange"
      >全选本页</el-checkbox>
      <span class="selected-tip" v-if="selectedIds.length > 0">
        已选择 <span class="num">{{ selectedIds.length }}</span> 项
      </span>
    </div>

    <!-- 2. 题目列表 -->
    <div class="q-list" v-loading="loading">
      <div class="empty-tip" v-if="questions.length === 0">
        暂无题目，请点击右上角录入
      </div>

      <el-checkbox-group v-model="selectedIds" @change="handleCheckedChange">
      <div class="q-card" v-for="(item, index) in questions" :key="item.id">
        <div class="q-header">
          <div class="header-left" style="display: flex; align-items: center; gap: 10px;">
              <!-- 复选框 -->
            <el-checkbox :label="item.id" class="item-checkbox" @click.stop>&nbsp;</el-checkbox>
            <div class="badges">
              <el-tag 
                v-for="t in item.tags" 
                :key="t" 
                size="small" 
                type="info" 
                class="custom-tag"
              >
                #{{ t }}
              </el-tag>
              <span class="type-badge" :class="item.type">{{ getTypeLabel(item.type) }}</span>
              <span class="diff-badge" :class="'lv-'+item.difficulty">{{ getDiffLabel(item.difficulty) }}</span>
            </div>
          </div>
          <div class="ops">
            <el-button link type="primary" size="small" @click="handleEdit(item)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(item.id)">删除</el-button>
          </div>
        </div>
        
        <div class="q-content">
          <!-- 题干 -->
          <div class="stem" v-html="item.content"></div>
          
          <!-- 选项 (仅选择题显示) -->
          <div class="options" v-if="['single', 'multiple'].includes(item.type) && item.options">
            <div class="opt-row" v-for="opt in item.options" :key="opt.label">
              <span class="opt-label" :class="{ 'is-answer': isAnswer(item, opt.label) }">{{ opt.label }}</span>
              <span class="opt-text">{{ opt.text }}</span>
            </div>
          </div>

          <!-- 答案与解析 (默认折叠，可点击展开，这里简单直接展示) -->
          <div class="analysis-box">
            <div class="ans-row">
              <span class="label">正确答案：</span>
              <strong class="val">{{ formatAnswer(item.answer) }}</strong>
            </div>
            <div class="ans-row" v-if="item.analysis">
              <span class="label">解析：</span>
              <span class="val text-gray">{{ item.analysis }}</span>
            </div>
          </div>
        </div>
      </div>
      </el-checkbox-group>
    </div>

    <div class="pagination-bar">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.limit"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="fetchQuestions"
        />
    </div>

    <transition name="el-zoom-in-bottom">
      <div class="batch-toolbar" v-if="selectedIds.length > 0">
        <div class="batch-info">已选中 {{ selectedIds.length }} 道试题</div>
        <div class="batch-actions">
          <el-button type="danger" plain :icon="Delete" @click="handleBatchDelete">批量删除</el-button>
        </div>
      </div>
    </transition>

    <QuestionDrawer 
      v-model="showDrawer" 
      :question-data="currentQuestion"
      @success="handleSuccess" 
    />

    <ImportQuestionDrawer 
      v-model="showImportDrawer" 
      @success="fetchQuestions" 
    />

  </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { Search, Download, Delete } from '@element-plus/icons-vue'
import { getQuestions, deleteQuestion, getQuestionStats, getAllTags, batchDeleteQuestions, type QuestionItem, type QuestionStats } from '@/api/exam'
import { ElMessage, ElMessageBox } from 'element-plus'
import QuestionDrawer from './QuestionDrawer.vue'
import ImportQuestionDrawer from './ImportQuestionDrawer.vue'

const showImportDrawer = ref(false)

// 2. 定义状态
const showDrawer = ref(false)
const currentQuestion = ref<QuestionItem | undefined>(undefined)

const loading = ref(false)
const questions = ref<QuestionItem[]>([])
const filter = reactive({
  keyword: '',
  type: '',
  difficulty: '' as any,
  tag: ''
})

// ✅ 新增状态
const tagOptions = ref<string[]>([]) // 标签下拉选项
const selectedIds = ref<number[]>([]) // 选中的题目ID
const isIndeterminate = ref(false) // 全选框的中间状态
const checkAll = ref(false) // 全选状态



// ✅ 新增：分页状态
const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
})

onMounted(() => {
  fetchQuestions()
  loadStats()
  loadTags()
})

const loadTags = async () => {
  try {
    const res = await getAllTags()
    tagOptions.value = res
  } catch (e) { console.error(e) }
}

const fetchQuestions = async () => {
  loading.value = true
  try {
    // 计算 skip
    const skip = (pagination.page - 1) * pagination.limit
    
    const res = await getQuestions({
      type: filter.type || undefined,
      difficulty: filter.difficulty || undefined,
      keyword: filter.keyword || undefined, // ✅ 传参
      tag: filter.tag || undefined,
      skip: skip,
      limit: pagination.limit
    })
    
    // ✅ 适配新的返回结构
    questions.value = res.items
    pagination.total = res.total
    
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// --- ✅ 全选/多选逻辑 ---
const handleCheckAllChange = (val: boolean) => {
  // 如果全选，就把当前页所有题目的ID赋给 selectedIds
  selectedIds.value = val ? questions.value.map(q => q.id!) : []
  isIndeterminate.value = false
}

const handleCheckedChange = (value: any) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === questions.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < questions.value.length
}

// --- ✅ 批量删除 ---
const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 道题目吗？`, '批量删除', { type: 'warning' })
    await batchDeleteQuestions(selectedIds.value)
    ElMessage.success('批量删除成功')
    fetchQuestions()
    loadStats()
  } catch (e) { }
}

// ✅ 新增：触发搜索（重置到第一页）
const handleSearch = () => {
  pagination.page = 1
  fetchQuestions()
}

const handleCreate = () => {
  currentQuestion.value = undefined // 清空当前选中，表示新增
  showDrawer.value = true
}

const handleEdit = (item: QuestionItem) => {
  currentQuestion.value = item // 传入当前数据
  showDrawer.value = true
}

const handleSuccess = () => {
  fetchQuestions() // 刷新列表
  loadStats()
}

const handleDelete = async (id?: number) => {
  if (!id) return
  try {
    await ElMessageBox.confirm('确定要删除这道题吗？', '警告', { type: 'warning' })
    await deleteQuestion(id)
    ElMessage.success('删除成功')
    fetchQuestions()
    loadStats()
  } catch (e) {
    // cancel
  }
}

// --- 工具函数 ---
const getTypeLabel = (type: string) => {
  const map: any = { single: '单选', multiple: '多选', judge: '判断', blank: '填空', essay: '简答' }
  return map[type] || type
}
const getDiffLabel = (diff: number) => ['简单', '中等', '困难'][diff - 1] || '未知'

const isAnswer = (item: QuestionItem, label: string) => {
  if (Array.isArray(item.answer)) return item.answer.includes(label)
  return item.answer === label
}

const formatAnswer = (ans: any) => {
  if (Array.isArray(ans)) return ans.join('、')
  if (typeof ans === 'boolean') return ans ? '正确' : '错误'
  return ans
}


// ----看板统计----
// 新增统计数据状态
const stats = ref<QuestionStats>({
  total: 0,
  type_counts: {},
  difficulty_counts: {}
})

const loadStats = async () => {
  try {
    const res = await getQuestionStats()
    stats.value = res as any // 强转一下类型，或者在 request 泛型里定义好
  } catch (e) {
    console.error(e)
  }
}

const calcPercent = (count: number, total: number) => {
  if (!total || !count) return 0
  return Math.floor((count / total) * 100)
}
</script>

<style scoped lang="scss">
$primary: #00c9a7;

/* 顶部数据看板样式 */
.stats-overview {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;

  .stat-card {
    flex: 1;
    background: #fff;
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: transform 0.2s;
    
    &:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.05); }

    .card-title { font-size: 14px; color: #999; margin-bottom: 15px; font-weight: 600; }
  }

  /* 总量卡片特殊样式 */
  .total-card {
    flex: 0.6; /* 稍微窄一点 */
    flex-direction: row;
    align-items: center;
    gap: 20px;
    background: linear-gradient(135deg, #00c9a7 0%, #00b894 100%);
    color: white;
    border: none;

    .icon-wrapper { font-size: 40px; background: rgba(255,255,255,0.2); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
    .info {
      .label { font-size: 14px; opacity: 0.9; margin-bottom: 5px; }
      .num { font-size: 32px; font-weight: bold; small { font-size: 14px; font-weight: normal; margin-left: 5px; } }
    }
  }

  /* 题型分布样式 */
  .tags-group {
    display: flex; flex-wrap: wrap; gap: 15px;
    .mini-stat {
      background: #f7f8fa; padding: 8px 12px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; min-width: 60px;
      .l { font-size: 12px; color: #999; margin-bottom: 2px; }
      .v { font-size: 16px; font-weight: bold; color: #333; }
    }
  }

  /* 进度条组样式 */
  .progress-group {
    display: flex; flex-direction: column; gap: 10px;
    .p-row {
      display: flex; align-items: center; gap: 10px; font-size: 12px;
      .label { width: 30px; color: #666; }
      .val { width: 30px; text-align: right; font-weight: bold; color: #333; }
    }
  }
}

.toolbar {
  display: flex; justify-content: space-between; margin-bottom: 20px;
  .filters {
    display: flex; 
    gap: 12px; /* 稍微大一点间距 */
    align-items: center;
  }
  .actions { display: flex; gap: 10px; }
}

.q-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  
  /* ✅ 核心修改：增加 60px 的底部内边距 */
  /* 这会强制把白色背景撑大，留出呼吸空间 */
  padding-bottom: 60px; 
  
  /* ✅ 额外优化：防止卡片四周的阴影被容器裁剪 */
  padding-left: 5px;
  padding-right: 5px;
  margin-top: 5px; 
}

.empty-tip { text-align: center; padding: 40px; color: #999; border: 1px dashed #eee; border-radius: 8px; }

.q-card {
  border: 1px solid #eee; border-radius: 8px; padding: 20px; transition: all 0.2s;
  
  &:hover { border-color: $primary; box-shadow: 0 4px 12px rgba(0, 201, 167, 0.05); }

  .q-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
    align-items: flex-start; /* 顶部对齐，防止多行标签时右侧按钮错位 */

    /* ✅ 新增：左侧容器，包裹复选框和徽章 */
    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap; /* 允许标签过多时换行 */
      flex: 1; /* 占据左侧主要空间 */

      /* 复选框微调 */
      .item-checkbox {
        margin-right: 0;
        height: auto;
      }
    }

    .badges {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;

      /* ✅ 新增：自定义标签样式 (对应 template 里的 class="custom-tag") */
      /* 自定义标签样式 */
      .custom-tag {
        background-color: #ecf5ff; /* 淡蓝背景 */
        color: #409eff;            /* 亮蓝文字 */
        border: 1px solid #d9ecff;
        
        font-weight: 600;
        border-radius: 4px;
        padding: 0 10px;
        margin-right: 10px;
        font-size: 12px;
        height: 24px;
        line-height: 22px;
      }

      /* 原有样式保持不变 */
      .type-badge { 
        background: #e6fffb; 
        color: $primary; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 12px; 
        white-space: nowrap; /* 防止文字换行 */
      }
      .diff-badge { 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 12px; 
        font-weight: bold; 
        white-space: nowrap;
        &.lv-1 { background: #f6ffed; color: #52c41a; }
        &.lv-2 { background: #fff7e6; color: #fa8c16; }
        &.lv-3 { background: #fff1f0; color: #f5222d; }
      }
    }
  }

  /* ✅ 修复：底部解析区域文字重叠问题 (请确保这段代码也在 .q-card 内部) */
  .analysis-box {
    background: #f9fafc; 
    padding: 15px 20px;       
    border-radius: 8px; 
    font-size: 13px;
    margin-top: 20px;         /* 拉开与上方选项的距离 */
    border: 1px solid #f0f0f0;
    
    display: flex;
    flex-direction: column;   /* 纵向排列 */
    gap: 8px;                 /* 行间距 */

    .ans-row {
      line-height: 1.6;       
      .label { color: #909399; font-weight: 600; margin-right: 5px; }
      .val { color: #303133; &.text-gray { color: #606266; } }
    }
  }

  .stem { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 15px; line-height: 1.6; }

  .options {
    margin-bottom: 15px;
    
    .opt-row {
      display: flex; 
      gap: 10px; 
      margin-bottom: 8px; 
      font-size: 14px; 
      color: #555;
      
      /* ✅ 核心修改：添加这一行，强制垂直居中 */
      align-items: center; 

      .opt-label { 
        width: 24px; 
        height: 24px; 
        border: 1px solid #ddd; 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 12px; 
        font-weight: bold;
        
        /* ✅ 建议添加：防止文字过长时标签被挤扁 */
        flex-shrink: 0; 

        &.is-answer { 
          background: $primary; 
          color: white; 
          border-color: $primary; 
        }
      }
      
      /* ✅ 建议添加：微调文字行高，使其更饱满 */
      .opt-text {
        line-height: 1.5;
      }
    }
  }
}

/* 新增分页栏样式 */
.pagination-bar {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  background: white;
  border-top: 1px solid #eee;
  /* 固定在底部或者跟随流都可以，这里建议跟随流 */
  margin-top: auto; 
}

/* 列表头部的全选栏 */
.list-header-bar {
  padding: 10px 5px;
  border-bottom: 1px dashed #eee;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 13px;
  .selected-tip { color: #666; .num { color: $primary; font-weight: bold; margin: 0 2px; } }
}

.batch-toolbar {
  position: fixed;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(44, 62, 80, 0.9); /* 深色背景 */
  color: white;
  padding: 15px 30px;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 30px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  z-index: 2000;
  backdrop-filter: blur(5px);

  .batch-info { font-weight: bold; font-size: 16px; }
  .batch-actions { display: flex; gap: 15px; }
}
</style>