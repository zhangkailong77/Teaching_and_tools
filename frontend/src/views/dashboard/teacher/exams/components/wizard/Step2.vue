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
              <!-- 使用 class 控制样式 -->
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
      <div class="strategy-header">
        <el-button type="primary" icon="Plus" @click="addStrategy">添加抽题策略</el-button>
        <div class="summary">
          预计题量: <strong>{{ totalCount }}</strong> 题，
          预计总分: <strong>{{ totalScoreRandom }}</strong> 分
        </div>
      </div>

      <el-table :data="form.random_config" border style="width: 100%">
        <el-table-column label="题型" width="150">
          <template #default="{ row }">
            <el-select v-model="row.type" size="small">
              <el-option label="单选题" value="single" />
              <el-option label="多选题" value="multiple" />
              <el-option label="判断题" value="judge" />
              <el-option label="填空题" value="blank" />
              <el-option label="简答题" value="essay" />
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column label="难度" width="150">
          <template #default="{ row }">
            <el-rate v-model="row.difficulty" :max="3" />
          </template>
        </el-table-column>

        <el-table-column label="知识点(可选)">
          <template #default="{ row }">
            <el-select v-model="row.tag" placeholder="不限" clearable size="small" filterable allow-create>
              <el-option v-for="t in tagOptions" :key="t" :label="t" :value="t" />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column label="抽取数量" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.count" :min="1" size="small" />
          </template>
        </el-table-column>

        <el-table-column label="每题分值" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.score" :min="1" size="small" />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="80" align="center">
          <template #default="{ $index }">
            <el-button type="danger" link icon="Delete" @click="removeStrategy($index)" />
          </template>
        </el-table-column>
      </el-table>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { getQuestions, getAllTags, type QuestionItem } from '@/api/exam'
import { Plus, Close, Delete, Search, Top, Bottom, CircleCheckFilled } from '@element-plus/icons-vue'

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

// --- 手动模式逻辑 ---
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
    // ✅ 核心修改：计算偏移量 skip
    // 第一页 skip = (1-1)*10 = 0
    // 第二页 skip = (2-1)*10 = 10
    const skipValue = (page.value - 1) * 10;

    const res = await getQuestions({ 
      skip: skipValue,    // ✅ 传给后端的必须是 skip
      limit: 10, 
      keyword: filter.keyword || undefined,
      type: filter.type === 'all' ? undefined : filter.type
    });
    
    // 判断是否还有更多：如果当前返回的加上已有的，等于总数，则没有更多了
    // 或者简单判断：如果返回的数量小于 limit，说明到底了
    if (res.items.length < 10) {
      hasMore.value = false;
    } else {
      hasMore.value = true;
    }

    if (page.value === 1) {
      bankQuestions.value = res.items;
    } else {
      // ✅ 翻页时追加
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
    // 如果已经选了，就移除
    form.value.questions.splice(index, 1)
  } else {
    // 如果没选，就添加
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
  // 只去 HTML 标签，不截断长度
  return html.replace(/<[^>]+>/g, '')
}

const getShortTypeLabel = (type: string) => {
  const map: any = { all: '全部', single: '单选', multiple: '多选', judge: '判断', blank: '填空', essay: '简答' }
  return map[type] || type
}

// --- 随机模式逻辑 ---
const addStrategy = () => {
  form.value.random_config.push({
    type: 'single',
    difficulty: 1,
    tag: '',
    count: 5,
    score: 2
  })
}

const removeStrategy = (index: number) => {
  form.value.random_config.splice(index, 1)
}

const totalCount = computed(() => form.value.random_config.reduce((sum: number, c: any) => sum + c.count, 0))
const totalScoreRandom = computed(() => form.value.random_config.reduce((sum: number, c: any) => sum + (c.count * c.score), 0))

// --- 初始化 ---
onMounted(async () => {
  if (form.value.mode === 1) fetchBank()
  if (form.value.mode === 2) {
    const tags = await getAllTags()
    tagOptions.value = tags
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

      .paper-body {
        .empty-paper { text-align: center; margin-top: 100px; color: #ccc; p { margin-top: 10px; font-size: 14px; } }
        
        .paper-item {
          display: flex; gap: 20px; margin-bottom: 30px; border-bottom: 1px dashed #eee; padding-bottom: 20px;
          
          .item-sidebar {
            width: 80px; flex-shrink: 0; text-align: center;
            .idx-badge { background: #333; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-bottom: 8px; display: inline-block; }
            .ops { 
              display: flex; flex-direction: column; align-items: center; gap: 5px; 
              .icon-group { 
                margin-top: 5px; display: flex; gap: 8px; 
                .op-icon { cursor: pointer; color: #999; transition: color 0.2s; &:hover { color: $primary; } &.delete:hover { color: #ff4d4f; } }
              }
            }
          }

          /* 题目内容容器 */
            .item-content {
            flex: 1;
            .q-stem { 
                font-size: 15px; 
                color: #333; 
                line-height: 1.6; 
                margin-bottom: 12px; 
                font-weight: 500; 
            }
            .type-label { color: $primary; font-weight: bold; margin-right: 8px; }
            }

            /* 统一选项样式 */
            .q-options {
            margin-left: 10px;
            .opt-row { 
                margin-bottom: 8px; 
                font-size: 14px; 
                color: #444; 
                display: flex; 
                gap: 8px; 
                align-items: flex-start; 
            }
            .opt-key { font-weight: bold; color: #333; width: 18px; }
            }

            /* ✅ 答题占位符样式 (填空和简答) */
            .q-answer-placeholder {
            margin-top: 15px;
            margin-left: 10px;

            &.blank-area {
                color: #dcdfe6;
                letter-spacing: 2px;
            }

            &.essay-area {
                .essay-input-box {
                width: 100%;
                min-height: 120px; /* ✅ 给一个足够的高度 */
                border: 1px dashed #dcdfe6; /* ✅ 使用虚线边框 */
                background-color: #fafafa;
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #adb5bd;
                font-size: 13px;
                }
            }
            }
        }
      }
    }
  }
}

/* 随机布局 */
.random-layout {
  padding: 20px;
  .strategy-header { display: flex; justify-content: space-between; margin-bottom: 15px; }
  .summary strong { color: $primary; font-size: 16px; margin: 0 3px; }
}

/* ✅ 新增：列表平移过渡动画 */
.list-move {
  transition: transform 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}

/* 确保切换时的布局不会瞬间塌陷（可选优化） */
.list-leave-active {
  position: absolute;
}
</style>