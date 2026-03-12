<template>
  <div class="stats-grid">
    
    <!-- 卡片 1: 学生概况 (垂直柱状图) -->
    <div class="stat-card">
      <div class="card-left">
        <div class="icon-bg purple"><el-icon><User /></el-icon></div>
        <div class="big-num">{{ data.total_students }}</div>
        <div class="label">学生总数</div>
      </div>
      <div class="card-right">
        <div class="chart-box" ref="chartRef1"></div>
      </div>
    </div>

    <!-- 卡片 3: 执教覆盖 (横向条形图) -->
    <div class="stat-card">
      <div class="card-left">
        <div class="icon-bg green"><el-icon><DataBoard /></el-icon></div>
        <div class="big-num">{{ data.teaching_class_count }}</div>
        <div class="label">执教班级</div>
      </div>
      <div class="card-right scroll-container">
        <!-- 班级列表容器 -->
        <div class="class-matrix">
          <!-- ✅ 使用 el-tooltip 替换原有的 :title -->
          <el-tooltip 
            v-for="(item, index) in data.teaching_distribution" 
            :key="index"
            placement="top"
            effect="light"
            :fallback-placements="['bottom', 'top']"
          >
            <!-- 悬停弹出的内容区 -->
            <template #content>
              <div class="tooltip-content">
                <div class="tooltip-header">绑定课程清单：</div>
                <div v-for="course in item.extra" :key="course" class="course-line">
                  • {{ course }}
                </div>
                <div v-if="!item.extra || item.extra.length === 0" class="empty-tip">暂无课程</div>
              </div>
            </template>

            <!-- 原有的班级胶囊 (去掉 :title 属性) -->
            <div class="class-pill">
              <span class="name">{{ item.name }}</span>
              <span class="badge" v-if="item.value > 0">{{ item.value }}</span>
            </div>
          </el-tooltip>
          
          <div v-if="data.teaching_distribution.length === 0" class="empty-text">暂无班级</div>
        </div>
      </div>
    </div>

    <!-- 卡片 4: 待办任务 (环形图) -->
    <div class="stat-card">
      <div class="card-left">
        <div class="icon-bg orange"><el-icon><Bell /></el-icon></div>
        <div class="big-num">{{ data.total_pending }}</div>
        <div class="label">待办事项</div>
      </div>
      <div class="card-right action-container">
        
        <!-- 作业通道 -->
        <div class="task-block homework" @click="router.push('/dashboard/teacher/homeworks')">
          <div class="block-info">
            <span class="label">待批作业</span>
            <span class="num">{{ data.task_distribution.homework }}</span>
          </div>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>

        <!-- 考试通道 -->
        <div class="task-block exam" @click="router.push('/dashboard/teacher/exams')">
          <div class="block-info">
            <span class="label">待阅试卷</span>
            <span class="num">{{ data.task_distribution.exam }}</span>
          </div>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useRouter } from 'vue-router'
import type { DashboardStats } from '@/api/course'
import { User, Files, DataBoard, Bell, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{ data: DashboardStats }>()
const router = useRouter()

// DOM 引用
const chartRef1 = ref()


let charts: echarts.ECharts[] = []

// 初始化图表
const initCharts = () => {
  charts.forEach(c => c.dispose())
  charts = []

  if (!props.data) return

  // ==========================================
  // 图表 1: 学生分布 (加宽的紫色渐变柱)
  // ==========================================
  if (chartRef1.value) {
    const chart = echarts.init(chartRef1.value)
    const xData = props.data.student_distribution.map(i => i.name)
    const sData = props.data.student_distribution.map(i => i.value)
    
    chart.setOption({
      tooltip: { 
        trigger: 'axis',
        axisPointer: { type: 'none' } // 去掉鼠标悬停时的灰线，更干净
      },
      grid: { 
        top: '25%', bottom: '5%', left: '5%', right: '5%', 
        containLabel: false 
      },
      xAxis: { show: false, data: xData },
      yAxis: { show: false },
      series: [{
        type: 'bar',
        data: sData,
        barWidth: '40%', // ✅ 核心修改：宽度加宽到 40%
        itemStyle: {
          borderRadius: [6, 6, 0, 0], // 圆角加大
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#9b59b6' }, // 浓紫色
            { offset: 1, color: '#e0c3fc' }  // 淡紫色
          ])
        },
        showBackground: true,
        backgroundStyle: { 
          color: 'rgba(180, 180, 180, 0.05)', // 背景条更淡
          borderRadius: [6, 6, 0, 0] 
        },
        label: {
          show: true,
          position: 'top',
          color: '#9b59b6',
          fontSize: 13,
          fontWeight: 'bold',
          offset: [0, 2] // 稍微往上提一点
        }
      }]
    })
    charts.push(chart)
  }
}

// 监听数据变化刷新图表
watch(() => props.data, () => {
  nextTick(() => initCharts())
}, { deep: true })

window.addEventListener('resize', () => charts.forEach(c => c.resize()))
</script>

<style scoped lang="scss">
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
  transition: transform 0.2s;
  height: 140px; 
  border: 1px solid #f5f7fa;
  border-radius: 16px;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.05);
  }

  .card-left {
    width: 25%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 8px;
    z-index: 2;
    
    .icon-bg {
      width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px; margin-bottom: 5px;
      &.purple { background: #f3e5f5; color: #9b59b6; }
      &.blue { background: #e3f2fd; color: #3498db; }
      &.green { background: #e0f2f1; color: #00c9a7; }
      &.orange { background: #fff3e0; color: #f39c12; }
    }

    .big-num { font-size: 28px; font-weight: 800; color: #2c3e50; line-height: 1; font-family: 'DIN Alternate', sans-serif; }
    .label { font-size: 12px; color: #999; }
  }

  .card-right {
    width: 75%; /* ✅ 右侧图表区变大 */
    height: 100%;
    position: relative;
    
    .chart-box {
      width: 100%;
      height: 100%;
    }
  }
}

.scroll-container {
  overflow: hidden; /* 限制外层溢出 */
  padding-right: 5px; /* 给滚动条留点位置 */
}

.class-matrix {
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
  gap: 8px; /* 间距 */
  max-height: 100%; /* 限制高度 */
  overflow-y: auto; /* ✅ 关键：开启垂直滚动 */
  align-content: flex-start; /* 内容靠上对齐 */
  padding: 5px 0;

  /* 自定义滚动条样式，让它不那么丑 */
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 4px; }
  &::-webkit-scrollbar-track { background: transparent; }

  .class-pill {
    background-color: #f0fdfa; /* 浅青背景 */
    color: #00c9a7;
    border: 1px solid rgba(0, 201, 167, 0.15);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap; /* 防止文字折行 */
    cursor: default;
    transition: all 0.2s;

    &:hover {
      background-color: #00c9a7;
      color: white;
      transform: translateY(-1px);
    }

    .badge {
      background: white;
      color: #00c9a7;
      border-radius: 10px;
      padding: 0 5px;
      font-size: 10px;
      height: 16px;
      line-height: 16px;
      min-width: 16px;
      text-align: center;
    }
  }
  
  .empty-text { font-size: 12px; color: #ccc; width: 100%; text-align: center; margin-top: 20px; }
}

/* =========================================
   ✅ 卡片 4: 待办任务 (双通道布局)
   ========================================= */
.action-container {
  display: flex;
  flex-direction: column; /* 上下排列 */
  gap: 8px;
  padding: 5px 0;
}

.task-block {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  
  .block-info {
    display: flex;
    align-items: center;
    gap: 10px;
    .label { font-size: 12px; color: #666; font-weight: 500; }
    .num { font-weight: 800; font-size: 16px; }
  }

  .arrow { font-size: 12px; color: #ccc; transition: transform 0.2s; }

  &:hover {
    transform: translateX(3px); /* 悬停右移反馈 */
    .arrow { transform: translateX(2px); }
  }

  /* 🟠 作业通道风格 */
  &.homework {
    background: #fff7e6; /* 浅橙背景 */
    border: 1px solid #ffe7ba;
    .num { color: #fa8c16; }
    &:hover { border-color: #fa8c16; }
  }

  /* 🔴 试卷通道风格 */
  &.exam {
    background: #fff1f0; /* 浅红背景 */
    border: 1px solid #ffccc7;
    .num { color: #f5222d; }
    &:hover { border-color: #f5222d; }
  }
}

.tooltip-content {
  padding: 5px;
  .tooltip-header {
    font-weight: bold;
    margin-bottom: 8px;
    color: #909399;
    font-size: 12px;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 4px;
  }
  .course-line {
    line-height: 1.8;
    font-size: 13px;
    color: #333;
    white-space: nowrap; /* 防止课程名太长被折行，保持一行一课 */
  }
  .empty-tip {
    color: #ccc;
    font-size: 12px;
  }
}
</style>