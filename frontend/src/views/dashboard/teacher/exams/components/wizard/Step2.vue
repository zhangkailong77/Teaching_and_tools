<template>
  <div class="step-container">
    
    <!-- 模式A: 手动组卷 (仿照参考图的左右分栏布局) -->
    <div v-if="form.mode === 1" class="manual-layout">
      
      <!-- 左侧：题库选择器 -->
      <div class="left-panel">
        <div class="panel-header">
          <span class="title">📚 题库选题</span>
          <el-input 
            v-model="filter.keyword" 
            placeholder="搜题目..." 
            prefix-icon="Search"
            clearable 
            size="small" 
            style="width: 140px" 
            @keyup.enter="fetchBank(true)" 
          />
        </div>
        
        <!-- 简单的题型过滤 Tabs -->
        <div class="filter-tabs">
          <span 
            v-for="type in ['all', 'single', 'multiple', 'judge', 'blank', 'essay']" 
            :key="type" 
            class="tab-item"
            :class="{ active: filter.type === type }"
            @click="filter.type = type; fetchBank(true)"
          >
            {{ getShortTypeLabel(type) }}
          </span>
        </div>

        <div class="question-list" v-loading="loading && page === 1">
          <div class="q-item" v-for="q in bankQuestions" :key="q.id" :class="{ 'is-selected': isSelected(q.id!) }" @click="toggleQuestion(q)">
            <div class="q-header-mini">
              <div class="badges">
                <span v-for="t in q.tags" :key="t" class="tag-point">#{{ t }}</span>
                <span class="tag-type" :class="q.type">{{ getShortTypeLabel(q.type) }}</span>
                <span class="tag-diff" :class="'lv-'+q.difficulty">{{ getDiffLabel(q.difficulty) }}</span>
              </div>

              <div v-if="isSelected(q.id!)" class="selected-icon">
                <el-icon><CircleCheckFilled /></el-icon>
              </div>
            </div>

            <!-- 内容：题干 -->
            <div class="q-content" :title="getTextContent(q.content)">
                {{ getTextContent(q.content) }}
            </div>

            <div class="q-options-preview" v-if="['single', 'multiple'].includes(q.type) && q.options">
                <div v-for="opt in q.options" :key="opt.label" class="opt-line">
                    <span class="opt-key">{{ opt.label }}.</span>
                    <span class="opt-text">{{ opt.text }}</span>
                </div>
            </div>

            <!-- 答案与解析预览区 (默认显示，或鼠标悬停显示) -->
            <div class="q-answer-preview">
              <span class="label">参考答案:</span> 
              <div class="val-box">{{ formatAnswer(q.answer) }}</div>
            </div>
          </div>

          <div class="load-more-section">
            <div v-if="hasMore">
            <el-button 
                link 
                type="primary" 
                :loading="loading" 
                @click="handleLoadMore"
                class="load-more-btn"
            >
                {{ loading ? '正在加载...' : '加载更多题目...' }}
            </el-button>
            </div>
            <div v-else-if="bankQuestions.length > 0" class="no-more-text">
            --- 已经到底啦 ---
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：试卷预览区 (A4纸风格) -->
      <div class="right-panel">
        <div class="paper-preview">
          <!-- 试卷头 -->
          <div class="paper-header">
            <h2 class="exam-title">{{ form.title || '未命名试卷' }}</h2>
            <div class="exam-meta">
              <span>总分: {{ totalScore }}</span>
              <span class="divider">|</span>
              <span>共 {{ form.questions.length }} 题</span>
            </div>
          </div>

          <div class="divider-line"></div>

          <!-- 题目列表 -->
          <div class="paper-body">
            <div v-if="form.questions.length === 0" class="empty-paper">
              <img src="https://cdni.iconscout.com/illustration/premium/thumb/empty-state-2130362-1800926.png" width="150" />
              <p>请从左侧选择题目，开始组卷</p>
            </div>

            <transition-group name="list" v-else>
            <div 
              class="paper-item" 
              v-for="(item, index) in form.questions" 
              :key="item.id"
            >
              <!-- 左侧边栏：题号与操作 -->
              <div class="item-sidebar">
                <div class="idx-badge">第{{ index + 1 }}题</div>
                <div class="ops">
                  <el-input-number 
                    v-model="item.score" 
                    :min="1" 
                    :max="100" 
                    controls-position="right"
                    size="small" 
                    style="width: 70px" 
                  />
                  <div class="icon-group">
                    <el-icon class="op-icon" @click="moveQuestion(index, -1)" title="上移"><Top /></el-icon>
                    <el-icon class="op-icon" @click="moveQuestion(index, 1)" title="下移"><Bottom /></el-icon>
                    <el-icon class="op-icon delete" @click="removeQuestion(index)" title="删除"><Delete /></el-icon>
                  </div>
                </div>
              </div>

              <!-- 右侧：题目内容展示 -->
              <div class="item-content">
                <div class="q-stem">
                    <!-- 题型标签 -->
                    <span class="type-label">[{{ getShortTypeLabel(item.raw?.type || 'single') }}]</span>
                    <!-- 题目正文 -->
                    <span v-html="item.raw?.content || item.title"></span>
                </div>

                <!-- 1. 选择题 (单选/多选) -->
                <div class="q-options" v-if="item.raw?.type === 'single' || item.raw?.type === 'multiple'">
                    <div v-for="opt in item.raw.options" :key="opt.label" class="opt-row">
                    <span class="opt-key">{{ opt.label }}.</span>
                    <span class="opt-val">{{ opt.text }}</span>
                    </div>
                </div>

                <!-- 2. 判断题 (强制显示 A.正确 B.错误) -->
                <div class="q-options" v-else-if="item.raw?.type === 'judge'">
                    <div class="opt-row"><span class="opt-key">A.</span><span class="opt-val">正确</span></div>
                    <div class="opt-row"><span class="opt-key">B.</span><span class="opt-val">错误</span></div>
                </div>

                <!-- 3. 填空题 (显示横线) -->
                <div class="q-answer-placeholder blank-area" v-else-if="item.raw?.type === 'blank'">
                    <div class="blank-line-display">_______________</div>
                </div>

                <!-- 4. 简答题 (显示一个明显的答题框) -->
                <div class="q-answer-placeholder essay-area" v-else-if="item.raw?.type === 'essay'">
                    <div class="essay-input-box">
                    <span>答题区</span>
                    </div>
                </div>
              </div>
            </div>
            </transition-group>
          </div>
        </div>
      </div>
    </div>

    <!-- 模式B: 随机组卷 (策略配置) -->
    <div v-else class="random-layout">
      
      <!-- 左侧：策略配置区 -->
      <div class="config-panel">
        
        <!-- 1. 顶部标题和按钮 -->
        <div class="panel-header">
          <div class="title">🎲 抽题策略配置</div>
          <button class="btn-add-premium" @click="addStrategy">
            <el-icon><Plus /></el-icon> 添加策略
          </button>
        </div>

        <!-- 2. 图表统计区 (放在顶部，有数据时显示) -->
        <div class="chart-wrapper" v-show="totalCountRandom > 0">
          <div class="chart-title">试卷结构分析</div>
          
          <div class="analysis-box">
            <!-- 左：图表 -->
            <div class="chart-left">
              <div class="chart-container" ref="chartRef"></div>
            </div>
            
            <!-- 右：详细统计列表 -->
            <div class="stats-right">
              <div class="stat-header">
                <span class="col-type">类型</span>
                <span class="col-count">题数</span>
                <span class="col-score">分值</span>
              </div>
              <div class="stat-list">
                <div class="stat-row" v-for="item in typeStatistics" :key="item.label">
                  <span class="col-type label">
                    <span class="dot"></span> {{ item.label }}
                  </span>
                  <span class="col-count val">{{ item.count }}</span>
                  <span class="col-score val score">{{ item.score }}</span>
                </div>
              </div>
              <div class="stat-footer">
                <span class="col-type">总计</span>
                <span class="col-count">-</span>
                <span class="col-score highlight">{{ totalScoreRandom }}</span>
              </div>
            </div>
          </div>

          <!-- 下方知识点条形图 -->
          <div class="knowledge-analysis">
            <div class="sub-title">知识点覆盖分布</div>
            <div class="tag-chart-container" ref="chartRefTag"></div>
          </div>
        </div>

        <!-- 3. 策略卡片列表 -->
        <div class="strategy-list">
          <div v-if="form.random_config.length === 0" class="empty-tip">
            点击右上角添加策略，开始智能组卷
          </div>

          <div v-else class="strategy-card" v-for="(item, index) in form.random_config" :key="index">
            <!-- 筛选条件行 -->
            <div class="row filters">
              <el-select v-model="item.type" size="small" style="width: 90px" @change="checkStock(index)">
                <el-option label="单选题" value="single" />
                <el-option label="多选题" value="multiple" />
                <el-option label="判断题" value="judge" />
                <el-option label="填空题" value="blank" />
                <el-option label="简答题" value="essay" />
              </el-select>
              
              <el-rate v-model="item.difficulty" :max="3" @change="checkStock(index)" />
              
              <el-select 
                v-model="item.tag" 
                placeholder="知识点(可选)" 
                clearable 
                size="small" 
                filterable 
                allow-create 
                style="width: 120px"
                @change="checkStock(index)"
              >
                <el-option v-for="t in tagOptions" :key="t" :label="t" :value="t" />
              </el-select>

              <!-- 删除按钮放在这里 -->
              <el-button type="danger" link icon="Delete" class="del-btn" @click="removeStrategy(index)" />
            </div>

            <!-- 库存状态行 -->
            <div class="row stock-info">
              <span v-if="item._loading" class="loading">正在查询库存...</span>
              <span v-else class="stock-text" :class="{'warning': item._stock < item.count}">
                <el-icon><Refresh /></el-icon> 
                题库现有: <strong>{{ item._stock }}</strong> 题
                <span v-if="item._stock < item.count" class="err-msg">库存不足!</span>
              </span>
            </div>

            <!-- 抽取数量行 -->
            <div class="row settings">
              <div class="set-item">
                <span>抽取</span>
                <el-input-number v-model="item.count" :min="1" :max="item._stock || 999" size="small" style="width: 90px" />
                <span>题</span>
              </div>
              <div class="set-item">
                <span>每题</span>
                <el-input-number v-model="item.score" :min="1" size="small" style="width: 90px" />
                <span>分</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：结构蓝图与分析 -->
      <div class="blueprint-panel">
        <div class="paper-preview">
          <!-- 试卷头 -->
          <div class="paper-header">
            <h2 class="exam-title">{{ form.title || '智能组卷预览' }}</h2>
            <div class="preview-actions">
              <div class="exam-meta">
                <span v-if="isGenerated">实际总分: <b class="real">{{ totalScore }}</b></span>
                <span v-else>预估总分: {{ totalScoreRandom }}</span>
                <span class="divider">|</span>
                <span>共 {{ isGenerated ? form.questions.length : totalCountRandom }} 题</span>
              </div>

              <el-button 
                  type="primary" 
                  :loading="isGenerating"
                  @click="handleGeneratePreview"
                  class="btn-generate"
              >
                  <el-icon class="icon"><Refresh /></el-icon>
                  {{ isGenerated ? '换一批题目' : '生成试卷预览' }}
              </el-button>
            </div>
          </div>
          
          <div class="divider-line"></div>

          <div class="paper-body">
            
            <!-- 状态 A: 已生成预览 (显示真实的题目样式) -->
            <div v-if="isGenerated" class="real-list">
               <div class="paper-item" v-for="(item, index) in form.questions" :key="index">
                  <div class="item-sidebar">
                    <div class="idx-badge">第{{ index + 1 }}题</div>
                    <div class="score-badge">{{ item.score }}分</div>
                  </div>
                  <div class="item-content">
                    <div class="q-stem">
                       <span class="type-label">[{{ getShortTypeLabel(item.raw?.type) }}]</span>
                       <span v-html="item.raw?.content"></span>
                    </div>
                    <!-- 1. 选择题 -->
                    <div class="q-options" v-if="['single','multiple'].includes(item.raw?.type)">
                      <div v-for="opt in item.raw.options" :key="opt.label" class="opt-row">
                        <span class="opt-key">{{ opt.label }}.</span> {{ opt.text }}
                      </div>
                    </div>
                    <!-- 2. 判断题 -->
                    <div class="q-options" v-else-if="item.raw?.type === 'judge'">
                       <div class="opt-row"><span class="opt-key">A.</span> 正确</div>
                       <div class="opt-row"><span class="opt-key">B.</span> 错误</div>
                    </div>
                    <!-- 3. 填空/简答题 -->
                    <div class="q-answer-placeholder blank-area" v-else-if="item.raw?.type === 'blank'">
                      <div class="blank-line-display">________________________________________________</div>
                    </div>
                    <div class="q-answer-placeholder essay-area" v-else>
                      <div class="essay-input-box">答题区</div>
                    </div>
                  </div>
               </div>
            </div>

            <!-- 状态 B: 未生成 (显示骨架屏/蓝图) -->
            <div v-else class="blueprint-list">
              <div v-if="previewList.length === 0" class="empty-paper">
                <img src="https://cdni.iconscout.com/illustration/premium/thumb/automation-processing-2890184-2408375.png" width="120" />
                <p>暂无题目，请在左侧配置策略</p>
              </div>

              <div v-else class="preview-list">
                <div 
                  v-for="(item, index) in previewList" 
                  :key="index" 
                  class="paper-item placeholder-item"
                >
                  <div class="item-sidebar">
                    <div class="idx-badge">第{{ index + 1 }}题</div>
                    <div class="score-badge">{{ item.score }}分</div>
                  </div>

                  <div class="item-content">
                    <div class="q-stem">
                      <span class="type-label">[{{ getShortTypeLabel(item.type) }}]</span>
                      <span class="placeholder-text">
                        [系统将随机抽取] 
                        <span class="tag" v-if="item.tag">#{{ item.tag }}</span>
                        <span class="diff">难度:{{ getDiffLabel(item.difficulty) }}</span>
                      </span>
                    </div>
                    <!-- 骨架条 -->
                    <div class="q-options skeleton" v-if="['single','multiple'].includes(item.type)">
                      <div class="sk-line" style="width: 60%"></div>
                      <div class="sk-line" style="width: 40%"></div>
                      <div class="sk-line" style="width: 50%"></div>
                      <div class="sk-line" style="width: 30%"></div>
                    </div>
                    <div class="q-options skeleton" v-else-if="item.type === 'judge'">
                      <div class="sk-line" style="width: 15%"></div>
                      <div class="sk-line" style="width: 15%"></div>
                    </div>
                    <div class="q-options skeleton" v-else>
                      <div class="sk-line" style="width: 100%; height: 24px;"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch, nextTick } from 'vue'
import { getQuestions, getAllTags, checkQuestionStock, previewRandomGeneration, type QuestionItem } from '@/api/exam'
import { Plus, Close, Delete, Search, Top, Bottom, CircleCheckFilled, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const props = defineProps<{ modelValue: any }>()
const emit = defineEmits(['update:modelValue'])

const getDiffLabel = (diff: number) => ['简单', '中等', '困难'][diff - 1] || '未知'
const formatAnswer = (ans: any) => {
  if (ans === null || ans === undefined || ans === '') return '暂无答案'
  if (Array.isArray(ans)) return ans.join('、')
  if (typeof ans === 'boolean') return ans ? '正确' : '错误'
  return ans // 字符串直接返回
}

const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// --- 通用 ---
const tagOptions = ref<string[]>([])

// ===========================
// 模式 A: 手动组卷
// ===========================
const loading = ref(false)
const bankQuestions = ref<QuestionItem[]>([])
const page = ref(1)
const filter = reactive({ keyword: '', type: 'all' })
const hasMore = ref(true)

const handleLoadMore = () => {
  if (loading.value || !hasMore.value) return;
  page.value++;
  fetchBank();
};

// 获取题库
const fetchBank = async (isReset = false) => {
  if (isReset) {
    page.value = 1;
    bankQuestions.value = [];
    hasMore.value = true;
  }
  
  if (!hasMore.value && !isReset) return;

  loading.value = true;
  try {
    const skipValue = (page.value - 1) * 10;

    const res = await getQuestions({ 
      skip: skipValue, 
      limit: 10, 
      keyword: filter.keyword || undefined,
      type: filter.type === 'all' ? undefined : filter.type
    });
    
    if (res.items.length < 10) {
      hasMore.value = false;
    } else {
      hasMore.value = true;
    }

    if (page.value === 1) {
      bankQuestions.value = res.items;
    } else {
      bankQuestions.value.push(...res.items);
    }
  } catch (error) {
    console.error("加载题库失败", error);
  } finally {
    loading.value = false;
  }
};

// 检查是否已在试卷中
const isSelected = (id: number) => form.value.questions.some((q: any) => q.id === id)

// ✅ 2. 新增：切换选择状态的函数
const toggleQuestion = (q: QuestionItem) => {
  const index = form.value.questions.findIndex((item: any) => item.question_id === q.id)
  
  if (index > -1) {
    form.value.questions.splice(index, 1)
  } else {
    addQuestion(q)
  }
}

// 添加题目到试卷
const addQuestion = (q: QuestionItem) => {
  form.value.questions.push({
    id: q.id, 
    question_id: q.id, 
    title: q.content,
    score: 2,
    raw: q 
  })
}

// 移除题目
const removeQuestion = (index: number) => {
  form.value.questions.splice(index, 1)
}

// 移动题目顺序
const moveQuestion = (index: number, step: number) => {
  const newIndex = index + step
  if (newIndex < 0 || newIndex >= form.value.questions.length) return
  
  const temp = form.value.questions[index]
  form.value.questions[index] = form.value.questions[newIndex]
  form.value.questions[newIndex] = temp
}

// 计算总分
const totalScore = computed(() => form.value.questions.reduce((sum: number, q: any) => sum + q.score, 0))

// 辅助：提取纯文本预览
const getTextContent = (html: string) => {
  if (!html) return ''
  return html.replace(/<[^>]+>/g, '')
}

const getShortTypeLabel = (type: string) => {
  const map: any = { all: '全部', single: '单选', multiple: '多选', judge: '判断', blank: '填空', essay: '简答' }
  return map[type] || type
}

// ===========================
// 模式 B: 随机组卷
// ===========================
const chartRef = ref<HTMLElement | null>(null)
let myChart: echarts.ECharts | null = null
const chartRefTag = ref<HTMLElement | null>(null)
let tagChart: echarts.ECharts | null = null
const isGenerated = ref(false)
const isGenerating = ref(false)

const addStrategy = () => {
  form.value.random_config.push({
    type: 'single',
    difficulty: 1,
    tag: '',
    count: 5,
    score: 2,
    _stock: 0, 
    _loading: false
  })
  checkStock(form.value.random_config.length - 1)
}

const removeStrategy = (index: number) => {
  form.value.random_config.splice(index, 1)
}

// 核心：查询库存
const checkStock = async (index: number) => {
  const item = form.value.random_config[index]
  item._loading = true
  try {
    const res = await checkQuestionStock({
      type: item.type,
      difficulty: item.difficulty,
      tag: item.tag || undefined
    })
    item._stock = res.count
  } catch (e) {
    console.error(e)
  } finally {
    item._loading = false
    updateChart() 
  }
}

const totalCountRandom = computed(() => form.value.random_config.reduce((sum: number, c: any) => sum + c.count, 0))
const totalScoreRandom = computed(() => form.value.random_config.reduce((sum: number, c: any) => sum + (c.count * c.score), 0))

// 试卷
const previewList = computed(() => {
  const list: any[] = []
  form.value.random_config.forEach((strategy: any) => {
    // 策略里说抽N题，我们就生成N个占位符
    for (let i = 0; i < strategy.count; i++) {
      list.push({
        type: strategy.type,
        score: strategy.score,
        difficulty: strategy.difficulty,
        tag: strategy.tag
      })
    }
  })
  return list
})

watch(() => form.value.random_config, () => {
  isGenerated.value = false
  if (totalCountRandom.value > 0) {
    nextTick(() => {
      updateChart()
      myChart?.resize() 
      tagChart?.resize()
    })
  }
}, { deep: true })

// ✅ 新增：计算各题型的详细统计 (用于左侧图表右边的文字展示)
const typeStatistics = computed(() => {
  // 初始化统计对象
  const stats: Record<string, { count: number; score: number; label: string }> = {
    single: { count: 0, score: 0, label: '单选' },
    multiple: { count: 0, score: 0, label: '多选' },
    judge: { count: 0, score: 0, label: '判断' },
    blank: { count: 0, score: 0, label: '填空' },
    essay: { count: 0, score: 0, label: '简答' }
  }

  // 遍历配置累加
  form.value.random_config.forEach((c: any) => {
    if (stats[c.type]) {
      stats[c.type].count += (c.count || 0)
      stats[c.type].score += (c.count || 0) * (c.score || 0)
    }
  })

  // 过滤掉数量为 0 的题型，只返回有数据的
  return Object.values(stats).filter(item => item.count > 0)
})

// 图表渲染 (难度分布)
const updateChart = () => {
  if (!chartRef.value) return
  // 确保 DOM 已经显示
  if (chartRef.value.clientWidth === 0) return

  if (!myChart) myChart = echarts.init(chartRef.value)
  
  let easy = 0, medium = 0, hard = 0
  form.value.random_config.forEach((c: any) => {
    // 确保 count 是数字
    const count = Number(c.count) || 0
    if (c.difficulty === 1) easy += count
    if (c.difficulty === 2) medium += count
    if (c.difficulty === 3) hard += count
  })

  // 如果全是0，清空
  if (easy + medium + hard === 0) {
     myChart.clear()
     return
  }

  myChart.setOption({
    // 移除 ECharts 自带的标题，改用 DOM 布局更灵活
    // title: { ... }, 
    tooltip: { trigger: 'item' },
    legend: { show: false }, // 隐藏图例，空间太小放不下
    series: [{
      type: 'pie', 
      radius: ['55%', '80%'], // 稍微调大一点环的厚度
      center: ['50%', '50%'], // 居中显示
      avoidLabelOverlap: false,
      label: { 
        show: true, 
        position: 'center',
        formatter: '{total|' + totalCountRandom.value + '}\n{text|总题量}',
        rich: {
          total: { fontSize: 20, fontWeight: 'bold', color: '#333' },
          text: { fontSize: 10, color: '#999', padding: [4, 0, 0, 0] }
        }
      },
      data: [
        { value: easy, name: '简单', itemStyle: { color: '#52c41a' } },
        { value: medium, name: '中等', itemStyle: { color: '#fa8c16' } },
        { value: hard, name: '困难', itemStyle: { color: '#f5222d' } }
      ]
    }]
  })

  // --- 图表 2: 知识点分布 (新增) ---
  if (!tagChart) tagChart = echarts.init(chartRefTag.value)

  // 1. 统计知识点 (保持不变)
  const tagCounts: Record<string, number> = {}
  form.value.random_config.forEach((c: any) => {
    const label = c.tag || '未分类'
    if (!tagCounts[label]) tagCounts[label] = 0
    tagCounts[label] += (c.count || 0)
  })

  // 2. 转换并排序 (保持不变)
  const tagData = Object.keys(tagCounts).map(key => ({
    name: key,
    value: tagCounts[key]
  })).sort((a, b) => a.value - b.value)

  const yAxisData = tagData.map(item => item.name)
  const seriesData = tagData.map(item => item.value)

  // ✅ 定义一组高级配色 (莫兰迪色系 + 主题色)
  const colors = ['#00c9a7', '#8e44ad', '#3498db', '#f39c12', '#e74c3c', '#34495e']

  // 3. 设置配置项 (深度优化版)
  tagChart.setOption({
    title: { show: false },
    grid: { 
      top: '5%', 
      bottom: '5%', 
      left: '90', 
      right: '15%', 
      containLabel: false 
    },
    tooltip: { 
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      padding: [8, 12],
      textStyle: { color: '#333', fontSize: 12 },
      extraCssText: 'box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 6px;'
    },
    xAxis: { type: 'value', show: false },
    yAxis: { 
      type: 'category', 
      data: yAxisData,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { 
        color: '#606266', 
        fontSize: 12,
        fontWeight: 'bold', 
        
        width: 80,          
        overflow: 'truncate', 
        align: 'left',      
        margin: 80,        
        
        lineHeight: 20
      }
    },
    series: [{
      type: 'bar',
      data: seriesData,
      barWidth: 10,
      showBackground: true,
      backgroundStyle: {
        color: '#f0f2f5',
        borderRadius: [0, 5, 5, 0]
      },
      itemStyle: { 
        color: function(params: any) {
          return colors[params.dataIndex % colors.length]
        },
        borderRadius: [0, 5, 5, 0] 
      },
      label: {
        show: true,
        position: 'right',
        color: '#999',
        fontSize: 11,
        formatter: '{c}题'
      }
    }]
  })
}

// ✅ 核心功能：点击生成预览
const handleGeneratePreview = async () => {
  if (form.value.random_config.length === 0) return ElMessage.warning('请先添加策略')
  
  isGenerating.value = true
  try {
    const res = await previewRandomGeneration(form.value.random_config)
    form.value.questions = res
    
    isGenerated.value = true
    
    ElMessage.success(`成功生成 ${res.length} 道题目，可继续点击刷新更换`)
  } catch (e) {
    console.error(e)
    ElMessage.error('生成预览失败')
  } finally {
    isGenerating.value = false
  }
}

// --- 初始化 ---
onMounted(async () => {
  if (form.value.mode === 1) fetchBank()
  if (form.value.mode === 2) {
    const tags = await getAllTags()
    tagOptions.value = tags
    form.value.random_config.forEach((_: any, idx: number) => checkStock(idx))
    nextTick(() => updateChart())
  }
})
</script>

<style scoped lang="scss">
$primary: #00c9a7;
$bg-color: #f5f7fa;

.step-container {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 手动布局 */
.manual-layout {
  display: flex; height: 100%; background: $bg-color;
  
  /* 左侧侧边栏 */
  .left-panel {
    width: 500px; background: white; display: flex; flex-direction: column;
    border-right: 1px solid #eee; flex-shrink: 0;

    .panel-header {
      padding: 15px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center;
      .title { font-weight: 600; color: #333; }
    }

    .filter-tabs {
      display: flex; gap: 5px; padding: 10px 15px; overflow-x: auto;
      .tab-item {
        font-size: 12px; padding: 4px 10px; border-radius: 12px; cursor: pointer; color: #666; background: #f5f5f5; white-space: nowrap; transition: all 0.2s;
        &.active { background: rgba(0, 201, 167, 0.1); color: $primary; font-weight: bold; }
        &:hover { color: $primary; }
      }
    }

    .load-more-section {
        text-align: center;
        padding: 20px 0 10px;
        
        .load-more-btn {
            font-size: 13px;
            font-weight: 500;
            color: $primary;
            transition: all 0.2s;
            
            &:hover {
            opacity: 0.8;
            text-decoration: underline;
            }
        }
        
        .no-more-text {
            font-size: 12px;
            color: #ccc;
            letter-spacing: 1px;
        }
    }

    .question-list {
      flex: 1; overflow-y: auto; padding: 0 15px 15px; scroll-behavior: smooth;
      
      .q-item {
        position: relative;
        cursor: pointer;
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 12px; 
        background: #fff; 
        border: 1px solid #f0f0f0;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        
        &:hover { 
          border-color: $primary; 
          background-color: rgba(0, 201, 167, 0.02);
        }

         &.is-selected {
            border-color: $primary;
            background-color: rgba(0, 201, 167, 0.05); /* 淡淡的青绿背景 */
            box-shadow: 0 4px 12px rgba(0, 201, 167, 0.1);
            
            /* 让左侧有一个醒目的指示条 */
            &::before {
            content: '';
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 4px;
            background: $primary;
            border-radius: 8px 0 0 8px;
            }
        }

        .q-header-mini {
        margin-bottom: 8px;
        .selected-icon {
          color: $primary;
          font-size: 18px;
        }
        .badges {
            display: flex; gap: 6px; align-items: center; flex-wrap: wrap;
            
            .tag-point { font-size: 10px; color: $primary; background: rgba(0, 201, 167, 0.08); padding: 1px 5px; border-radius: 3px; }
            
            .tag-type { font-size: 10px; padding: 1px 5px; border-radius: 3px; background: #f0f2f5; color: #606266; 
            &.single { background: #e6f7ff; color: #1890ff; } /* 也可以换成你的主题色系 */
            }
            
            .tag-diff { font-size: 10px; font-weight: bold; 
            &.lv-1 { color: #52c41a; } &.lv-2 { color: #fa8c16; } &.lv-3 { color: #f5222d; }
            }
        }
        }

        .q-content {
            font-size: 13px; color: #333; line-height: 1.5;
            // display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; 
            padding-right: 30px; /* 留出按钮位置 */
        }

        .q-options-preview {
            margin-top: 8px;
            background: #f9f9f9;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            color: #666;
            
            .opt-line { margin-bottom: 2px; }
            .opt-key { font-weight: bold; margin-right: 4px; }
        }

        .q-answer-preview {
            margin-top: 8px;
            font-size: 12px;
            color: $primary; /* 你的主题色 */
            background: rgba(0, 201, 167, 0.05);
            padding: 8px 10px;
            border-radius: 4px;
            display: flex; 
            flex-direction: column; /* 上下排列：标签在上，内容在下 */
            gap: 4px;

            .label {
              color: $primary; 
              font-weight: bold;
            }

            .val-box {
                color: #333; /* 答案内容用深色，看得清 */
                white-space: pre-wrap; /* ✅ 关键：保留换行符，并允许自动换行 */
                word-break: break-all; /* 防止长单词撑破 */
                line-height: 1.5;
            }
        }

        /* 添加按钮绝对定位在右侧垂直居中 */
        .btn-add {
            position: absolute; right: 15px; top: 50%; transform: translateY(-50%);
            background-color: $primary; border-color: $primary;
            transition: all 0.2s;
            
            &:disabled { background-color: #a0cfff; border-color: #a0cfff; opacity: 0.6; }
        }
      }
    }
  }

  /* 右侧预览区 (A4纸风格) */
  .right-panel {
    flex: 1; padding: 20px; overflow-y: auto; display: flex; justify-content: center; 

    .paper-preview {
      width: 100%; max-width: 1000px; background: white; margin: 0 auto;
      box-shadow: 0 4px 20px rgba(0,0,0,0.05); padding: 40px 50px;
      border-radius: 4px; /* A4纸微圆角 */
      margin-bottom: 40px; /* 底部留白 */
      
      .paper-header {
        text-align: center; margin-bottom: 20px;
        .exam-title { font-size: 24px; color: #333; margin-bottom: 10px; }
        .exam-meta { color: #666; font-size: 14px; .divider { margin: 0 10px; color: #ddd; } }
      }

      .divider-line { height: 2px; background: #333; margin-bottom: 30px; }
    }
  }
}

/* 随机组卷布局 */
.random-layout {
  display: flex; height: 100%; background: $bg-color;
  
  /* 左侧配置面板 */
  .config-panel {
    width: 420px; /* 稍微宽一点放配置 */
    background: white; border-right: 1px solid #eee; display: flex; flex-direction: column;

    .chart-wrapper {
      height: auto !important;
      // min-height: 250px;
      border-top: 1px solid #f0f0f0;
      padding: 20px;
      background: #fff; /* 改为纯白背景更干净 */
      margin-top: auto;
      flex-shrink: 0;
      border-radius: 0 0 8px 8px; /* 底部圆角 */

    .chart-title {
      font-size: 14px; 
      font-weight: 700; 
      color: #333; 
      margin-bottom: 15px; 
      padding-left: 10px; 
      border-left: 4px solid $primary;
    }

    /* 左右布局容器 */
    .analysis-box {
      display: flex;
      align-items: stretch;
      gap: 20px; /* ✅ 增加间距 */
      height: 180px;

      /* 左侧图表 */
      .chart-left {
        flex: 0 0 40%; /* ✅ 固定占 40% 宽度 */
        .chart-container { height: 100%; width: 100%; }
      }

      /* 右侧统计列表 */
      .stats-right {
        flex: 1; /* ✅ 占据剩余空间 */
        display: flex;
        flex-direction: column;
        font-size: 13px;
        padding-left: 20px;
        border-left: 1px dashed #eee;

        /* 列宽控制 */
        .col-type { flex: 1; text-align: left; }
        .col-count { width: 60px; text-align: center; }
        .col-score { width: 60px; text-align: right; }

        .stat-item {
          display: flex;
          align-items: center;
          padding: 8px 0;
          
          .col-count, .col-score {
            text-align: center; // ✅ 确保数据内容也居中
          }
        }

        .stat-header {
          display: flex; 
          color: #999; 
          margin-bottom: 10px;
          padding-bottom: 5px;
          border-bottom: 1px solid #f5f5f5;
          font-size: 12px;
        }

        .stat-list {
          flex: 1; 
          overflow-y: auto; 
          
          .stat-row {
            display: flex; 
            align-items: center;
            margin-bottom: 8px; 
            color: #555;
            
            .label { 
              font-weight: 600; 
              color: #333; 
              display: flex; 
              align-items: center; 
              gap: 6px;
              
              .dot { /* 小圆点装饰 */
                width: 6px; height: 6px; 
                background: $primary; 
                border-radius: 50%; 
                opacity: 0.5;
              }
            }
            .score { color: #999; font-family: monospace; }
          }
        }

        .stat-footer {
          border-top: 1px solid #eee;
          padding-top: 10px;
          margin-top: 5px;
          display: flex;
          font-weight: bold;
          color: #333;
          .highlight { color: $primary; font-size: 16px; }
        }
      }
    }
    .knowledge-analysis {
      margin-top: 20px;
      padding-top: 15px;
      border-top: 1px dashed #eee; /* 虚线分隔 */

      .sub-title {
        font-size: 12px;
        font-weight: 600;
        color: #999;
        margin-bottom: 10px;
        padding-left: 5px;
      }

      .tag-chart-container {
        width: 100%;
        height: 120px; /* 给一个固定高度 */
      }
    }
    }
    
    .panel-header {
      padding: 15px 20px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center;
      .title { font-weight: 600; color: #333; }
    }

    .strategy-list {
      flex: 1; overflow-y: auto; padding: 20px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
      .empty-tip { text-align: center; color: #999; margin-top: 50px; font-size: 13px; }

      .strategy-card {
        background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 15px; margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02); transition: all 0.2s;
        &:hover { border-color: $primary; box-shadow: 0 4px 12px rgba(0, 201, 167, 0.08); }

        .row { display: flex; align-items: center; margin-bottom: 10px; &:last-child { margin-bottom: 0; } }
        
        .filters { 
          gap: 10px; 
          .del-btn { margin-left: auto; }
        }

        .stock-info {
          font-size: 12px; background: #f9f9f9; padding: 5px 10px; border-radius: 4px; color: #666;
          .loading { color: $primary; }
          .stock-text { display: flex; align-items: center; gap: 4px; strong { color: #333; } }
          .warning { color: #fa8c16; strong { color: #f5222d; } }
          .err-msg { color: #f5222d; margin-left: 5px; }
        }

        .settings {
          justify-content: space-between;
          .set-item { font-size: 13px; color: #666; display: flex; align-items: center; gap: 5px; }
        }
      }
    }
  }

  /* 右侧蓝图面板 (复用 A4 纸样式) */
  .blueprint-panel {
    flex: 1; padding: 20px; overflow-y: auto; display: flex; justify-content: center;
    
    .paper-preview {
      width: 100%; max-width: 800px; background: white; min-height: 800px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.05); padding: 40px 50px; border-radius: 4px;
      
      .paper-header {
        text-align: center; margin-bottom: 20px;
        .exam-title { font-size: 24px; color: #333; margin-bottom: 10px; }
        .exam-meta { color: #666; font-size: 14px; .divider { margin: 0 10px; color: #ddd; } }
      }
      .divider-line { height: 2px; background: #333; margin-bottom: 30px; }
    }
  }
}

/* ✅ 新增：列表平移过渡动画 */
.list-move {
  transition: transform 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}

/* 确保切换时的布局不会瞬间塌陷（可选优化） */
.list-leave-active {
  position: absolute;
}

.btn-add-premium {
  background: $primary;
  color: white;
  border: none;
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 4px 10px rgba(0, 201, 167, 0.2);
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 15px rgba(0, 201, 167, 0.3);
  }
  &:active { transform: translateY(0); }
}

.preview-list {
  .paper-item {
    display: flex; gap: 20px; margin-bottom: 30px; border-bottom: 1px dashed #eee; padding-bottom: 20px;
    
    .item-sidebar {
      width: 60px; text-align: center;
      .idx-badge { background: #333; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; margin-bottom: 5px; display: inline-block; }
      .score-badge { color: $primary; font-weight: bold; font-size: 12px; }
    }

    .item-content {
      flex: 1;
      .q-stem { 
        margin-bottom: 10px; font-size: 14px; 
        .type-label { color: $primary; font-weight: bold; margin-right: 8px; }
        .placeholder-text { 
          color: #999; font-style: italic; 
          .tag { background: #f0f2f5; padding: 2px 5px; border-radius: 4px; font-size: 11px; margin: 0 5px; font-style: normal; color: #666; }
          .diff { font-size: 11px; margin-left: 5px; color: #e6a23c; font-style: normal; }
        }
      }

      /* 骨架屏线条模拟选项 */
      .skeleton {
        margin-left: 10px; display: flex; flex-direction: column; gap: 8px;
        .sk-line {
          height: 14px; background: #f0f2f5; border-radius: 4px;
        }
      }
    }
  }
}

.empty-paper { text-align: center; margin-top: 100px; color: #ccc; img { opacity: 0.5; margin-bottom: 15px; } }

.preview-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-top: 10px;

  .btn-generate {
    background: linear-gradient(135deg, $primary 0%, color-mix(in srgb, $primary 90%, white 10%) 100%);
    border: none;
    padding: 10px 30px;
    border-radius: 20px;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0, 201, 167, 0.3);
    transition: all 0.3s;
    
    .icon { margin-right: 5px; transition: transform 0.5s; }

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0, 201, 167, 0.4);
      .icon { transform: rotate(180deg); }
    }
  }
}

.real { color: $primary; }

.paper-body {
  padding-bottom: 20px;
}

.paper-item {
  display: flex; 
  gap: 20px; 
  margin-bottom: 30px; 
  border-bottom: 1px dashed #eee; 
  padding-bottom: 20px;
  animation: fadeIn 0.5s ease;

  /* 左侧：题号与分数 */
  .item-sidebar {
    width: 60px; 
    flex-shrink: 0; 
    text-align: center;
    
    .idx-badge { 
      background: #333; 
      color: white; 
      padding: 2px 6px; 
      border-radius: 4px; 
      font-size: 12px; 
      margin-bottom: 5px; 
      display: inline-block; 
      font-weight: bold;
    }
    .score-badge { 
      color: $primary; 
      font-weight: bold; 
      font-size: 13px; 
    }
    
    /* 操作按钮 (手动模式会有) */
    .ops { 
      margin-top: 8px;
      display: flex; flex-direction: column; align-items: center; gap: 5px; 
      .icon-group { 
        display: flex; gap: 8px; 
        .op-icon { cursor: pointer; color: #ccc; &:hover { color: $primary; } &.delete:hover { color: #ff4d4f; } }
      }
    }
  }

  /* 右侧：题目内容 */
  .item-content {
    flex: 1;
    
    .q-stem { 
      margin-bottom: 12px; 
      font-size: 15px; 
      color: #333; 
      line-height: 1.6;
      
      .type-label { 
        color: $primary; 
        font-weight: bold; 
        margin-right: 8px; 
        font-size: 14px;
      }
      
      /* 骨架屏时的占位符文字 */
      .placeholder-text { 
        color: #999; font-style: italic; 
        .tag { background: #f0f2f5; padding: 2px 5px; border-radius: 4px; font-size: 11px; margin: 0 5px; font-style: normal; color: #666; }
        .diff { font-size: 11px; margin-left: 5px; color: #e6a23c; font-style: normal; }
      }
    }

    /* 选项列表 */
    .q-options {
      margin-left: 10px;
      .opt-row { 
        margin-bottom: 8px; 
        font-size: 14px; 
        color: #555; 
        display: flex; 
        gap: 8px; 
      }
      .opt-key { font-weight: bold; color: #333; }
    }

    /* 答题区占位 (填空/简答) */
    .q-answer-placeholder {
      margin-top: 10px;
      &.blank-area { color: #dcdfe6; letter-spacing: 2px; }
      &.essay-area {
        .essay-input-box {
          width: 100%; height: 80px; 
          border: 1px dashed #dcdfe6; 
          background: #fafafa; 
          border-radius: 6px; 
          display: flex; align-items: center; justify-content: center; 
          color: #ccc; font-size: 12px;
        }
      }
    }
    
    /* 骨架屏线条 */
    .skeleton {
       display: flex; flex-direction: column; gap: 10px;
       .sk-line { height: 12px; background: #f2f2f2; border-radius: 4px; }
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>