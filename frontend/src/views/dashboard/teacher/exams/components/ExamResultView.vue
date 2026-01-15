<template>
  <div class="result-view" v-loading="loading">
    
    <!-- 1. 顶部导航与统计 -->
    <div class="view-header">
      <div class="top-row">
        <el-button link @click="$emit('back')" class="btn-back">
          <el-icon style="margin-right: 4px;"><ArrowLeft /></el-icon>
          返回试卷列表
        </el-button>
        <div class="actions">
          <el-button icon="Download" class="btn-export" @click="handleExport">导出成绩单</el-button>
        </div>
      </div>
      
      <!-- 统计卡片区 -->
      <div class="stats-dashboard">
        
        <!-- 卡片 1: 参考概况 -->
        <div class="dash-card">
          <div class="chart-box" ref="chartRef1"></div>
        </div>

        <!-- 卡片 2: 成绩分析 (左图右文) -->
        <div class="dash-card score-card">
          <!-- 左侧图表 -->
          <div class="chart-box" ref="chartRef2"></div>
          
          <!-- 右侧：竖向排列的统计信息 -->
          <div class="extra-info">
            <div class="stat-row">
              <span class="label">平均分</span>
              <span class="num main">{{ stats.avgScore }}</span>
            </div>
            <div class="stat-mini-group">
              <div class="mini-item">
                <span class="label">最高</span>
                <span class="num">{{ stats.maxScore }}</span>
              </div>
              <div class="mini-item">
                <span class="label">最低</span>
                <span class="num">{{ stats.minScore }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 卡片 3: 及格分布 -->
        <div class="dash-card">
          <div class="chart-box" ref="chartRef3"></div>
        </div>

        <!-- 卡片 4: 批改进度 (保持进度条但美化) -->
        <div class="dash-card progress-card">
          <div class="p-header">
            <span>批改进度</span>
            <span class="p-val">{{ stats.gradedPercent }}%</span>
          </div>
          <el-progress 
            :percentage="stats.gradedPercent" 
            :color="customColors"
            :stroke-width="12"
            :show-text="false"
            class="custom-progress"
          />
          <div class="p-footer">
            已批 {{ list.filter(i => i.status === 2).length }} / 共 {{ stats.submitCount }}
          </div>
        </div>

      </div>
    </div>

    <!-- 2. 学生成绩表格 -->
    <div class="table-container">
      
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-radio-group v-model="filterStatus" size="small">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="pending">待批改</el-radio-button>
          <el-radio-button label="graded">已完成</el-radio-button>
          <el-radio-button label="unsubmitted">未提交</el-radio-button>
        </el-radio-group>
        
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索姓名或学号..." 
          prefix-icon="Search"
          size="small"
          style="width: 200px"
        />
      </div>

      <el-table :data="filteredList" style="width: 100%" height="100%" stripe>
        <el-table-column prop="student_name" label="姓名" min-width="20">
          <template #default="{ row }">
            <span class="name-text">{{ row.student_name }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="student_number" label="学号" min-width="50" align="center">
          <template #default="{ row }">
            <span class="code-text">{{ row.student_number }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="class_name" label="班级" width="160" align="center" />
        
        <el-table-column label="提交时间" width="220" align="center">
          <template #default="{ row }">
            <span v-if="row.submit_time" class="time-text">{{ formatTime(row.submit_time) }}</span>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="得分明细" align="center">
          <template #default="{ row }">
            <div v-if="row.status > 0" class="score-detail">
              <span class="obj" title="客观题">{{ row.objective_score }}</span>
              <span class="plus">+</span>
              <span class="subj" title="主观题">{{ row.subjective_score }}</span>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column prop="total_score" label="总分" width="150" sortable align="center">
          <template #default="{ row }">
            <span v-if="row.status > 0" class="total-score">{{ row.total_score }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <button 
              v-if="row.status === 1" 
              class="btn-action primary" 
              @click="handleGrade(row)"
            >
              去批阅
            </button>
            <button 
              v-else-if="row.status === 2" 
              class="btn-action outline" 
              @click="handleGrade(row)"
            >
              查看详情
            </button>
            <span v-else class="text-gray">未交卷</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { Search, Refresh, ArrowLeft, Download } from '@element-plus/icons-vue'
import { getExamRecords, getExamDetail, exportExamGrades } from '@/api/exam'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const props = defineProps<{ examId: number }>()
const emit = defineEmits(['back', 'go-grade']) // 'go-grade' 是下一步要用的

const loading = ref(false)
const list = ref<any[]>([])
const searchKeyword = ref('')
const filterStatus = ref('all')
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const examMeta = ref<any>({})

const chartRef1 = ref<HTMLElement | null>(null) // 参考人数
const chartRef2 = ref<HTMLElement | null>(null) // 平均分
const chartRef3 = ref<HTMLElement | null>(null) // 及格率
let charts: echarts.ECharts[] = []

// 统计数据
const stats = computed(() => {
  const totalCount = list.value.length
  const submitCount = list.value.filter(i => i.status >= 0).length
  const submitted = list.value.filter(i => i.status > 0)
  const graded = list.value.filter(i => i.status === 2)
  
  if (submitted.length === 0) return {
    totalCount, submitCount: 0, maxScore: 0, minScore: 0, avgScore: 0, passRate: 0, gradedPercent: 0,
    distribution: [0, 0, 0, 0, 0]
  }

  const scores = submitted.map(i => i.total_score)
  const maxScore = Math.max(...scores)
  const minScore = Math.min(...scores)
  const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / submitted.length)
  let targetPass = 60; // 默认值
  
  // 1. 如果后端存了及格分，就用存的
  if (examMeta.value.pass_score && examMeta.value.pass_score > 0) {
    targetPass = examMeta.value.pass_score;
  } 
  // 2. 如果没存及格分，但是有总分，则计算总分的 60%
  else if (examMeta.value.total_score && examMeta.value.total_score > 0) {
    targetPass = Math.ceil(examMeta.value.total_score * 0.6);
  }
  const passCount = scores.filter(s => s >= targetPass).length 
  const passRate = Math.round((passCount / submitted.length) * 100)
  const gradedPercent = totalCount > 0 ? Math.round((graded.length / totalCount) * 100) : 0

  const totalScore = examMeta.value.total_score || 100
  const dist = [0, 0, 0, 0, 0] // [不及格, 及格, 中等, 良好, 优秀]
  
  scores.forEach(s => {
    const ratio = s / totalScore
    if (ratio < 0.6) dist[0]++
    else if (ratio < 0.7) dist[1]++
    else if (ratio < 0.8) dist[2]++
    else if (ratio < 0.9) dist[3]++
    else dist[4]++
  })

  return {
    totalCount,
    submitCount,
    maxScore,
    minScore,
    avgScore,
    passRate,
    gradedPercent,
    distribution: dist
  }
})

// ✅ 新增：图表初始化函数
const initCharts = () => {
  if (!chartRef1.value || !chartRef2.value || !chartRef3.value) return
  
  // 销毁旧实例防止内存泄漏
  charts.forEach(c => c.dispose())
  charts = []

  const primaryColor = '#00c9a7'
  const secondaryColor = '#e0f2f1'
  const textColor = '#2c3e50'

  // 1. 参考人数 (环形图)
  const chart1 = echarts.init(chartRef1.value)
  chart1.setOption({
    title: { 
      text: `${stats.value.submitCount}/${stats.value.totalCount}`, 
      subtext: '参考人数', 
      left: 'center', top: '32%', 
      textStyle: { fontSize: 16, color: textColor, fontWeight: 'bold' },
      subtextStyle: { fontSize: 12, color: '#999' }
    },
    series: [{
      type: 'pie', radius: ['65%', '85%'], center: ['50%', '50%'],
      label: { show: false },
      data: [
        { value: stats.value.submitCount, itemStyle: { color: primaryColor } },
        { value: stats.value.totalCount - stats.value.submitCount, itemStyle: { color: '#f0f0f0' } }
      ]
    }]
  })
  charts.push(chart1)

  // 2. 成绩分布 (柱状图)
  const chart2 = echarts.init(chartRef2.value)
  chart2.setOption({
    // 移除标题，用 CSS 布局
    grid: { 
      top: '25%', // 留出顶部空间显示数值
      bottom: '10%', 
      left: '0%', 
      right: '0%', 
      containLabel: true // 防止标签被切
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' }, // 鼠标悬停时不显示那根灰线，更干净
      formatter: '{b}: {c}人'
    },
    xAxis: {
      type: 'category',
      data: ['不及格', '及格', '中等', '良好', '优秀'],
      axisTick: { show: false }, // 不显示刻度线
      axisLine: { 
        lineStyle: { color: '#e0e0e0' } // 轴线颜色变淡
      },
      axisLabel: { 
        color: '#999', 
        fontSize: 10,
        interval: 0 
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { 
        lineStyle: { type: 'dashed', color: '#f0f0f0' } // 网格线变成虚线，极淡
      },
      axisLabel: { show: false } // 不显示Y轴数字，更简约，因为柱子上有数字了
    },
    series: [{
      name: '人数',
      type: 'bar',
      barWidth: '24px', // ✅ 柱子加宽
      data: stats.value.distribution,
      itemStyle: {
        color: '#00c9a7', // ✅ 纯正的主题色
        borderRadius: [4, 4, 0, 0] // ✅ 顶部圆角
      },
      label: {
        show: true, // ✅ 开启数值显示
        position: 'top', // ✅ 显示在顶部
        color: '#333',
        fontWeight: 'bold',
        fontSize: 12
      }
    }]
  })
  charts.push(chart2)

  // 3. 及格率 (饼图)
  const chart3 = echarts.init(chartRef3.value)
  chart3.setOption({
    // ✅ 新增：中间的标题配置
    title: {
      text: `${stats.value.passRate}%`,  // 主标题：及格率数值
      subtext: '及格率',                // 副标题：说明文字
      // 定位核心：因为圆环中心设为了 35%，所以标题也要定在 34%~35% 左右
      left: '34%',          
      top: '34%',           // 垂直居中微调
      textAlign: 'center',  // 文字居中对齐
      textStyle: { 
        fontSize: 20,       // 字号大一点
        fontWeight: 'bold', 
        color: '#2c3e50' 
      },
      subtextStyle: { 
        fontSize: 12, 
        color: '#999',
        lineHeight: 14      // 增加一点行高防止太挤
      }
    },
    tooltip: { trigger: 'item' },
    legend: { 
      orient: 'vertical', 
      right: '5%', 
      top: 'center', 
      itemWidth: 8, 
      itemHeight: 8,
      textStyle: { color: '#666' }
    },
    series: [{
      type: 'pie', 
      radius: ['60%', '80%'], // 保持环形
      center: ['35%', '50%'], // ✅ 圆心保持在左侧 35% 处
      avoidLabelOverlap: false,
      label: { show: false }, // 隐藏自带的引导线标签
      data: [
        { value: stats.value.passRate, name: '及格', itemStyle: { color: '#00c9a7' } },
        { value: 100 - stats.value.passRate, name: '不及格', itemStyle: { color: '#ff9f43' } }
      ]
    }]
  })
  charts.push(chart3)
}

// 监听数据变化刷新图表
watch(stats, () => {
  nextTick(() => {
    initCharts()
  })
})

// 窗口大小改变时重绘
window.addEventListener('resize', () => charts.forEach(c => c.resize()))
onUnmounted(() => charts.forEach(c => c.dispose()))

const customColors = [
  { color: '#fab1a0', percentage: 20 },
  { color: '#00c9a7', percentage: 100 },
]

// 列表过滤
const filteredList = computed(() => {
  let res = list.value
  
  // 状态过滤
  if (filterStatus.value !== 'all') {
    if (filterStatus.value === 'pending') res = res.filter(i => i.status === 1)
    if (filterStatus.value === 'graded') res = res.filter(i => i.status === 2)
    if (filterStatus.value === 'unsubmitted') {
      res = res.filter(i => i.status === 0 || i.status === -1) 
    }
  }

  // 关键词过滤
  if (searchKeyword.value) {
    const k = searchKeyword.value.toLowerCase()
    res = res.filter(i => 
      i.student_name.toLowerCase().includes(k) || 
      i.student_number.includes(k)
    )
  }
  
  return res
})

onMounted(() => {
  fetchData()
})

const fetchData = async () => {
  loading.value = true
  try {
    // ✅ 并行请求：同时获取 成绩列表 和 试卷详情(为了拿及格分)
    const [recordsRes, detailRes] = await Promise.all([
      getExamRecords(props.examId),
      getExamDetail(props.examId)
    ])
    
    list.value = recordsRes
    examMeta.value = detailRes // 存入元数据
    
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleGrade = (row: any) => {
  // 触发父组件切换到批阅详情页
  emit('go-grade', row.id)
}

const handleExport = async () => {
  try {
    ElMessage.info('正在生成成绩单，请稍候...')
    
    const res = await exportExamGrades(props.examId)
    
    // 创建 Blob 对象
    const blob = new Blob([res as any], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 设置文件名 (这里简单用当前时间，也可以尝试从响应头解析)
    const fileName = `考试成绩单_${new Date().toISOString().slice(0, 10)}.xlsx`
    link.download = fileName
    
    // 触发点击
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败')
  }
}

// 工具函数
const formatTime = (t: string) => t.replace('T', ' ').substring(0, 16)
const getStatusLabel = (s: number) => {
  const map: any = { 
    '-1': '未开始', // ✅ 新增
    '0': '进行中', 
    '1': '待批改', 
    '2': '已完成' 
  }
  return map[s] || '未知'
}
const getStatusType = (s: number) => {
  const map: any = {
    '-1': 'info',    // 灰色
    '0': '',         // 默认蓝色
    '1': 'warning',  // 橙色
    '2': 'success'   // 绿色
  }
  return map[s] || ''
}

</script>

<style scoped lang="scss">
$primary: #00c9a7;

.result-view {
  height: 100%;
  background: white;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
  overflow: hidden;
}

/* 头部统计区 */
.view-header {
  padding: 20px 30px;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;

  .top-row {
    display: flex; justify-content: space-between; margin-bottom: 20px;
  }

  .btn-back {
    color: #606266;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s;
    
    &:hover {
      color: $primary;
      transform: translateX(-3px); /* 悬停时往左微动，增加交互感 */
    }
    
    .el-icon {
      font-weight: bold;
    }
  }

  .stats-row {
  display: flex; 
  gap: 40px;
  background: #f9fafc; /* 浅底色背景 */
  padding: 15px 25px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  margin-top: 10px;

  .stat-item {
    display: flex; 
    flex-direction: column; 
    gap: 5px;
    
    .label { font-size: 12px; color: #909399; }
    .val { 
      font-size: 24px; /* 加大数字 */
      font-weight: 700; 
      color: #303133; 
      line-height: 1.2;
    }
    .val.highlight { color: $primary; } /* 强调色 */
  }
}
}

/* 表格区 */
.table-container {
  flex: 1; padding: 20px 30px; display: flex; flex-direction: column; overflow: hidden;

  .filter-bar {
    display: flex; justify-content: space-between; margin-bottom: 15px;
  }

  .name-text {
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
  }

.code-text {
  font-family: 'Roboto Mono', monospace; /* 等宽字体显示数字更专业 */
  color: #909399;
  font-size: 13px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  }

  .time-text { font-size: 13px; color: #666; font-family: monospace; }
  .text-gray { color: #ccc; font-size: 12px; }

  .score-detail {
    font-size: 13px; color: #666;
    .plus { margin: 0 4px; color: #ddd; }
    .obj { color: #409eff; }
    .subj { color: #e6a23c; font-weight: bold; }
  }

  .total-score { font-size: 16px; font-weight: bold; color: $primary; }
}

.btn-action {
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;

  /* “去批阅” - 实心风格 */
  &.primary {
    background-color: $primary;
    color: white;
    box-shadow: 0 2px 6px rgba(0, 201, 167, 0.25);
    
    &:hover {
      background-color: mix(#fff, $primary, 10%);
      transform: translateY(-1px);
      box-shadow: 0 4px 10px rgba(0, 201, 167, 0.35);
    }
  }

  /* “查看详情” - 描边风格 */
  &.outline {
    background-color: transparent;
    border-color: $primary;
    color: $primary;
    
    &:hover {
      background-color: rgba(0, 201, 167, 0.05);
    }
  }
}

:deep(.el-radio-group) {
  /* 去掉默认的连体阴影 */
  box-shadow: none !important; 
  display: flex;
  gap: 10px; /* 按钮之间留空隙 */

  .el-radio-button__inner {
    border: 1px solid #e4e7ed;
    border-radius: 6px !important; /* 强制圆角 */
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #606266;
    background: white;
    box-shadow: none !important; /* 去掉左侧阴影 */
    transition: all 0.3s;

    &:hover {
      color: $primary;
      border-color: rgba(0, 201, 167, 0.5);
    }
  }

  /* 选中状态 */
  .el-radio-button__original-radio:checked + .el-radio-button__inner {
    background-color: rgba(0, 201, 167, 0.1); /* 浅青色背景 */
    border-color: $primary;
    color: $primary;
    font-weight: 600;
    box-shadow: none;
  }
}

.actions {
  display: flex;
  gap: 12px;

  /* 导出按钮 */
  .btn-export {
    border: 1px solid $primary;
    color: $primary;
    background-color: white;
    border-radius: 8px;
    font-weight: 600;
    padding: 0 25px 0 1px;
    height: 36px; 
    
    display: inline-flex;
    align-items: center;
    justify-content: center;
    
    :deep(span) {
      display: inline-flex;
      align-items: center;
      line-height: 1; 
    }

    :deep(.el-icon) {
      margin-right: 6px;
      font-size: 16px;
    }
    
    &:hover {
      background-color: $primary;
      color: white;
      box-shadow: 0 4px 12px rgba(0, 201, 167, 0.2);
      transform: translateY(-1px);
    }
  }
}

.stats-dashboard {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 4列等分 */
  gap: 20px;
  padding: 0 30px;
  margin-top: 15px;
  margin-bottom: 20px;

  .dash-card {
    background: white;
    border: 1px solid #f0f0f0;
    border-radius: 12px;
    padding: 15px;
    height: 150px; /* 固定高度 */
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
    
    .chart-box {
      width: 100%;
      height: 100%;
    }
    
    /* 特殊卡片：成绩分析 */
    &.score-card {
      flex-direction: row;
      align-items: stretch; /* 让左右高度一致 */
      padding: 0; 
      
      .chart-box { 
        width: 70%; /* 图表占宽一点 */
        height: 100%;
        padding: 10px; /* 给图表一点内边距 */
      }

      .extra-info {
        width: 30%;
        background: #fcfcfc; /* 右侧给个极淡的背景区分 */
        border-left: 1px solid #f0f0f0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 0 20px;
        gap: 15px;

        /* 平均分样式 */
        .stat-row {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          
          .label { font-size: 12px; color: #999; margin-bottom: 2px; }
          .num.main { 
            font-size: 32px; /* 超大字体 */
            font-weight: 700; 
            color: #2c3e50; 
            line-height: 1;
            font-family: 'DIN Alternate', 'Roboto', sans-serif; /* 选用比较现代的数字字体 */
          }
        }

        /* 最高/最低分样式 */
        .stat-mini-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
          border-top: 1px dashed #eee;
          padding-top: 12px;

          .mini-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            
            .label { color: #999; }
            .num { font-weight: 600; color: #555; }
          }
        }
      }
    }

    /* 特殊卡片：进度条 */
    &.progress-card {
      justify-content: space-between;
      padding: 20px;
      .p-header { 
        display: flex; justify-content: space-between; font-size: 13px; color: #666; font-weight: 600; 
        .p-val { color: $primary; font-weight: bold; }
      }
      .p-footer { font-size: 12px; color: #bbb; text-align: right; }
      
      /* 深度定制进度条圆角 */
      :deep(.el-progress-bar__outer), :deep(.el-progress-bar__inner) {
        border-radius: 10px !important;
      }
    }
  }
}
</style>