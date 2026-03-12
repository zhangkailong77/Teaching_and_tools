<template>
  <div class="analysis-container" v-loading="loading">
    
    <!-- 1. 顶部：核心成绩单 -->
    <div class="score-dashboard">
      <div class="back-nav">
        <el-button link icon="ArrowLeft" @click="$router.push('/dashboard/student/exams')">返回大厅</el-button>
      </div>

      <div class="score-card-wrapper">
        <!-- 左侧：分数展示 -->
        <div class="main-score" :class="isPass ? 'pass' : 'fail'">
          <div class="score-circle">
            <div class="num">{{ realTotalScore }}</div>
            <div class="label">最终得分</div>
          </div>
          <div class="badge">
            <span v-if="isPass" class="tag success">🎉 考试及格</span>
            <span v-else class="tag error">💪 继续努力</span>
          </div>
        </div>

        <!-- 右侧：元数据 -->
        <div class="meta-info">
          <h3>{{ result.exam_title }}</h3>
          <div class="info-grid">
            <div class="item">
              <el-icon><Timer /></el-icon>
              <span>耗时: {{ durationStr }}</span>
            </div>
            <div class="item">
              <el-icon><CircleCheck /></el-icon>
              <span>及格分: {{ result.pass_score }}</span>
            </div>
            <div class="item">
              <el-icon><Calendar /></el-icon>
              <span>交卷: {{ formatTime(result.submit_time) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="content-layout">
      <!-- 2. 左侧：试卷复盘流 -->
      <div class="review-panel">
        <div class="panel-header">
          <div class="title">试卷复盘</div>
          <div class="filters">
            <el-switch v-model="onlyWrong" active-text="只看错题" />
          </div>
        </div>

        <div class="q-list">
          <div 
            v-for="(q, index) in filteredQuestions" 
            :key="q.id" 
            class="q-card"
            :id="'q-' + (index + 1)"
            :class="{ 'is-wrong': isWrong(q) }"
          >
            <div class="q-head">
              <span class="idx">{{ index + 1 }}</span>
              <span class="type">[{{ getTypeLabel(q.type) }}]</span>
              <span class="score-badge">
                得分: <b :class="getScoreClass(q)">{{ q.earned_score }}</b> / {{ q.full_score }}
              </span>
            </div>
            
            <div class="q-stem" v-html="q.content"></div>

            <!-- 答案对比区 -->
            <div class="compare-box">
              <div class="row user">
                <span class="label">你的答案：</span>
                <span class="content" :class="isWrong(q) ? 'wrong-text' : 'correct-text'">
                  <el-icon v-if="isWrong(q)"><CloseBold /></el-icon>
                  <el-icon v-else><Select /></el-icon>
                  {{ formatAnswer(q.student_answer) || '(未作答)' }}
                </span>
              </div>
              <div class="row standard">
                <span class="label">正确答案：</span>
                <span class="content">{{ formatAnswer(q.standard_answer) }}</span>
              </div>
            </div>

            <!-- 解析区 -->
            <div class="analysis-box">
              <div class="label"><el-icon><Reading /></el-icon> 解析：</div>
              <div class="text">{{ q.analysis || '暂无解析' }}</div>
            </div>

            <!-- 老师评语 (仅主观题有) -->
            <div v-if="q.teacher_feedback" class="feedback-box">
              <div class="label">👨‍🏫 老师点评：</div>
              <div class="text">{{ q.teacher_feedback }}</div>
            </div>

          </div>
          <div v-if="filteredQuestions.length === 0" class="empty-tip">
            恭喜！没有错题 🎉
          </div>
        </div>
      </div>

      <!-- 3. 右侧：数据分析与导航 -->
      <div class="side-panel">
        
        <!-- 能力雷达图 -->
        <div class="chart-card">
          <h4>知识点能力模型</h4>
          <div class="chart-box" ref="radarChartRef"></div>
        </div>

        <!-- 答题卡导航 -->
        <div class="nav-card">
          <h4>题目导航</h4>
          <div class="nav-grid">
            <div 
              v-for="(q, index) in result.questions" 
              :key="q.id"
              class="nav-item"
              :class="getNavClass(q)"
              @click="scrollToQuestion(index + 1)"
            >
              {{ index + 1 }}
            </div>
          </div>
          <div class="legend">
            <span><i class="dot correct"></i>正确</span>
            <span><i class="dot partial"></i>半对</span>
            <span><i class="dot wrong"></i>错误</span>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getStudentResultDetail } from '@/api/exam'
import { ArrowLeft, Timer, CircleCheck, Calendar, Select, CloseBold, Reading } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const route = useRoute()
const examId = Number(route.params.id)

const loading = ref(true)
const result = ref<any>({ questions: [] })
const onlyWrong = ref(false)
const radarChartRef = ref<HTMLElement | null>(null)

// 题目过滤
const filteredQuestions = computed(() => {
  if (onlyWrong.value) {
    return result.value.questions.filter((q: any) => isWrong(q))
  }
  return result.value.questions
})

// ✅ 1. 新增：实时计算真实总分 (累加每一道题的 earned_score)
const realTotalScore = computed(() => {
  if (!result.value.questions) return 0
  return result.value.questions.reduce((sum: number, q: any) => sum + (q.earned_score || 0), 0)
})

const isPass = computed(() => realTotalScore.value >= result.value.pass_score)

// 初始化
onMounted(async () => {
  try {
    const res = await getStudentResultDetail(examId)
    result.value = res
    
    nextTick(() => {
      initRadarChart(res.tag_stats)
    })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

// 图表渲染
const initRadarChart = (stats: any) => {
  if (!radarChartRef.value || !stats || Object.keys(stats).length === 0) return
  
  const indicators: any[] = []
  const dataValues: any[] = []
  
  for (const tag in stats) {
    const { total, earned } = stats[tag]
    indicators.push({ name: tag, max: 100 })
    // 计算得分率
    dataValues.push(total === 0 ? 0 : Math.round((earned / total) * 100))
  }

  const chart = echarts.init(radarChartRef.value)
  chart.setOption({
    tooltip: {},
    radar: {
      indicator: indicators,
      splitArea: { areaStyle: { color: ['#f8fcfb', '#fff'] } },
      axisLine: { lineStyle: { color: '#e0e0e0' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: dataValues,
        name: '掌握程度(%)',
        areaStyle: { color: 'rgba(0, 201, 167, 0.2)' },
        itemStyle: { color: '#00c9a7' },
        lineStyle: { width: 2 }
      }]
    }]
  })
}

// --- 工具函数 ---
const isWrong = (q: any) => {
  // 客观题看 is_correct，主观题看得分是否满分
  if (['single', 'multiple', 'judge', 'blank'].includes(q.type)) return !q.is_correct
  return q.earned_score < q.full_score
}

const getScoreClass = (q: any) => {
  if (q.earned_score === q.full_score) return 'text-success'
  if (q.earned_score === 0) return 'text-error'
  return 'text-warning'
}

const getNavClass = (q: any) => {
  if (q.earned_score === q.full_score) return 'correct'
  if (q.earned_score === 0) return 'wrong'
  return 'partial'
}

const getTypeLabel = (t: string) => ({ single: '单选', multiple: '多选', judge: '判断', blank: '填空', essay: '简答' }[t] || t)

const formatAnswer = (val: any) => {
  if (typeof val === 'boolean') return val ? '正确' : '错误'
  if (Array.isArray(val)) return val.join('、')
  return val
}

const formatTime = (t: string) => t ? t.replace('T', ' ').substring(0, 16) : '-'

const durationStr = computed(() => {
  if (!result.value.start_time || !result.value.submit_time) return '-'
  const diff = new Date(result.value.submit_time).getTime() - new Date(result.value.start_time).getTime()
  return Math.floor(diff / 60000) + ' 分钟'
})

const scrollToQuestion = (idx: number) => {
  onlyWrong.value = false // 确保题目显示
  setTimeout(() => {
    document.getElementById('q-' + idx)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 100)
}

</script>

<style scoped lang="scss">
$primary: #00c9a7;
$bg-color: #f5f7fa;
$red: #f56c6c;
$orange: #e6a23c;

.analysis-container {
  min-height: 100vh;
  background-color: $bg-color;
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 顶部成绩单 */
.score-dashboard {
  .back-nav { margin-bottom: 10px; }
  
  .score-card-wrapper {
    background: white; border-radius: 16px; padding: 30px;
    display: flex; align-items: center; gap: 50px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);

    .main-score {
      display: flex; flex-direction: column; align-items: center; gap: 10px;
      .score-circle {
        position: relative;
        width: 120px; height: 120px;
        border-radius: 50%;
        border: 8px solid;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        
        .num { font-size: 48px; font-weight: 800; line-height: 1; }
        .label { font-size: 12px; color: #999; }
      }
      .tag { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; color: white; }

      &.pass {
        .score-circle { border-color: #e0f9f4; color: $primary; }
        .tag.success { background: $primary; }
      }
      &.fail {
        .score-circle { border-color: #fde2e2; color: $red; }
        .tag.error { background: $red; }
      }
    }

    .meta-info {
      flex: 1;
      h3 { font-size: 24px; color: #333; margin: 0 0 20px; }
      .info-grid {
        display: flex; gap: 30px;
        .item { 
          display: flex; align-items: center; gap: 8px; color: #666; font-size: 14px;
          .el-icon { font-size: 18px; color: $primary; }
        }
      }
    }
  }
}

/* 主体布局 */
.content-layout {
  display: flex; gap: 20px;
  
  .review-panel { flex: 1; }
  .side-panel { width: 320px; flex-shrink: 0; display: flex; flex-direction: column; gap: 20px; }
}

/* 题目列表 */
.review-panel {
  background: white; border-radius: 16px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  
  .panel-header {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;
    .title { font-size: 18px; font-weight: bold; border-left: 4px solid $primary; padding-left: 12px; }
  }

  .q-card {
    border-bottom: 1px dashed #eee; padding-bottom: 25px; margin-bottom: 25px;
    &:last-child { border-bottom: none; }
    
    .q-head {
      display: flex; align-items: center; gap: 10px; margin-bottom: 15px;
      .idx { width: 24px; height: 24px; background: #333; color: white; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 12px; }
      .score-badge { margin-left: auto; font-size: 13px; color: #666; .text-success { color: $primary; } .text-error { color: $red; } .text-warning { color: $orange; } }
    }

    .q-stem { font-size: 15px; color: #333; line-height: 1.6; margin-bottom: 15px; }

    .compare-box {
      background: #f9f9f9; padding: 15px; border-radius: 8px; font-size: 14px;
      .row { display: flex; margin-bottom: 8px; &:last-child { margin-bottom: 0; } }
      .label { color: #999; width: 80px; flex-shrink: 0; }
      .content { font-weight: bold; display: flex; align-items: center; gap: 5px; }
      .wrong-text { color: $red; } .correct-text { color: $primary; }
    }

    .analysis-box, .feedback-box {
      margin-top: 15px; font-size: 13px; line-height: 1.5;
      .label { font-weight: bold; color: #666; margin-bottom: 5px; display: flex; align-items: center; gap: 5px; }
      .text { color: #555; }
    }
    
    .feedback-box {
      background: #fff8e6; padding: 10px; border-radius: 6px; border: 1px solid #ffeebc;
      .label { color: $orange; }
    }
  }
}

/* 侧边栏卡片 */
.chart-card, .nav-card {
  background: white; border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  h4 { margin: 0 0 15px; font-size: 15px; color: #333; }
}

.chart-box { height: 200px; }

.nav-grid {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 15px;
  .nav-item {
    height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold;
    &.correct { background: #f0fdfa; color: $primary; border: 1px solid #ccfbf1; }
    &.wrong { background: #fef0f0; color: $red; border: 1px solid #fde2e2; }
    &.partial { background: #fdf6ec; color: $orange; border: 1px solid #faecd8; }
  }
}

.legend {
  display: flex; gap: 15px; justify-content: center; font-size: 12px; color: #666;
  .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 4px; }
  .correct { background: $primary; } .wrong { background: $red; } .partial { background: $orange; }
}

.empty-tip { text-align: center; padding: 40px; color: #999; }
</style>