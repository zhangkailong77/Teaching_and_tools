<template>
  <div class="dashboard-container">
    <StudentSidebar />

    <main class="main-content">
      <!-- 顶部 Header -->
      <div class="page-header">
        <div class="header-left">
          <h2>考试大厅</h2>
          <p>管理考试任务，检测学习成果</p>
        </div>
        <div class="header-right">
          <div class="stat-pill">
            <span class="label">本周已参加</span>
            <span class="val">{{ stats.week_finished_count }}</span>
          </div>
          <div class="stat-pill highlight">
            <span class="label">待考试</span>
            <span class="val">{{ ongoingCount }}</span>
          </div>
        </div>
      </div>

      <div class="layout-grid">
        
        <!-- === 左侧：考试任务列表 (70%) === -->
        <div class="left-panel">
          <!-- 风格统一的 Tabs -->
          <div class="custom-tabs">
            <div 
              v-for="tab in tabs" 
              :key="tab.value" 
              class="tab-item" 
              :class="{ active: currentTab === tab.value }"
              @click="currentTab = tab.value"
            >
              {{ tab.icon }} {{ tab.label }}
              <span class="badge" v-if="tab.count > 0">{{ tab.count }}</span>
            </div>
          </div>

          <div class="task-list-wrapper" v-loading="loading">
            <div v-if="filteredList.length === 0" class="empty-state">
              <div class="empty-content">
                <!-- 使用一个具有设计感的插画图标 -->
                <p class="main-msg">暂无考试任务</p>
              </div>
            </div>

            <div 
              v-else 
              class="earth-card exam-mode" 
              v-for="exam in filteredList" 
              :key="exam.id"
              :class="{ 'urgent': isTimeUrgent(exam.end_time) && exam.my_status <= 0 }"
            >
              <!-- 左侧状态条 -->
              <div class="status-bar" :class="getStatusClass(exam)"></div>

              <div class="card-content">
                <div class="meta-row">
                  <span class="course-tag">{{ getStatusText(exam) }}</span>
                  <span class="deadline-tag">
                    📅 {{ formatRange(exam.start_time, exam.end_time) }}
                  </span>
                </div>
                
                <h3 class="task-title">{{ exam.title }}</h3>
                
                <div class="bottom-row">
                  <div class="status-text">
  
                    <!-- ✅ 修改点 1：只有当 (状态是2) 且 (时间已结束) 时，才显示分数 -->
                    <span v-if="exam.my_status === 2 && isTimeEnded(exam)" class="text-score">
                      最终得分: <strong>{{ exam.my_score }}</strong>
                    </span>

                    <!-- ✅ 修改点 2：如果 (状态是2) 但 (时间没结束)，显示占位文字 -->
                    <span v-else-if="exam.my_status === 2 && !isTimeEnded(exam)" class="text-wait">
                      ⏳ 成绩待公布
                    </span>

                    <!-- 其他逻辑保持不变 -->
                    <span v-else-if="isTimeUrgent(exam.end_time) && exam.my_status <= 0" class="text-brown">
                      🚨 即将截止入场
                    </span>
                    
                    <span v-else class="text-gray">时长: {{ exam.duration }} 分钟</span>
                  </div>
                  
                  <div class="btn-group">
                    <!-- 情况 A: 可以进入考试 (未开始或进行中) -->
                    <button 
                      v-if="canEnter(exam)" 
                      class="action-btn primary" 
                      @click="handleEnterExam(exam)"
                    >
                      {{ exam.my_status === 0 ? '继续考试' : '进入考试' }}
                    </button>

                    <!-- 情况 B: 已交卷 (待批改 或 已出分) -->
                    <button 
                      v-else-if="exam.my_status === 1 || exam.my_status === 2" 
                      class="action-btn outline" 
                      :class="{ 'disabled': exam.my_status === 2 && !isTimeEnded(exam) }"
                      :disabled="exam.my_status === 2 && !isTimeEnded(exam)"
                      @click="handleViewResult(exam)"
                    >
                      {{ getBtnText(exam) }}
                    </button>

                    <!-- 情况 C: 其他情况 (如已过期且未参加) -->
                    <button 
                      v-else 
                      class="action-btn disabled" 
                      disabled
                    >
                      入口关闭
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- === 右侧：考试数据看板 (30%) === -->
        <div class="right-panel-dashboard">
          
          <!-- 1. 考试完成率 -->
          <div class="dashboard-card chart-card">
            <h4>考试完成情况</h4>
            <div ref="chartRef" class="chart-container"></div>
            <div class="chart-legend">
              <div class="legend-item"><span class="dot done"></span> 已参加</div>
              <div class="legend-item"><span class="dot todo"></span> 待考试</div>
            </div>
          </div>

          <!-- 2. 最近一场考试 -->
          <div class="dashboard-card urgent-card">
            <h4>📅 最近安排</h4>
            <div class="urgent-list" v-if="recentExam">
              <div class="u-item">
                <div class="u-left">
                  <!-- 确保类名正确 -->
                  <div class="u-title">{{ recentExam.title }}</div>
                  <div class="u-date">{{ recentExam.duration }}min | 总分{{ recentExam.total_score }}</div>
                </div>
                <div class="u-right">
                  <!-- 按钮使用 mini-btn 类 -->
                  <button class="mini-btn" @click="handleEnterExam(recentExam)">Go</button>
                </div>
              </div>
            </div>
            <div v-else class="no-urgent">近期无考试安排</div>
          </div>

          <!-- 3. 考试成绩趋势 -->
          <div class="dashboard-card trend-card">
            <h4>📈 考试成绩趋势</h4>
            <div ref="lineChartRef" class="line-chart-container"></div>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import StudentSidebar from '@/components/StudentSidebar.vue';
import { getStudentExams, enterExam } from '@/api/exam';
import { ElMessage, ElMessageBox } from 'element-plus';
import * as echarts from 'echarts';
import { useRouter } from 'vue-router';
const router = useRouter();

// 状态
const loading = ref(false);
const examList = ref<any[]>([]);
const currentTab = ref('ongoing');
const chartRef = ref<HTMLElement | null>(null);
const lineChartRef = ref<HTMLElement | null>(null);

const stats = ref({
  week_finished_count: 0,
  score_trend: [
    { date: '01-01', score: 85 },
    { date: '01-05', score: 92 },
    { date: '01-10', score: 78 }
  ] // 暂时 Mock，后续从后端获取
});

const handleEnterExam = async (exam: any) => {
  try {
    // 考前弹窗确认
    await ElMessageBox.confirm(
      `确定要进入《${exam.title}》吗？考试时长 ${exam.duration} 分钟，进入后请勿随意切屏。`,
      '考前确认',
      { 
        confirmButtonText: '立即开始', 
        cancelButtonText: '我再等等', 
        type: 'info',
        roundButton: true
      }
    );
    
    // 2. 调用后端接口，告知服务器学生已“开考”，创建 ExamRecord 记录
    // 即使学生不交卷，后端也能知道他什么时候进场的
    await enterExam(exam.id);

    // 3. ✅ 执行跳转
    // 我们把标题、时长、总分等信息通过 query 传过去，减少 take.vue 里的初始请求压力
    router.push({
      path: `/dashboard/student/exams/take/${exam.id}`,
      query: {
        title: exam.title,
        duration: exam.duration,
        total_score: exam.total_score,
        pass_score: exam.pass_score
      }
    });

  } catch (e) {
    // 用户取消或接口报错，不执行跳转
    console.log('取消进入或进入失败', e);
  }
};

const tabs = computed(() => [
  { label: '全部', value: 'all', icon: '📂', count: 0 },
  { label: '进行中', value: 'ongoing', icon: '📝', count: ongoingCount.value },
  { label: '已参加', value: 'finished', icon: '✅', count: 0 },
]);

onMounted(() => {
  fetchExams();
  initCharts();
});

const fetchExams = async () => {
  loading.value = true;
  try {
    const res = await getStudentExams();
    examList.value = res;
    updateCharts();
  } finally {
    loading.value = false;
  }
};

// 过滤逻辑
const filteredList = computed(() => {
  if (currentTab.value === 'ongoing') return examList.value.filter(e => canEnter(e));
  if (currentTab.value === 'finished') return examList.value.filter(e => e.my_status >= 1);
  return examList.value;
});

const ongoingCount = computed(() => examList.value.filter(e => canEnter(e)).length);
const finishedCount = computed(() => examList.value.filter(e => e.my_status >= 1).length);
const recentExam = computed(() => examList.value.find(e => canEnter(e)));

// 工具函数
const isTimeOngoing = (exam: any) => {
  const now = new Date().getTime();
  return now >= new Date(exam.start_time).getTime() && now <= new Date(exam.end_time).getTime();
};
const canEnter = (exam: any) => exam.my_status <= 0 && isTimeOngoing(exam);
const isTimeUrgent = (endTime: string) => {
  const diff = new Date(endTime).getTime() - new Date().getTime();
  return diff > 0 && diff < 1000 * 3600 * 24; // 24小时内
};

const getStatusClass = (exam: any) => {
  if (exam.my_status === 2) return 'graded';
  if (exam.my_status === 1) return 'submitted';
  return isTimeOngoing(exam) ? 'ongoing' : 'ended';
};

const getStatusText = (exam: any) => {
  const isEnded = new Date().getTime() > new Date(exam.end_time).getTime();
  
  const map: any = { 
    graded: isEnded ? '已出分' : '待公布', // ✅ 优化文案
    submitted: '待批改', 
    ongoing: '进行中', 
    pending: '未开始', 
    ended: '已结束' 
  };
  return map[getStatusClass(exam)];
};

const getBtnText = (e: any) => {
  const isEnded = new Date().getTime() > new Date(e.end_time).getTime();

  // 状态 2 = 已批改/系统自动批完
  if (e.my_status === 2) {
    if (isEnded) {
      return '查看成绩'; // ✅ 只有时间到了才显示这个
    } else {
      return '等待出分'; // ✅ 时间没到，显示等待
    }
  }
  
  if (e.my_status === 1) return '待批改'; // 含主观题，老师还没批
  
  if (canEnter(e)) return e.my_status === 0 ? '继续考试' : '进入考试';
  
  return '入口关闭';
};

const formatRange = (s: string, e: string) => `${s.substring(5, 16)} ~ ${e.substring(5, 16)}`;

// ECharts 逻辑
let pieChart: any = null;
let lineChart: any = null;

const initCharts = () => {
  if (chartRef.value) pieChart = echarts.init(chartRef.value);
  if (lineChartRef.value) lineChart = echarts.init(lineChartRef.value);
  updateCharts();
};

const updateCharts = () => {
  if (pieChart) {
    const total = examList.value.length || 1;
    const rate = Math.round((finishedCount.value / total) * 100);
    pieChart.setOption({
      series: [{
        type: 'pie', radius: ['60%', '80%'],
        label: { show: true, position: 'center', formatter: `${rate}%` },
        data: [
          { value: finishedCount.value, itemStyle: { color: '#00c9a7' } },
          { value: total - finishedCount.value, itemStyle: { color: '#947456' } }
        ]
      }]
    });
  }
  if (lineChart) {
    // A. 数据处理：筛选已出分(status=2)的考试，并按时间正序排列
    const completedExams = examList.value
      .filter(e => {
        // ✅ 核心修改：增加 isTimeEnded(e) 判断
        // 只有：(已批改) 且 (有提交时间) 且 (考试已结束/成绩已公布) 的才算进图表
        return e.my_status === 2 && e.submit_time && isTimeEnded(e);
      })
      .sort((a, b) => new Date(a.submit_time).getTime() - new Date(b.submit_time).getTime()); // 按时间升序

    // B. 提取 X轴 (日期) 和 Y轴 (分数) 数据
    const xData = completedExams.map(e => {
       // 格式化日期为 "01-13"
       const d = new Date(e.submit_time);
       return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    });
    
    const yData = completedExams.map(e => e.my_score);

    // C. 配置 ECharts
    lineChart.setOption({
      tooltip: { 
        trigger: 'axis',
        formatter: '{b}<br/>得分: {c}分'
      },
      grid: { 
        top: '15%', bottom: '10%', left: '10%', right: '5%', 
        containLabel: true 
      },
      xAxis: {
        type: 'category',
        data: xData,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#999', fontSize: 10 }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
      },
      series: [{
        data: yData,
        type: 'line',
        smooth: true, // 平滑曲线
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#00c9a7' }, // 线条颜色
        areaStyle: {
          // 渐变填充区域
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 201, 167, 0.4)' },
            { offset: 1, color: 'rgba(0, 201, 167, 0.01)' }
          ])
        }
      }]
    });
  }
};

const handleViewResult = (exam: any) => {
  const isEnded = new Date().getTime() > new Date(exam.end_time).getTime();
  
  if (!isEnded) {
    ElMessage.warning('考试尚未结束，成绩将在截止时间后统一公布。');
    return;
  }
  
  router.push(`/dashboard/student/exams/result/${exam.id}`);
};

const isTimeEnded = (exam: any) => {
  if (!exam.end_time) return false;
  return new Date().getTime() > new Date(exam.end_time).getTime();
};
</script>

<style scoped lang="scss">
$primary: #00c9a7;
$earth-brown: #947456;
$earth-dark: #2A5850;
$earth-light: #F9F7F2;
$text-main: #333;
$text-light: #999;

.dashboard-container { display: flex; width: 100vw; height: 100vh; background-color: #f5f6fa; overflow: hidden; }
.main-content { flex: 1; padding: 30px 40px; overflow-y: auto; }

.page-header {
  display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px;
  h2 { 
    font-size: 24px; 
    color: $earth-dark; // ✅ 使用大地深绿色
    margin: 0; 
    font-weight: bold;
  }
  p { 
    font-size: 14px; 
    color: $text-light; 
    margin-top: 5px; 
  }
  
  .header-right { display: flex; gap: 15px; }
  .stat-pill {
    background: white; padding: 6px 15px; border-radius: 20px; display: flex; align-items: center; gap: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    .label { font-size: 12px; color: $text-light; }
    .val { font-weight: bold; font-size: 16px; color: $earth-dark; }
    &.highlight { 
      border: 1px solid $earth-brown; 
      .val { color: $earth-brown; } 
    }
  }
}

.layout-grid { display: grid; grid-template-columns: 1fr 320px; gap: 30px; }

.custom-tabs {
  display: flex; gap: 10px; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px;
  .tab-item {
    padding: 8px 20px; cursor: pointer; font-weight: 600; color: #999; border-radius: 8px; position: relative;
    &.active { color: white; background: $earth-dark; box-shadow: 0 4px 10px rgba(42, 88, 80, 0.2); }
    .badge { position: absolute; top: -5px; right: -2px; background: $primary; color: white; font-size: 10px; padding: 1px 5px; border-radius: 10px; }
  }
}

.earth-card {
  background: white; border-radius: 12px; padding: 20px; margin-bottom: 15px;
  position: relative; overflow: hidden; border: 1px solid #f0f0f0; transition: all 0.2s ease;
  &:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(148, 116, 86, 0.1); }
  
  .status-bar { position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: #ccc; 
    &.ongoing { background: $primary; }
    &.graded { background: #00b894; }
  }
  &.urgent .status-bar { background: $earth-brown; }

  .card-content { padding-left: 15px; }
  .meta-row { display: flex; align-items: center; gap: 10px; font-size: 12px; margin-bottom: 8px;
    .course-tag { background: $earth-light; color: $earth-dark; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
  }
  .task-title { margin: 0 0 15px; font-size: 17px; color: #333; }
  
  .bottom-row {
    display: flex; justify-content: space-between; align-items: center;
    .status-text { font-size: 13px; font-weight: 500; .text-score { color: $primary; font-size: 15px; } 
    .text-wait {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      
      /* 极淡的灰背景 */
      background-color: #f2f3f5;
      /* 深灰文字，清晰但不刺眼 */
      color: #606266;
      /* 细微的边框 */
      border: 1px solid #e4e7ed;
      
      padding: 3px 10px;
      border-radius: 12px; /* 胶囊圆角 */
      font-size: 12px;
      font-weight: 500;
      letter-spacing: 0.5px;
    }
    }
    .action-btn { 
      padding: 6px 20px; 
      border-radius: 20px; 
      font-size: 13px; 
      font-weight: 600; 
      cursor: pointer; 
      transition: all 0.2s;

      /* 实心风格 (进入考试) */
      &.primary {
        background: $primary; 
        color: white; 
        border: 1px solid $primary;
        &:hover { opacity: 0.9; transform: translateY(-1px); }
      }

      /* 描边风格 (查看成绩) */
      &.outline {
        background: white; 
        color: $primary; 
        border: 1px solid $primary;
        &:hover:not(.disabled) { background: #f0fdfa; }
      }

      /* 禁用风格 */
      &.disabled {
        border-color: #ddd; 
        background: #f5f5f5;
        color: #ccc; 
        cursor: not-allowed;
        &:hover { transform: none; background: #f5f5f5; }
      }
    }
  }
}

.right-panel-dashboard { display: flex; flex-direction: column; gap: 20px; }
.dashboard-card {
  background: white; border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  h4 { margin: 0 0 15px; font-size: 15px; color: $earth-dark; border-left: 4px solid $earth-brown; padding-left: 10px; }
}

.chart-container { height: 160px; }
.line-chart-container { height: 180px; }
.chart-legend { display: flex; justify-content: center; gap: 15px; font-size: 12px; .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; } .dot.done { background: $primary; } .dot.todo { background: $earth-brown; } }

.urgent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 5px;

  .u-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 12px;
    border-bottom: 1px dashed #f0f0f0;
    
    &:last-child {
      border: none;
      padding-bottom: 0;
    }

    .u-left {
      flex: 1;
      overflow: hidden;
      
      .u-title {
        font-size: 14px;
        font-weight: 600; /* ✅ 标题加粗 */
        color: #333;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 4px;
      }

      .u-date {
        font-size: 12px;
        color: $earth-brown; /* 大地褐色 */
        opacity: 0.8;
      }
    }

    .mini-btn {
      margin-left: 15px;
      padding: 4px 14px;
      border-radius: 6px;
      border: 1px solid $earth-brown; /* 褐色边框 */
      background: white;
      color: $earth-brown;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        background: $earth-brown;
        color: white;
        box-shadow: 0 4px 8px rgba(148, 116, 86, 0.2);
      }
    }
  }
}

.no-urgent {
  text-align: center;
  color: #ccc;
  font-size: 13px;
  padding: 20px 0;
}

/* 找到并替换原来的 .empty-state 样式 */

.empty-state {
  width: 100%;
  min-height: 400px; /* ✅ 保证一定的高度，让它在左侧面板居中 */
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 16px;
  border: 1px dashed #e0e0e0; /* 虚线边框增加呼吸感 */
  margin-top: 10px;

  .empty-content {
    text-align: center;
    animation: fadeIn 0.6s ease;

    img {
      width: 160px; /* 图标适当加大 */
      opacity: 0.8;
      margin-bottom: 20px;
      filter: drop-shadow(0 10px 15px rgba(0,0,0,0.05)); /* 给图片一点投影 */
    }

    .main-msg {
      font-size: 18px;
      font-weight: 600;
      color: $earth-dark; /* 使用你的深森林绿 */
      margin-bottom: 10px;
    }

    .sub-msg {
      font-size: 14px;
      color: #a4b0be; /* 柔和的灰色 */
      letter-spacing: 0.5px;
    }
  }
}

/* 简单的进入动画 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>