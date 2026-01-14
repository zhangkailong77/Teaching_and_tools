<template>
  <div class="grading-container" v-loading="loading">
    
    <!-- 1. 顶部导航 -->
    <div class="grading-header">
      <div class="left">
        <el-button link @click="$emit('back')" class="btn-back">
          <el-icon style="margin-right: 4px;"><ArrowLeft /></el-icon>
          返回成绩单
        </el-button>
        <span class="divider">/</span>
        <span class="student-name">正在批阅：<b>{{ recordData.student_name }}</b></span>
      </div>
      <div class="right">
        <div class="total-score-badge">
          <span>当前总分</span>
          <span class="num">{{ currentTotalScore }}</span>
        </div>
        <button class="btn-submit" :disabled="submitting" @click="handleSubmit">
          {{ submitting ? '提交中...' : '完成批阅' }}
        </button>
      </div>
    </div>

    <div class="grading-body">
      <!-- ✅ 新增：左侧学生列表侧边栏 -->
      <div class="grading-sidebar left-sidebar">
        <div class="sidebar-header">
          <h4>学生名单 ({{ studentList.length }})</h4>
          <el-input v-model="searchKey" placeholder="搜姓名..." size="small" prefix-icon="Search" />
        </div>
        
        <div class="student-list">
          <div 
            v-for="stu in filteredStudents" 
            :key="stu.id" 
            class="stu-item"
            :class="{ active: stu.id === recordId }"
            @click="switchStudent(stu.id)"
          >
            <div class="stu-info">
              <span class="name">{{ stu.student_name }}</span>
              <span class="status-dot" :class="getStatusClass(stu.status)"></span>
            </div>
            <div class="stu-score">
              <span v-if="stu.status === 2" class="score">{{ stu.total_score }}分</span>
              <span v-else class="pending">待批</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 中间：试卷内容 -->
      <div class="paper-content">
        
        <!-- ✅ 新增：客观题概览条 -->
        <div class="objective-summary-bar">
          <div class="sum-left">
            <span class="text">
              客观题自动判分：
              <span class="score">{{ recordData.objective_score }} 分</span>
              <span class="detail">
                (共 {{ objectiveStats.total }} 题，错 {{ objectiveStats.wrong }} 题)
              </span>
            </span>
          </div>
          <div class="sum-right">
            <el-switch
              v-model="showAllQuestions"
              active-text="显示全部题目"
              inactive-text="只看需批阅"
              inline-prompt
              style="--el-switch-on-color: #00c9a7"
            />
          </div>
        </div>

        <!-- 题目列表 -->
        <div class="question-list">
          <template v-for="(q, index) in recordData.questions" :key="q.question_id">
            
            <!-- ✅ 逻辑控制：仅当 '显示全部' 开启，或者 '该题是主观题' 时才显示 -->
            <div 
              v-show="showAllQuestions || !isObjective(q.type)"
              class="q-card"
              :class="{ 'is-objective': isObjective(q.type), 'is-subjective': !isObjective(q.type) }"
              :id="'q-'+q.question_id"
            >
              <!-- 题目头部 -->
              <div class="q-title-row">
                <span class="q-idx">{{ index + 1 }}</span>
                <span class="q-type">{{ getTypeName(q.type) }}</span>
                <span class="q-score-label">满分 {{ q.full_score }}</span>
              </div>
              
              <!-- 题干 -->
              <div class="q-stem" v-html="q.content"></div>

              <!-- A. 客观题区域 (简化显示) -->
              <div v-if="isObjective(q.type)" class="objective-result">
                <div class="result-row">
                  <span class="label">学生答案：</span>
                  <span class="ans" :class="q.is_correct ? 'correct' : 'wrong'">
                    {{ formatAnswer(q.student_answer) }}
                    <el-icon class="icon" v-if="q.is_correct"><Select /></el-icon>
                    <el-icon class="icon" v-else><CloseBold /></el-icon>
                  </span>
                </div>
                <div class="result-row" v-if="!q.is_correct">
                  <span class="label">正确答案：</span>
                  <span class="ans standard">{{ formatAnswer(q.standard_answer) }}</span>
                </div>
                <div class="score-result">
                  得分：<strong>{{ q.earned_score }}</strong>
                </div>
              </div>

              <!-- B. 主观题区域 (重点优化) -->
              <div v-else class="subjective-grading-zone">
                
                <!-- 学生答案区 -->
                <div class="student-answer-box">
                  <div class="box-label">✍️ 学生回答</div>
                  <div class="box-content">{{ q.student_answer || '（该生未作答）' }}</div>
                </div>

                <!-- 参考答案 -->
                <div class="standard-answer-box">
                  <div class="box-label">💡 参考答案</div>
                  <div class="box-content">{{ q.standard_answer }}</div>
                </div>
                
                <!-- 评分操作栏 -->
                <div class="grading-toolbar">
                  <div class="input-group score-group">
                    <label>打分</label>
                    <el-input-number 
                      v-model="gradingForm[q.question_id].score" 
                      :min="0" 
                      :max="q.full_score" 
                      controls-position="right"
                      class="custom-number-input"
                    />
                  </div>
                  <div class="input-group feedback-group">
                    <label>评语</label>
                    <input 
                      v-model="gradingForm[q.question_id].feedback" 
                      type="text" 
                      placeholder="请输入评语（可选）..." 
                      class="custom-text-input"
                    />
                  </div>
                </div>
              </div>

            </div>
          </template>
        </div>

        <!-- 底部占位 -->
        <div class="bottom-placeholder">
          <el-icon><CircleCheck /></el-icon> 
          <span>已显示所有待批阅题目</span>
        </div>

      </div>

      <!-- 3. 右侧：快捷导航栏 -->
      <div class="grading-sidebar">
        <h4>题目导航</h4>
        <div class="nav-grid">
          <div 
            v-for="(q, index) in recordData.questions" 
            :key="q.question_id"
            class="nav-item"
            :class="getNavClass(q)"
            @click="scrollToQuestion(q.question_id)"
          >
            {{ index + 1 }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive, watch } from 'vue'
import { ArrowLeft, Select, CloseBold, CircleCheck } from '@element-plus/icons-vue'
import { getRecordDetail, submitGrade, getExamRecords } from '@/api/exam'
import { ElMessage } from 'element-plus'

const props = defineProps<{ 
  recordId: number, 
  examId: number 
}>()
const emit = defineEmits(['back', 'success'])

const loading = ref(false)
const submitting = ref(false)
const recordData = ref<any>({ questions: [] })
const showAllQuestions = ref(false)

// 存放主观题的打分数据 { question_id: { score: 0, feedback: '' } }
const gradingForm = reactive<any>({})
const studentList = ref<any[]>([])
const searchKey = ref('')
// 过滤学生
const filteredStudents = computed(() => {
  if (!searchKey.value) return studentList.value
  return studentList.value.filter(s => s.student_name.includes(searchKey.value))
})
// 初始化数据
const initData = async () => {
  loading.value = true
  try {
    // 1. 并行请求：获取详情 + 获取同考试的学生列表
    // 注意：如果 studentList 已经有数据了（比如切换学生时），就不必重复请求列表
    const promises = [getRecordDetail(props.recordId)]
    if (studentList.value.length === 0) {
      promises.push(getExamRecords(props.examId))
    }

    const [detailRes, listRes] = await Promise.all(promises)

    // 处理详情数据
    recordData.value = detailRes
    initGradingForm(detailRes) // 封装原来的表单初始化逻辑

    // 处理列表数据
    if (listRes) {
      studentList.value = listRes
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
// 封装初始化表单逻辑 (从 onMounted 提取出来)
const initGradingForm = (res: any) => {
  // 清空旧数据，防止串台
  for (const key in gradingForm) delete gradingForm[key]
  
  res.questions.forEach((q: any) => {
    if (!isObjective(q.type)) {
      gradingForm[q.question_id] = {
        score: q.earned_score || 0,
        feedback: q.teacher_feedback || ''
      }
    }
  })
}

const activeRecordId = ref(props.recordId)

// ✅ 切换学生逻辑
const switchStudent = async (targetRecordId: number) => {
  if (targetRecordId === activeRecordId.value) return
  activeRecordId.value = targetRecordId
  
  loading.value = true
  try {
    const res = await getRecordDetail(targetRecordId)
    recordData.value = res
    initGradingForm(res)
  } finally {
    loading.value = false
  }
}

// 监听 props 变化 (如果从外部进入)
onMounted(() => {
  initData()
})

// 工具函数：列表状态颜色
const getStatusClass = (status: number) => {
  if (status === 2) return 'done' // 已批改
  if (status === 1) return 'pending' // 待批改
  return 'ing' // 进行中
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getRecordDetail(props.recordId)
    recordData.value = res
    
    // 初始化打分表单
    res.questions.forEach((q: any) => {
      if (!isObjective(q.type)) {
        gradingForm[q.question_id] = {
          score: q.earned_score || 0, // 回显已有的分
          feedback: q.teacher_feedback || ''
        }
      }
    })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

// ✅ 新增：计算客观题统计信息
const objectiveStats = computed(() => {
  if (!recordData.value.questions) return { total: 0, wrong: 0 }
  
  const objQuestions = recordData.value.questions.filter((q: any) => isObjective(q.type))
  const wrongCount = objQuestions.filter((q: any) => !q.is_correct).length
  
  return {
    total: objQuestions.length,
    wrong: wrongCount
  }
})

// 计算当前总分
const currentTotalScore = computed(() => {
  let total = 0
  if (!recordData.value.questions) return 0
  
  recordData.value.questions.forEach((q: any) => {
    if (isObjective(q.type)) {
      total += q.earned_score
    } else if (gradingForm[q.question_id]) {
      total += gradingForm[q.question_id].score
    }
  })
  return total
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    const items = []
    for (const qId in gradingForm) {
      items.push({
        question_id: Number(qId),
        score: gradingForm[qId].score,
        feedback: gradingForm[qId].feedback
      })
    }
    
    await submitGrade(props.recordId, items)
    ElMessage.success('批阅完成')
    emit('success')
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

// --- 工具函数 ---
const isObjective = (type: string) => ['single', 'multiple', 'judge', 'blank'].includes(type)

const getTypeName = (type: string) => {
  const map: any = { single: '单选', multiple: '多选', judge: '判断', blank: '填空', essay: '简答' }
  return map[type] || type
}

const formatAnswer = (val: any) => {
  if (typeof val === 'boolean') return val ? '正确' : '错误'
  if (Array.isArray(val)) return val.join(', ')
  return val
}

const getNavClass = (q: any) => {
  if (isObjective(q.type)) {
    return q.is_correct ? 'correct' : 'wrong'
  } else {
    const s = gradingForm[q.question_id]?.score
    return s > 0 ? 'graded' : 'pending'
  }
}

const scrollToQuestion = (id: number) => {
  document.getElementById('q-' + id)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}
</script>

<style scoped lang="scss">
$primary: #00c9a7;
$bg-color: #f5f7fa;
$text-main: #2c3e50;

.grading-container {
  height: 100%; display: flex; flex-direction: column; background: $bg-color;
  position: absolute; top: 0; left: 0; width: 100%; z-index: 20;
}

/* 1. 顶部栏优化 */
.grading-header {
  height: 64px; background: white; border-bottom: 1px solid #eef0f5; 
  display: flex; justify-content: space-between; align-items: center; padding: 0 40px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.02);
  
  .left { display: flex; align-items: center; gap: 10px; font-size: 14px; }

  .btn-back {
    color: #606266;
    font-size: 14px;
    font-weight: 500;
    padding: 0;
    transition: all 0.2s;
    
    &:hover {
      color: $primary;
      transform: translateX(-3px); /* 悬停时往左微动 */
      background: transparent;
    }
    
    .el-icon {
      font-weight: bold;
    }
  }

  .divider { color: #dcdfe6; margin: 0 5px; }
  .student-name { font-size: 16px; color: $text-main; }
  
  .right { display: flex; align-items: center; gap: 20px; }
  
  .total-score-badge {
    background: rgba(0, 201, 167, 0.08); 
    padding: 4px 16px; 
    border-radius: 10px; 
    color: $primary; 
    font-weight: 600; 
    font-size: 13px; 
    display: flex;
    align-items: center; // ✅ 改为居中对齐，便于微调
    border: 1px solid rgba(0, 201, 167, 0.15); 
    
    // ✅ 针对“当前总分”这四个字进行微调
    span:first-child {
      position: relative;
      top: 0px; 
    }
    
    .num { 
      font-size: 28px; 
      margin-left: 10px; 
      font-family: 'DIN Alternate', 'Inter', sans-serif; 
      line-height: 1;
      position: relative;
      top: -2px; 
    }
  }

  .btn-submit {
    background: $primary; color: white; border: none; padding: 10px 24px;
    border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(0, 201, 167, 0.3);
    &:hover { transform: translateY(-1px); filter: brightness(1.05); }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}

.grading-body {
  flex: 1; display: flex; overflow: hidden; 
  padding: 20px; 
  gap: 15px; /* 栏间距 */
  background: #f5f7fa;
}

.paper-content {
  flex: 1; overflow-y: auto; padding-right: 10px; scroll-behavior: smooth;
}

/* 2. 客观题概览条 */
.objective-summary-bar {
  background: white; border-radius: 10px; padding: 15px 20px; margin-bottom: 20px;
  display: flex; justify-content: space-between; align-items: center;
  border: 1px solid #eef0f5;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
  
  .sum-left {
    display: flex; align-items: center; gap: 10px; font-size: 14px;
    .icon { font-size: 20px; }
    .score { font-size: 18px; font-weight: bold; color: $primary; margin: 0 5px; }
    .detail { color: #999; font-size: 12px; }
  }
}

/* 3. 题目卡片通用样式 */
.q-card {
  background: white; border-radius: 12px; padding: 25px; margin-bottom: 20px;
  border: 1px solid #f0f0f0; transition: all 0.2s;
  
  &.is-objective { 
    padding: 15px 25px; 
    background: #fafbfc; 
    border: 1px dashed #e0e0e0;
  }
  
  &.is-subjective {
    border-left: 4px solid $primary; 
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  }

  .q-title-row {
    display: flex; align-items: center; gap: 10px; margin-bottom: 15px;
    .q-idx { 
      width: 24px; height: 24px; background: #333; color: white; border-radius: 50%; 
      display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;
    }
    .q-type { font-weight: bold; color: $text-main; }
    .q-score-label { color: #999; font-size: 12px; margin-left: auto; background: #f5f5f5; padding: 2px 8px; border-radius: 4px; }
  }

  .q-stem { font-size: 15px; color: #333; line-height: 1.6; margin-bottom: 20px; }
}

/* 4. 主观题打分区域 */
.subjective-grading-zone {
  .student-answer-box, .standard-answer-box {
    margin-bottom: 15px;
    .box-label { font-size: 12px; color: #999; margin-bottom: 6px; font-weight: 600; }
    .box-content { 
      padding: 12px; border-radius: 8px; font-size: 14px; line-height: 1.5; 
      white-space: pre-wrap; word-break: break-all;
    }
  }

  .student-answer-box .box-content { background: #f0fdfa; color: #333; border: 1px solid #ccfbf1; }
  .standard-answer-box .box-content { background: #f9f9f9; color: #666; border: 1px dashed #eee; font-size: 13px; }

  .grading-toolbar {
    background: #fff; border-top: 1px solid #eee; margin-top: 20px; padding-top: 20px;
    display: flex; align-items: center; gap: 20px;

    .input-group {
      display: flex; align-items: center; gap: 10px;
      label { font-weight: 600; color: $text-main; font-size: 14px; }
    }

    .score-group { width: 140px; }
    .feedback-group { flex: 1; }

    .custom-text-input {
      width: 100%; padding: 8px 12px; border: 1px solid #e0e0e0; border-radius: 6px;
      outline: none; transition: border 0.2s; font-size: 13px;
      &:focus { border-color: $primary; }
    }
  }
}

/* 5. 客观题结果样式 */
.objective-result {
  font-size: 13px; 
  .result-row { margin-bottom: 5px; display: flex; align-items: center; gap: 5px; }
  .label { color: #999; }
  .ans.correct { color: #52c41a; font-weight: bold; display: flex; align-items: center; gap: 5px; }
  .ans.wrong { color: #f5222d; font-weight: bold; display: flex; align-items: center; gap: 5px; }
  .ans.standard { color: #666; font-family: monospace; }
  .score-result { margin-top: 8px; color: #666; font-size: 12px; }
}

.bottom-placeholder { text-align: center; color: #ccc; margin-top: 40px; margin-bottom: 20px; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 5px; }

.grading-sidebar {
  width: 240px; background: white; border-radius: 12px; padding: 20px; height: fit-content;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  h4 { margin: 0 0 15px; font-size: 14px; color: #999; }
  .nav-grid {
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;
    .nav-item {
      height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; transition: all 0.2s;
      
      &.correct { background: #f6ffed; color: #52c41a; }
      &.wrong { background: #fff1f0; color: #f5222d; }
      &.graded { background: #e6f7ff; color: #1890ff; }
      &.pending { background: #fff7e6; color: #fa8c16; border: 1px solid #ffd591; }
      
      &:hover { filter: brightness(0.95); transform: scale(1.05); }
    }
  }
}

/* 覆盖 Element 数字输入框样式 */
:deep(.custom-number-input) {
  width: 100%;
  .el-input__wrapper {
    box-shadow: 0 0 0 1px #e0e0e0 inset;
    &:hover { box-shadow: 0 0 0 1px #ccc inset; }
    &.is-focus { box-shadow: 0 0 0 1px $primary inset; }
  }
}

.left-sidebar {
  width: 240px; 
  flex-shrink: 0;

  .sidebar-header {
    margin-bottom: 15px;
    h4 { margin: 0 0 10px; font-size: 14px; color: #333; }
  }

  .student-list {
    flex: 1; overflow-y: auto; 
    
    .stu-item {
      display: flex; justify-content: space-between; align-items: center;
      padding: 10px 12px;
      border-radius: 8px;
      cursor: pointer;
      margin-bottom: 5px;
      transition: all 0.2s;
      border: 1px solid transparent;

      &:hover { background: #f9f9f9; }
      
      /* 选中态 */
      &.active {
        background: rgba(0, 201, 167, 0.08);
        border-color: rgba(0, 201, 167, 0.2);
        .name { color: $primary; font-weight: bold; }
      }

      .stu-info {
        display: flex; align-items: center; gap: 8px;
        .name { font-size: 13px; color: #333; }
        .status-dot {
          width: 6px; height: 6px; border-radius: 50%;
          &.done { background: #52c41a; }
          &.pending { background: #fa8c16; }
          &.ing { background: #ccc; }
        }
      }

      .stu-score {
        font-size: 12px;
        .score { font-weight: bold; color: #333; }
        .pending { color: #ccc; }
      }
    }
  }
}
</style>