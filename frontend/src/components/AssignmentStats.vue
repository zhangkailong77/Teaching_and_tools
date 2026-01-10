<template>
  <div class="stats-panel" v-loading="loading">
    
    <!-- 左侧：图表区 -->
    <div class="chart-section">
      <h4>📊 分数段分布</h4>
      <div ref="chartRef" class="mini-chart"></div>
      <div class="summary-text">
        <span>最高分: <strong>{{ maxScore }}</strong></span>
        <span>平均分: <strong>{{ avgScore }}</strong></span>
        <span>不及格: <strong class="red">{{ failCount }}</strong></span>
      </div>
    </div>

    <!-- 右侧：名单区 -->
    <div class="list-section">
      <div class="list-header">
        <h4>📑 成绩名单
            <span class="expand-icon" @click="showFullList = true" title="放大查看">⤢</span>
        </h4>
        <div class="filters">
          <span :class="{active: filter==='all'}" @click="filter='all'">全部</span>
          <span :class="{active: filter==='fail'}" @click="filter='fail'">不及格</span>
          <span :class="{active: filter==='none'}" @click="filter='none'">未交</span>
        </div>
      </div>
      
      <div class="student-table-wrapper">
        <table class="simple-table">
          <thead><tr><th>姓名</th><th>分数</th><th>状态</th></tr></thead>
          <tbody>
            <tr v-for="stu in filteredList" :key="stu.student_id">
              <td>{{ stu.student_name }}</td>
              <td>
                <span v-if="stu.status===2" :class="getScoreClass(stu.score)">{{ stu.score }}</span>
                <span v-else class="gray">-</span>
              </td>
              <td>
                <span class="status-dot" :class="getStatusClass(stu.status)"></span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ✅ 新增：成绩详情大弹窗 -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showFullList" @click.self="showFullList = false">
        <div class="modal-content" style="width: 700px;"> <!-- 宽一点 -->
            <div class="modal-header">
            <h3>📊 成绩详情列表</h3>
            <div class="header-actions">
                <button class="btn-export" @click="exportExcel">导出 Excel</button>
            </div>
            </div>
            
            <div class="modal-body table-scroll-area" style="height: 400px; overflow: auto;">
            <table class="simple-table full-width">
                <thead>
                <tr>
                    <th>姓名</th>
                    <th>学号</th>
                    <th>提交时间</th>
                    <th class="sortable" @click="handleSort('score')">
                        分数
                        <span class="sort-icon">
                            <span :class="{ active: sortKey==='score' && sortOrder==='asc' }">▲</span>
                            <span :class="{ active: sortKey==='score' && sortOrder==='desc' }">▼</span>
                        </span>
                    </th>
                    <th>状态</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="stu in sortedFullList" :key="stu.student_id">
                    <td>{{ stu.student_name }}</td>
                    <td>{{ stu.student_number }}</td>
                    <td>{{ stu.submitted_at ? new Date(stu.submitted_at).toLocaleString() : '-' }}</td>
                    <td>
                    <span v-if="stu.status===2" :class="getScoreClass(stu.score)">{{ stu.score }}</span>
                    <span v-else class="gray">-</span>
                    </td>
                    <td>
                    <span class="status-badge" :class="getStatusClass(stu.status)">
                        {{ ['未交','待批','已批'][stu.status] }}
                    </span>
                    </td>
                </tr>
                </tbody>
            </table>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { getAssignmentSubmissions, type GradingData, type SubmissionItem } from '@/api/homework';
import * as echarts from 'echarts';
import * as XLSX from 'xlsx'; 

// ✅ 新增状态
const showFullList = ref(false); // 控制大弹窗

// ✅ 新增：导出 Excel 函数
const exportExcel = () => {
  // 1. 准备数据：表头 + 内容
  const exportData = allStudents.value.map(s => ({
    '姓名': s.student_name,
    '学号': s.student_number,
    '分数': s.status === 2 ? s.score : (s.status === 1 ? '待批改' : '未交'),
    '提交时间': s.submitted_at ? new Date(s.submitted_at).toLocaleString() : '-'
  }));

  // 2. 生成工作簿
  const ws = XLSX.utils.json_to_sheet(exportData);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "成绩单");

  // 3. 下载文件
  XLSX.writeFile(wb, `作业成绩单_${props.assignmentId}.xlsx`);
};
// ----------

// 1. 定义排序状态
const sortKey = ref<'score' | 'submitted_at' | null>(null);
const sortOrder = ref<'asc' | 'desc'>('desc'); // 默认降序 (高分在前)

// 2. 修改排序函数
const handleSort = (key: 'score' | 'submitted_at') => {
  if (sortKey.value === key) {
    // 切换顺序: desc -> asc -> null (取消排序)
    if (sortOrder.value === 'desc') sortOrder.value = 'asc';
    else {
      sortKey.value = null; // 取消排序，恢复默认
      sortOrder.value = 'desc';
    }
  } else {
    // 新字段，默认降序
    sortKey.value = key;
    sortOrder.value = 'desc';
  }
};

// 3. 计算排序后的列表 (修改原来的 filteredList 或新建一个 sortedFullList)
// 我们这里新建一个 sortedFullList 专门给大弹窗用
const sortedFullList = computed(() => {
  // 先浅拷贝一份
  let list = [...allStudents.value];
  
  if (sortKey.value) {
    list.sort((a, b) => {
      const valA = sortKey.value === 'score' ? (a.score || 0) : new Date(a.submitted_at || 0).getTime();
      const valB = sortKey.value === 'score' ? (b.score || 0) : new Date(b.submitted_at || 0).getTime();
      
      return sortOrder.value === 'asc' ? valA - valB : valB - valA;
    });
  }
  
  return list;
});
// ----





const props = defineProps<{ assignmentId: number }>();

const loading = ref(false);
const allStudents = ref<SubmissionItem[]>([]);
const chartRef = ref<HTMLElement | null>(null);
const filter = ref('all');

// 统计数据
const maxScore = computed(() => Math.max(...allStudents.value.map(s => s.score || 0)));
const avgScore = computed(() => {
  const graded = allStudents.value.filter(s => s.status === 2);
  if (!graded.length) return 0;
  const sum = graded.reduce((a, b) => a + (b.score || 0), 0);
  return Math.round(sum / graded.length);
});
const failCount = computed(() => allStudents.value.filter(s => s.status === 2 && (s.score || 0) < 60).length);

// 列表过滤
const filteredList = computed(() => {
  if (filter.value === 'fail') return allStudents.value.filter(s => s.status === 2 && (s.score || 0) < 60);
  if (filter.value === 'none') return allStudents.value.filter(s => s.status === 0);
  return allStudents.value;
});

onMounted(async () => {
  loading.value = true;
  try {
    const res = await getAssignmentSubmissions(props.assignmentId);
    allStudents.value = res.students;
    initChart();
  } catch(e) { console.error(e); }
  finally { loading.value = false; }
});

// 图表渲染
const initChart = () => {
  if (!chartRef.value) return;
  const myChart = echarts.init(chartRef.value);
  
  // 计算分布
  const distribution = [0, 0, 0, 0, 0]; // <60, 60-69, 70-79, 80-89, 90-100
  allStudents.value.forEach(s => {
    if (s.status !== 2 || s.score === undefined) return;
    const score = s.score;
    if (score < 60) distribution[0]++;
    else if (score < 70) distribution[1]++;
    else if (score < 80) distribution[2]++;
    else if (score < 90) distribution[3]++;
    else distribution[4]++;
  });

  myChart.setOption({
    grid: { top: 30, bottom: 20, left: 30, right: 10 },
    xAxis: { type: 'category', data: ['<60', '60+', '70+', '80+', '90+'], axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ 
        type: 'bar', 
        data: distribution, 
        itemStyle: { color: '#00c9a7', 
        borderRadius: [4, 4, 0, 0] }, 
        barWidth: '40%',
        label: {
            show: true,
            position: 'top',
            color: '#333',
            fontSize: 12,
            fontWeight: 'bold',
            formatter: (params: any) => params.value > 0 ? params.value : ''
      }
    }]
  });
};

const getScoreClass = (s?: number) => {
  if (s === undefined) return '';
  if (s < 60) return 'score-fail';
  if (s >= 90) return 'score-good';
  return 'score-normal';
};
const getStatusClass = (s: number) => ['gray', 'orange', 'green'][s];
</script>

<style scoped lang="scss">
$primary: #00c9a7;
$bg-soft: #f0fdfa; /* 极淡的青绿色背景 */
$text-main: #333;
$text-dark: #2d3436; 
$text-light: #999;

.stats-panel {
  display: flex;
  gap: 30px;
  height: 260px; /* 稍微加高一点 */
  padding: 20px 25px;
  background: $bg-soft; 
  border-radius: 12px;
  /* 去掉边框，用柔和的内阴影或纯色 */
  box-shadow: inset 0 0 20px rgba(0, 201, 167, 0.05);
  margin-top: 15px;
  
  /* 左侧图表区 */
  .chart-section {
    flex: 1; 
    display: flex; 
    flex-direction: column;
    
    h4 { 
      margin: 0 0 15px; 
      font-size: 14px; 
      color: $text-dark; 
      font-weight: 700;
      display: flex; align-items: center; gap: 8px;
      &::before { content: ''; display: block; width: 4px; height: 14px; background: $primary; border-radius: 2px; }
    }
    
    .mini-chart { flex: 1; }
    
    .summary-text {
      margin-top: 10px;
      display: flex; 
      gap: 20px; 
      font-size: 13px; 
      color: #666;
      background: white;
      padding: 8px 15px;
      border-radius: 20px;
      align-self: flex-start; /* 靠左 */
      box-shadow: 0 2px 10px rgba(0,0,0,0.03);
      
      strong { color: $text-dark; font-weight: 800; font-family: 'DIN Alternate', sans-serif; font-size: 15px; }
      .red { color: #ff6b6b; }
    }
  }

  /* 右侧名单区 */
  .list-section {
    width: 320px; 
    display: flex; 
    flex-direction: column; 
    background: white; /* 独立的白卡片 */
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05); /* 悬浮感 */
    border: 1px solid rgba(0,0,0,0.02);

    .list-header {
      display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
      h4 { margin: 0; font-size: 14px; color: #333; }
      .filters {
        background: #f5f5f5; border-radius: 4px; padding: 2px; display: flex;
        span {
          font-size: 11px; padding: 2px 8px; cursor: pointer; color: #888; border-radius: 3px; transition: all 0.2s;
          &:hover { color: #555; }
          &.active { background: white; color: $primary; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        }
      }
    }
    
    .student-table-wrapper {
      flex: 1; overflow-y: auto;
      /* 隐藏滚动条但保留功能 */
      &::-webkit-scrollbar { width: 4px; }
      &::-webkit-scrollbar-thumb { background: #eee; border-radius: 2px; }
    }
    
    .simple-table {
      width: 100%; border-collapse: separate; border-spacing: 0 4px; /* 行间距 */
      
      th { text-align: left; color: #bbb; font-size: 12px; padding: 5px 10px; font-weight: normal; }
      
      td { 
        padding: 8px 10px; color: #555; font-size: 13px; 
        background: #f9fbfb; /* 极淡的条纹底 */
        &:first-child { border-top-left-radius: 6px; border-bottom-left-radius: 6px; font-weight: 500; }
        &:last-child { border-top-right-radius: 6px; border-bottom-right-radius: 6px; }
      }
      
      /* 分数样式 */
      .score-fail { color: #ff6b6b; font-weight: bold; }
      .score-good { color: $primary; font-weight: bold; }
      .score-normal { color: #333; }
      
      /* 状态点 */
      .status-dot { 
        display: inline-block; width: 6px; height: 6px; border-radius: 50%; 
        &.gray { background: #eee; } 
        &.orange { background: #ff9f43; } 
        &.green { background: $primary; box-shadow: 0 0 5px rgba(0, 201, 167, 0.4); }
      }
    }
  }
}

/* 放大图标 */
.expand-icon {
  margin-left: 8px; cursor: pointer; color: #999; font-size: 14px;
  &:hover { color: $primary; transform: scale(1.1); }
}

/* 导出按钮 */
.btn-export {
  display: flex; align-items: center; gap: 6px;
  background-color: #fff;
  border: 1px solid #d9d9d9;
  color: #666;
  padding: 6px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  
  &:hover {
    color: $primary;
    border-color: $primary;
    background-color: #f0fdfa;
  }
}

/* 弹窗头部布局 */
.header-actions { display: flex; align-items: center; }

/* 大表格样式 */
.full-width { width: 100%; }
.status-badge {
  font-size: 11px; padding: 2px 6px; border-radius: 4px;
  &.gray { background: #eee; color: #999; }
  &.orange { background: #fff7e6; color: #fa8c16; }
  &.green { background: #f6ffed; color: #52c41a; }
}

.modal-content {
  background-color: #ffffff !important; /* ✅ 强制纯白，不透明 */
  width: 700px;
  max-width: 90vw; /* 防止手机端溢出 */
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2); /* 加深阴影 */
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: popUp 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28);
  position: relative; /* 确保 z-index 生效 */
  z-index: 10000; /* ✅ 比遮罩层更高 */
}

.modal-overlay {
  position: fixed; 
  top: 0; left: 0; 
  width: 100vw; height: 100vh; /* 确保占满屏幕 */
  background: rgba(0, 0, 0, 0.5); 
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 9999; /* ✅ 调高层级 */
  display: flex; justify-content: center; align-items: center; 
  backdrop-filter: blur(4px);
}

/* 弹窗内的滚动区域 */
.table-scroll-area {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #eee; /* 外边框 */
  border-radius: 8px;
}

/* 完整版大表格样式 */
.simple-table.full-width {
  width: 100%;
  border-collapse: collapse; /* 去掉单元格间隙 */
  
  /* 表头 */
  thead {
    position: sticky; top: 0; z-index: 1; /* 固定表头 */
    background-color: #f8f9fa; /* 浅灰背景 */
    
    th {
      text-align: left;
      padding: 15px;
      font-size: 13px;
      color: #666;
      font-weight: 600;
      border-bottom: 2px solid #e0e0e0;
    }
  }
  
  /* 表体 */
  tbody {
    tr {
      transition: background-color 0.2s;
      
      /* 斑马纹 */
      &:nth-child(even) { background-color: #fcfcfc; }
      
      &:hover { background-color: #f0fdfa; } /* 悬停变淡青色 */
      
      td {
        padding: 12px 15px;
        font-size: 14px;
        color: #333;
        border-bottom: 1px solid #f0f0f0;
      }
    }
  }
}

/* 可排序表头 */
th.sortable {
  cursor: pointer;
  user-select: none;
  &:hover { background-color: #eee; }
  
  .sort-icon {
    display: inline-flex; flex-direction: column; margin-left: 5px; font-size: 10px; line-height: 8px; vertical-align: middle; color: #ccc; gap: 2px;
    
    span.active { color: $primary; } /* 激活时变青色 */
  }
}
</style>