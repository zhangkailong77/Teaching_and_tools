<template>
  <div class="dashboard-container">
    <TeacherSidebar />

    <main class="main-content">
      <header class="top-bar">
        <div class="welcome-text">
          <h2>作业批改中心</h2>
          <p>当前共有 <strong class="highlight">{{ stats.pending_count }}</strong> 份作业待批改</p>
        </div>
        <button class="create-btn" @click="handleCreate">+ 发布自定义作业</button>
      </header>

      <div class="layout-grid">
        
        <!-- === 左侧：班级分组列表 (手风琴) === -->
        <div class="left-panel">
          <div class="panel-header">
            <h3>班级作业列表</h3>
            <div class="actions">
              <el-input v-model="searchText" placeholder="搜索作业..." prefix-icon="Search" style="width: 200px" />
            </div>
          </div>

          <div v-if="filteredGroups.length === 0" class="empty-state">
            <p>暂无相关作业任务</p>
          </div>

          <!-- 班级分组 -->
          <div class="class-group" v-for="group in filteredGroups" :key="group.class_id">
            
            <!-- 班级标题行 (点击折叠) -->
            <div class="group-header" @click="toggleGroup(group)">
              <div class="gh-left">
                <span class="arrow" :class="{ open: group.isExpanded }">▶</span>
                <span class="c-name">{{ group.class_name }}</span>
                <span class="badge" v-if="group.pending_count > 0">{{ group.pending_count }} 待批</span>
              </div>
              <div class="gh-right">
                <span class="total">共 {{ group.assignments.length }} 个任务</span>
              </div>
            </div>

            <!-- 作业列表 (展开区域) -->
            <div class="group-body" v-show="group.isExpanded">
              <div class="hw-item" v-for="item in group.assignments" :key="item.id">
                <!-- 左侧信息 -->
                <div class="hw-info">
                  <div class="tags">
                    <span class="course-tag">{{ item.course_name }}</span>
                    <span v-if="isExpired(item.deadline)" class="status-tag expired">已截止</span>
                  </div>
                  <h4>{{ item.title }}</h4>
                  <div class="meta">截止: {{ formatDate(item.deadline) }}</div>
                </div>

                <!-- 进度条 -->
                <div class="hw-progress">
                  <div class="bar-container">
                    <div class="segment graded" :style="{ flex: item.stats.graded }" title="已批改"></div>
                    <div class="segment submitted" :style="{ flex: item.stats.submitted }" title="待批改"></div>
                    <div class="segment unsubmitted" :style="{ flex: item.stats.unsubmitted }" title="未交"></div>
                  </div>
                  <div class="bar-legend">
                    <span class="val orange">{{ item.stats.submitted }} 待批</span>
                    <span class="sep">/</span>
                    <span class="val gray">{{ item.stats.total }} 总数</span>
                  </div>
                </div>

                <!-- 操作栏 -->
                <div class="hw-action">
                  <!-- ✅ 新增：查看成绩按钮 -->
                  <button class="btn-text stats-btn" @click="toggleStats(item.id)">
                    {{ expandedTaskId === item.id ? '收起' : '成绩概览' }}
                  </button>
                  
                  <button class="btn-grade" @click="handleGrade(item.id)">进入批改</button>
                </div>

                <!-- ✅ 新增：内嵌分析组件 (独占一行) -->
                <!-- 使用 v-if 确保只有展开时才渲染组件和发请求 -->
                <div class="stats-row-full" v-if="expandedTaskId === item.id">
                  <AssignmentStats :assignmentId="item.id" />
                </div>               
              </div>
            </div>
          </div>
        </div>

        <!-- === 右侧：数据看板 (双图表) === -->
        <div class="right-panel-dashboard">
          
          <!-- 图表 1: 整体状态分布 (饼图) -->
          <div class="chart-card">
            <h4>📊 批改进度概览</h4>
            <div ref="pieChartRef" class="chart-box"></div>
          </div>

          <!-- 图表 2: 班级提交率排行 (条形图) -->
          <div class="chart-card">
            <h4>🏆 班级提交率排行</h4>
            <div ref="barChartRef" class="chart-box" style="height: 250px;"></div>
          </div>

        </div>
      </div>

      <CustomHomeworkDrawer 
        v-model="showCreateDrawer" 
        @success="handleCreateSuccess"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, onActivated } from 'vue';
import TeacherSidebar from '@/components/TeacherSidebar.vue';
import { getTeacherHomeworkStats, getTeacherHomeworkList, type HomeworkStatsV2, type ClassHomeworkGroup } from '@/api/homework';
import * as echarts from 'echarts';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import AssignmentStats from '@/components/AssignmentStats.vue';
import CustomHomeworkDrawer from '@/components/CustomHomeworkDrawer.vue'; 

const route = useRoute();
const userStore = useUserStore();
const router = useRouter();

// 状态
const stats = ref<HomeworkStatsV2>({ pending_count: 0, pie_data: { submitted:0, graded:0, unsubmitted:0 }, rank_data: [] });
const classGroups = ref<ClassHomeworkGroup[]>([]);
const searchText = ref('');
// ✅ 2. 定义控制抽屉显示的状态
const showCreateDrawer = ref(false);

// 图表 Ref
const pieChartRef = ref<HTMLElement | null>(null);
const barChartRef = ref<HTMLElement | null>(null);

// 2. 定义状态：当前展开的作业ID (默认 null)
const expandedTaskId = ref<number | null>(null);

  // 3. 切换展开函数
const toggleStats = (id: number) => {
  if (expandedTaskId.value === id) {
    expandedTaskId.value = null; // 收起
  } else {
    expandedTaskId.value = id;   // 展开
  }
};

// 初始化
onMounted(async () => {
  await loadData();
  
  // ✅ 修改点：检查 URL 参数
  const cid = route.query.class_id;
  if (cid) {
    // 逻辑：如果传了 class_id，我们可以把其他的班级都折叠，只展开这个
    classGroups.value.forEach(group => {
      group.isExpanded = (group.class_id === Number(cid));
    });
    
    // 如果有平滑滚动需求，也可以滚动到对应位置
  }
});

onActivated(() => {
  loadData();
});

const loadData = async () => {
  // 1. 加载统计
  const s = await getTeacherHomeworkStats();
  stats.value = s;
  userStore.pendingHomeworkCount = s.pending_count;
  initPieChart(s.pie_data);
  initBarChart(s.rank_data);

  // 2. 加载列表
  const list = await getTeacherHomeworkList();
  // 默认全部展开
  classGroups.value = list.map(g => ({ ...g, isExpanded: true }));
};

// 筛选逻辑
const filteredGroups = computed(() => {
  if (!searchText.value) return classGroups.value;
  // 简单的模糊搜索：只要班级名或下面的作业名包含关键字就显示
  return classGroups.value.filter(g => 
    g.class_name.includes(searchText.value) || 
    g.assignments.some(a => a.title.includes(searchText.value))
  );
});

// 交互
const toggleGroup = (group: ClassHomeworkGroup) => {
  group.isExpanded = !group.isExpanded;
};
const handleGrade = (id: number) => {
  router.push(`/dashboard/teacher/homeworks/${id}`);
};
const handleCreate = () => {
  showCreateDrawer.value = true;
};

const handleCreateSuccess = () => {
  // 重新加载列表，这样刚发布的作业就会显示出来
  loadData(); 
};

// 工具函数
const formatDate = (d: string) => d ? new Date(d).toLocaleDateString() : '无限制';
const isExpired = (d: string) => d && new Date(d) < new Date();

// --- 图表初始化 ---
const initPieChart = (data: any) => {
  if (!pieChartRef.value) return;
  const chart = echarts.init(pieChartRef.value);
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: '0%', left: 'center' },
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
      avoidLabelOverlap: false,
      label: { show: false },
      data: [
        { value: data.graded, name: '已批改', itemStyle: { color: '#00c9a7' } },
        { value: data.submitted, name: '待批改', itemStyle: { color: '#ff9f43' } },
        { value: data.unsubmitted, name: '未提交', itemStyle: { color: '#eee' } } // 可选
      ]
    }]
  });
};

const initBarChart = (data: any[]) => {
  if (!barChartRef.value) return;
  const chart = echarts.init(barChartRef.value);
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', max: 100 },
    yAxis: { type: 'category', data: data.map(i => i.class_name).reverse() },
    series: [{
      type: 'bar',
      data: data.map(i => i.rate).reverse(),
      itemStyle: { color: '#00c9a7', borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  });
};
</script>

<style scoped lang="scss">
$primary: #00c9a7;
$bg: #f5f6fa;
$text-dark: #2d3436;

.dashboard-container { display: flex; width: 100vw; height: 100vh; background-color: $bg; font-family: 'Inter', sans-serif; overflow: hidden; }
.main-content { flex: 1; padding: 30px 40px; overflow-y: auto; display: flex; flex-direction: column; gap: 25px; }

/* 头部 */
.top-bar { display: flex; justify-content: space-between; align-items: flex-end; 
  .welcome-text h2 { font-size: 24px; margin-bottom: 5px; color: $text-dark; }
  .highlight { color: #ff9f43; font-size: 18px; }
  .create-btn { background: $primary; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; &:hover { filter: brightness(0.9); } }
}

/* 布局 */
.layout-grid { display: grid; grid-template-columns: 1fr 320px; gap: 30px; }

/* 左侧列表 */
.left-panel { background: white; border-radius: 16px; padding: 20px; min-height: 500px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; h3 { font-size: 18px; margin: 0; } }

.class-group { margin-bottom: 15px; border: 1px solid #eee; border-radius: 12px; overflow: hidden;
  .group-header { background: #fafafa; padding: 12px 15px; display: flex; justify-content: space-between; cursor: pointer; user-select: none; &:hover { background: #f0fdfa; }
    .gh-left { display: flex; align-items: center; gap: 10px; font-weight: bold; font-size: 15px;
      .arrow { transition: transform 0.2s; font-size: 12px; color: #999; &.open { transform: rotate(90deg); } }
      .badge { background: #ff9f43; color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px; }
    }
    .gh-right { font-size: 12px; color: #999; }
  }

  .group-body { padding: 10px; 
    .hw-item { 
      display: flex; 
      align-items: center; 
      padding: 15px; 
      border-bottom: 1px solid #f5f5f5; 
      gap: 20px; 
      flex-wrap: wrap; 
      &:last-child { border-bottom: none; }

      .stats-row-full {
        width: 100%;       /* 占满整行宽度 */
        margin-top: 5px;   /* 与上面内容隔开一点 */
        flex-basis: 100%;  /* 强制换行 */
        animation: fadeIn 0.3s ease;
      }

      .stats-btn {
        background: none; border: none; cursor: pointer; color: #999; font-size: 13px; margin-right: 15px;
        &:hover { color: $primary; text-decoration: underline; }
      }

      .hw-info { width: 250px; 
        h4 { margin: 5px 0; font-size: 15px; } 
        .meta { font-size: 12px; color: #999; }
        .course-tag { background: #e0f2f1; color: $primary; font-size: 10px; padding: 2px 5px; border-radius: 4px; margin-right: 5px; }
        .expired { background: #fee; color: #f56c6c; font-size: 10px; padding: 2px 5px; border-radius: 4px; margin-left: 5px; }
      }
      .hw-progress { flex: 1; 
        .bar-container { height: 8px; background: #eee; border-radius: 4px; display: flex; overflow: hidden; }
        .segment.graded { background: $primary; } .segment.submitted { background: #ff9f43; }
        .bar-legend { display: flex; justify-content: flex-end; font-size: 12px; margin-top: 4px; gap: 5px; .orange { color: #ff9f43; font-weight: bold; } }
      }
      .btn-grade { padding: 6px 15px; background: white; border: 1px solid $primary; color: $primary; border-radius: 6px; cursor: pointer; font-size: 12px; &:hover { background: $primary; color: white; } }
    }
  }
}

/* 右侧看板 */
.right-panel-dashboard { display: flex; flex-direction: column; gap: 20px; }
.chart-card { background: white; padding: 20px; border-radius: 16px; h4 { margin: 0 0 15px; font-size: 15px; border-left: 4px solid $primary; padding-left: 10px; } .chart-box { height: 200px; } }
</style>