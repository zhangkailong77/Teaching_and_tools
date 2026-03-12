<template>
  <div class="dashboard-container">
    <StudentSidebar />

    <main class="main-content">
      <!-- 顶部问候与概览 -->
      <div class="page-header">
        <div class="header-left">
          <h2>作业任务中心</h2>
          <p>管理你的学习任务，把控时间节奏</p>
        </div>
        <div class="header-right">
          <!-- 简单的顶部数据条 -->
          <div class="stat-pill">
            <span class="label">本周已提交</span>
            <span class="val">{{ stats.week_submitted_count }}</span>
          </div>
          <div class="stat-pill highlight">
            <span class="label">待完成</span>
            <span class="val">{{ stats.pending_count }}</span>
          </div>
        </div>
      </div>

      <div class="layout-grid">
        
        <!-- === 左侧：主要任务列表 (70%) === -->
        <div class="left-panel">
          
          <!-- Tabs 切换 (大地色系风格) -->
          <div class="custom-tabs">
            <div 
              class="tab-item" 
              :class="{ active: currentTab === 0 }" 
              @click="currentTab = 0"
            >
              📝 待办任务
              <span class="badge" v-if="pendingCount > 0">{{ pendingCount }}</span>
            </div>
            <div 
              class="tab-item" 
              :class="{ active: currentTab === 1 }" 
              @click="currentTab = 1"
            >
              ⏳ 批改中
            </div>
            <div 
              class="tab-item" 
              :class="{ active: currentTab === 2 }" 
              @click="currentTab = 2"
            >
              ✅ 已批改
            </div>
          </div>

          <!-- 任务列表 -->
          <div class="task-list-wrapper">
            <div v-if="filteredList.length === 0" class="empty-state">
              <p>暂无相关作业</p>
            </div>

            <div 
              v-else 
              class="earth-card" 
              v-for="task in filteredList" 
              :key="task.id"
              :class="{ 'urgent': isUrgent(task.deadline) && task.status === 0 }"
              :style="{
                backgroundImage: `linear-gradient(to right, #fff 50%, rgba(255,255,255,0) 100%), url(${getImgUrl(task.course_cover)})`
              }"
            >
              <!-- 左侧装饰条 -->
              <div class="status-bar"></div>

              <div class="card-content" style="position: relative; z-index: 2; width: 100%;">
                <div class="meta-row">
                  <span class="course-tag" :class="{'is-custom': !task.course_cover}">
                    {{ task.course_name || '班级任务' }}
                  </span>
                  <span class="lesson-tag" v-if="task.lesson_title">
                    {{ task.lesson_title }}
                  </span>
                  <span class="deadline-tag" v-if="task.deadline" style="background: rgba(255,255,255,0.8); padding: 2px 6px; border-radius: 4px;">
                    📅 {{ formatDate(task.deadline) }} 截止
                  </span>
                </div>
                
                <h3 class="task-title">{{ task.title }}</h3>
                
                <div class="bottom-row">
                  <div class="status-text">
                    <span v-if="task.status === 0 && isUrgent(task.deadline)" class="text-brown">
                      🔥 仅剩 {{ getDaysLeft(task.deadline) }} 天
                    </span>
                    <span v-else-if="task.status === 2" class="text-score">
                      得分: <strong>{{ task.score }}</strong>
                    </span>
                    <span v-else class="text-gray">普通优先级</span>
                  </div>
                  
                  <button 
                    class="action-btn" 
                    :class="{ 'disabled': task.status === 0 && isExpired(task.deadline) }"
                    :disabled="task.status === 0 && isExpired(task.deadline)"
                    @click="handleOpenDrawer(task)"
                  >
                    {{ task.status === 0 && isExpired(task.deadline) ? '已截止' : getActionText(task.status) }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- === 右侧：数据看板 (30%) === -->
        <div class="right-panel-dashboard">
          
          <!-- 图表卡片 -->
          <div class="dashboard-card chart-card">
            <h4>作业完成率</h4>
            <div ref="chartRef" class="chart-container"></div>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="dot done"></span> 已完成
              </div>
              <div class="legend-item">
                <span class="dot todo"></span> 待办
              </div>
            </div>
          </div>

          <!-- 近期截止 -->
          <div class="dashboard-card urgent-card">
            <h4>🚨 近期截止</h4>
            <div class="urgent-list">
              <div class="u-item" v-for="task in urgentTasks" :key="task.id">
                <div class="u-left">
                  <div class="u-title">{{ task.title }}</div>
                  <div class="u-date">{{ formatDateShort(task.deadline) }}</div>
                </div>
                <div class="u-right">
                  <button class="mini-btn" @click="handleOpenDrawer(task)">Go</button>
                </div>
              </div>
              <div v-if="urgentTasks.length === 0" class="no-urgent">
                近期无紧急作业 ☕
              </div>
            </div>
          </div>

          <!-- 学习格言/提示 -->
          <div class="dashboard-card quote-card">
            <p>“ 积跬步，以至千里 ”</p>
          </div>

          <div class="dashboard-card trend-card">
            <h4>📈 成绩走势</h4>
            <div ref="lineChartRef" class="line-chart-container"></div>
          </div>

        </div>
      </div>

      <!-- 抽屉组件 -->
      <HomeworkDrawer 
        ref="drawerRef" 
        @success="fetchData" 
        @close="fetchData" 
      />

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import StudentSidebar from '@/components/StudentSidebar.vue';
import HomeworkDrawer from '@/components/HomeworkDrawer.vue';
import { getMyHomeworkTodos, getStudentDashboardStats, type AssignmentCard } from '@/api/homework';
import * as echarts from 'echarts'; // 引入 ECharts
import { getImgUrl } from '@/utils/index';

// --- 状态定义 ---
const currentTab = ref(0);
const allTasks = ref<AssignmentCard[]>([]);
const drawerRef = ref();
const chartRef = ref<HTMLElement | null>(null);
// ✅ 新增状态
const stats = ref({
  pending_count: 0,
  week_submitted_count: 0,
  score_trend: [] as any[]
});

// --- 初始化 ---
onMounted(async () => {
  await fetchData();
  initChart();
});

const fetchData = async () => {
  try {
    // 1. 并行请求：获取列表 + 获取统计
    const [listRes, statsRes] = await Promise.all([
      getMyHomeworkTodos(),
      getStudentDashboardStats()
    ]);

    // 2. 更新列表
    allTasks.value = listRes;
    updateChart(); // 更新饼图

    // 3. 更新统计和折线图
    stats.value = statsRes;
    initLineChart(statsRes.score_trend); // 把数据传给图表函数

  } catch (error) {
    console.error(error);
  }
};

// --- 计算属性 ---
const filteredList = computed(() => {
  return allTasks.value.filter(t => t.status === currentTab.value);
});

const pendingCount = computed(() => allTasks.value.filter(t => t.status === 0).length);
const doneCount = computed(() => allTasks.value.filter(t => t.status !== 0).length);

// 获取近期紧急任务 (未来3天内且未完成)
const urgentTasks = computed(() => {
  const now = new Date();
  const threeDaysLater = new Date();
  threeDaysLater.setDate(now.getDate() + 3);
  
  return allTasks.value.filter(t => {
    if (!t.deadline || t.status !== 0) return false;
    const d = new Date(t.deadline);
    return d > now && d < threeDaysLater;
  }).slice(0, 3); // 只取前3个
});

// --- ECharts 图表逻辑 ---
let myChart: echarts.ECharts | null = null;

const initChart = () => {
  if (chartRef.value) {
    myChart = echarts.init(chartRef.value);
    updateChart();
    window.addEventListener('resize', () => {
      myChart?.resize();
      lineChart?.resize(); 
    });
  }
};

const updateChart = () => {
  if (!myChart) return;
  const total = allTasks.value.length || 1; // 防止除0
  const rate = Math.round((doneCount.value / total) * 100);

  // 使用你的配色
  const colorDone = '#00c9a7';  // 青绿
  const colorTodo = '#947456';  // 大地褐

  const option = {
    series: [
      {
        type: 'pie',
        radius: ['60%', '80%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'center',
          formatter: `{val|${rate}%}\n{name|完成率}`,
          rich: {
            val: { fontSize: 24, fontWeight: 'bold', color: '#2A5850' },
            name: { fontSize: 12, color: '#999', padding: [5, 0, 0, 0] }
          }
        },
        labelLine: { show: false },
        data: [
          { value: doneCount.value, name: '已完成', itemStyle: { color: colorDone } },
          { value: pendingCount.value, name: '待办', itemStyle: { color: colorTodo } }
        ]
      }
    ]
  };
  myChart.setOption(option);
};

// 监听数据变化刷新图表
watch(allTasks, updateChart);

// ✅ 新增：监听 Tab 切换，强制刷新数据，防止状态滞后
watch(currentTab, () => {
  fetchData();
});

// --- 交互与工具函数 ---
const handleOpenDrawer = (task: AssignmentCard) => drawerRef.value.open(task);

const getActionText = (s: number) => ['去完成', '查看提交', '查看成绩'][s];
const formatDate = (d: string) => d ? new Date(d).toLocaleDateString() : '无限制';
const formatDateShort = (d: string) => d ? new Date(d).toLocaleDateString().slice(5) : '-'; // MM/DD
const isUrgent = (d: string) => {
  if (!d) return false;
  const days = getDaysLeft(d);
  return days >= 0 && days <= 3;
};
const getDaysLeft = (d: string) => {
  const diff = new Date(d).getTime() - new Date().getTime();
  return Math.ceil(diff / (1000 * 3600 * 24));
};


// --- 监听成绩变化刷新图表 ---
const lineChartRef = ref<HTMLElement | null>(null);
let lineChart: echarts.ECharts | null = null;

// 3. 初始化折线图函数
const initLineChart = (trendData: any[]) => {
  if (!lineChartRef.value) return;
  
  // 处理空数据
  if (!trendData || trendData.length === 0) {
    trendData = []; // 或者给个空数组，ECharts 会显示空白
  }

  // 防止重复初始化
  if (lineChart) {
    lineChart.dispose();
  }
  lineChart = echarts.init(lineChartRef.value);
  
  const option = {
    grid: { top: 30, right: 10, bottom: 20, left: 30 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: trendData.map(i => i.date),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#999', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
    },
    series: [
      {
        data: trendData.map(i => i.score),
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#00c9a7' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 201, 167, 0.4)' },
            { offset: 1, color: 'rgba(0, 201, 167, 0.01)' }
          ])
        }
      }
    ]
  };
  lineChart.setOption(option);
};


//----自定义作业----
const getCardStyle = (task: AssignmentCard) => {
  if (task.course_cover) {
    return {
      backgroundImage: `linear-gradient(to right, #fff 50%, rgba(255,255,255,0) 100%), url(${getImgUrl(task.course_cover)})`
    };
  } else {
    // 自定义作业没有封面，使用纯色或默认图案
    return {
      background: 'white',
      borderLeft: '4px solid #00c9a7' // 这里其实被 status-bar 覆盖了，主要是 fallback
    };
  }
};


// 检查作业是否已过期
const isExpired = (d: string) => {
  if (!d) return false; // 无截止日期
  return new Date(d).getTime() < new Date().getTime();
};
</script>

<style scoped lang="scss">
/* --- 调色板 (Earth Tone + Primary) --- */
$primary: #00c9a7;
$bg-color: #f5f6fa;
$earth-brown: #947456; /* 核心大地色 */
$earth-dark: #2A5850;  /* 深森林绿 */
$earth-light: #F9F7F2; /* 米白色背景 */
$text-main: #333;
$text-light: #999;

.dashboard-container { display: flex; width: 100vw; height: 100vh; background-color: $bg-color; font-family: 'Inter', sans-serif; overflow: hidden; }
.main-content { flex: 1; padding: 30px 40px; overflow-y: auto; display: flex; flex-direction: column; }

/* 顶部 Header */
.page-header {
  display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px;
  h2 { font-size: 24px; color: $earth-dark; margin: 0; }
  p { font-size: 14px; color: $text-light; margin-top: 5px; }
  
  .header-right { display: flex; gap: 15px; }
  .stat-pill {
    background: white; padding: 6px 15px; border-radius: 20px; display: flex; align-items: center; gap: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    .label { font-size: 12px; color: $text-light; }
    .val { font-weight: bold; font-size: 16px; color: $earth-dark; }
    &.highlight { border: 1px solid $earth-brown; .val { color: $earth-brown; } }
  }
}

/* 左右分栏布局 */
.layout-grid {
  display: grid;
  grid-template-columns: 1fr 320px; /* 左侧自适应，右侧固定宽 */
  gap: 30px;
  min-height: 500px;
}

/* === 左侧面板 === */
.left-panel {
  display: flex; flex-direction: column; gap: 20px;
}

/* 自定义大地色 Tabs */
.custom-tabs {
  display: flex; gap: 10px; border-bottom: 2px solid #eee; padding-bottom: 10px;
  .tab-item {
    position: relative; padding: 8px 20px; cursor: pointer; font-weight: 600; color: $text-light; transition: all 0.3s; border-radius: 8px;
    &:hover { color: $earth-brown; background: rgba(148, 116, 86, 0.05); }
    &.active { color: white; background: $earth-dark; box-shadow: 0 4px 10px rgba(42, 88, 80, 0.3); }
    
    .badge { position: absolute; top: -5px; right: -5px; background: $earth-brown; color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px; border: 2px solid #fff; }
  }
}

/* 任务列表 */
.task-list-wrapper {
  display: flex; flex-direction: column; gap: 15px;
}

.empty-state { text-align: center; padding: 60px; color: #ccc; img { width: 100px; margin-bottom: 10px; opacity: 0.5; } }

/* 大地风卡片 */
.earth-card {
  background: white; border-radius: 12px; padding: 20px; 
  position: relative; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  border: 1px solid #f0f0f0;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(148, 116, 86, 0.1); /* 褐色的投影 */
  }

  /* 左侧状态条 */
  .status-bar { position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: $primary; }
  /* 紧急状态变色 */
  &.urgent .status-bar { background: $earth-brown; }

  .card-content { padding-left: 15px; }

  .meta-row { display: flex; align-items: center; gap: 10px; font-size: 12px; margin-bottom: 8px;
    .course-tag { background: $earth-light; color: $earth-dark; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
    .lesson-tag { color: $text-light; }
    .deadline-tag { margin-left: auto; color: $text-light; }
  }

  .task-title { margin: 0 0 15px; font-size: 16px; color: $text-main; }

  .bottom-row { display: flex; justify-content: space-between; align-items: center;
    .status-text { font-size: 13px; font-weight: 500;
      .text-brown { color: $earth-brown; display: flex; align-items: center; gap: 5px; }
      .text-score { color: $primary; font-size: 14px; }
      .text-gray { color: #ccc; font-weight: normal; }
    }
    .action-btn { 
      padding: 6px 18px; border-radius: 20px; border: 1px solid #ddd; background: white; cursor: pointer; transition: all 0.2s; font-size: 13px;
      &:hover { border-color: $earth-dark; color: $earth-dark; background: $earth-light; }
    }
  }

  background-size: cover;
  background-position: center right; /* 图片靠右 */
  background-repeat: no-repeat;
}

/* === 右侧：数据看板 === */
.right-panel-dashboard {
  display: flex; flex-direction: column; gap: 20px;
}

.dashboard-card {
  background: white; border-radius: 16px; padding: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  h4 { margin: 0 0 15px; font-size: 15px; color: $earth-dark; border-left: 4px solid $earth-brown; padding-left: 10px; }
}

/* 图表卡片 */
.chart-container { width: 100%; height: 180px; }
.chart-legend { display: flex; justify-content: center; gap: 20px; margin-top: 5px;
  .legend-item { font-size: 12px; color: $text-light; display: flex; align-items: center; gap: 5px; 
    .dot { width: 8px; height: 8px; border-radius: 50%; }
    .dot.done { background: $primary; }
    .dot.todo { background: $earth-brown; }
  }
}

/* 紧急列表 */
.urgent-list {
  display: flex; flex-direction: column; gap: 10px;
  .u-item { display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px dashed #eee;
    &:last-child { border: none; padding-bottom: 0; }
    .u-left {
      .u-title { font-size: 13px; color: $text-main; width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .u-date { font-size: 12px; color: $earth-brown; }
    }
    .mini-btn { font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid $earth-brown; color: $earth-brown; background: white; cursor: pointer; &:hover { background: $earth-brown; color: white; } }
  }
  .no-urgent { text-align: center; color: #ccc; font-size: 13px; padding: 10px; }
}

/* 格言卡片 */
.quote-card {
  background: $earth-light; border: none;
  p { margin: 0; color: $earth-brown; font-style: italic; text-align: center; font-size: 13px; font-family: serif; }
}

/* 趋势图容器 */
.line-chart-container {
  width: 100%;
  height: 200px; /* 或者 180px */
}

/* 在 .earth-card 样式块附近添加 */
.earth-card.custom-task {
  /* 自定义作业的特殊样式，比如加个底纹 */
  background-image: radial-gradient(#f1f1f1 1px, transparent 1px);
  background-size: 20px 20px;
}

.course-tag.is-custom {
  background: #e6fffb; /* 浅青色背景 */
  color: #00c9a7;
  border: 1px solid #b5f5ec;
}

.action-btn.disabled {
  background: #eee;
  color: #999;
  border-color: #ddd;
  cursor: not-allowed;
  &:hover {
    background: #eee;
    color: #999;
    border-color: #ddd;
  }
}
</style>