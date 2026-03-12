<template>
  <div class="exam-engine-container" ref="examPageRef">
    <!-- 阶段一：考试开启协议 (引导页) -->
    <div v-if="!isStarted" class="protocol-wrapper">
      <div class="protocol-card">
        <div class="header">
          <el-icon class="logo-icon"><Memo /></el-icon>
          <h2>考试确认与环境检查</h2>
        </div>
        
        <div class="info-grid">
          <div class="info-item">
            <span class="label">试卷名称</span>
            <span class="val">{{ examInfo.title }}</span>
          </div>
          <div class="info-item">
            <span class="label">考试时长</span>
            <span class="val">{{ examInfo.duration }} 分钟</span>
          </div>
          <div class="info-item">
            <span class="label">题目总数</span>
            <span class="val">{{ questions.length }} 题</span>
          </div>
          <div class="info-item">
            <span class="label">及格线</span>
            <span class="val">{{ examInfo.pass_score }} / {{ examInfo.total_score }} 分</span>
          </div>
        </div>

        <div class="rules-section">
          <h4>📌 考前规则须知</h4>
          <ul>
            <li><strong>禁止切换窗口：</strong> 系统将实时监控切屏行为，超过3次将自动强制交卷。</li>
            <li><strong>全屏答题：</strong> 点击开始后将进入全屏模式，中途退出全屏需立即恢复。</li>
            <li><strong>断电保护：</strong> 答案每 30 秒自动同步至云端，意外掉线后重新进入可继续答题。</li>
            <li><strong>摄像头监考：</strong> 本场考试过程中请保持面部出现在屏幕前方（如开启）。</li>
          </ul>
        </div>

        <div class="device-check">
          <div class="check-item">
            <el-icon :class="isOnline ? 'success' : 'error'"><Opportunity /></el-icon>
            网络连接：{{ isOnline ? '正常' : '异常' }}
          </div>
          <div class="check-item">
            <el-icon class="success"><CircleCheck /></el-icon>
            系统环境：就绪
          </div>
        </div>

        <div class="footer-action">
          <button class="btn-start" @click="startExam">我已阅读并准备好开始</button>
          <p class="tip">点击按钮将进入全屏沉浸模式</p>
        </div>
      </div>
    </div>

    <!-- 阶段二：核心答题界面 -->
    <div v-else class="exam-main-layout">
      <!-- 顶部状态栏 -->
      <header class="exam-header">
        <div class="left">
          <span class="title">{{ examInfo.title }}</span>
          <span class="save-status" :class="{ 'saving': isSaving }">
             {{ isSaving ? '🔄 正在同步答案...' : '✅ 答案已实时保存' }}
          </span>
        </div>
        
        <div class="center">
          <div class="timer" :class="{ 'warning': timeLeft < 300 }">
            <el-icon><Timer /></el-icon>
            <span class="time">{{ formatTime(timeLeft) }}</span>
          </div>
        </div>

        <div class="right">
          <div class="progress-info">
            进度：<strong>{{ answeredCount }}</strong> / {{ questions.length }}
          </div>
          <button class="btn-submit" @click="confirmSubmit">提交试卷</button>
        </div>
      </header>

      <div class="layout-body">
        <!-- 2.1 左侧：题型快速导航 -->
        <aside class="type-nav">
          <div 
            v-for="group in groupedQuestions" 
            :key="group.type" 
            class="nav-item"
            @click="scrollToType(group.type)"
          >
            {{ getTypeLabel(group.type) }}
          </div>
        </aside>

        <!-- 2.2 中间：题目列表 -->
        <main class="question-scroll-area" ref="scrollContainer">
          <div v-for="group in groupedQuestions" :key="group.type" :id="'type-' + group.type" class="type-section">
            <h3 class="type-title">{{ getTypeLabel(group.type) }}<span>（共{{ group.list.length }}题）</span></h3>
            
            <div 
              v-for="(q, idx) in group.list" 
              :key="q.id" 
              :id="'q-' + q.id" 
              class="q-card"
            >
              <div class="q-head">
                <span class="q-num">{{ q.index + 1 }}</span>
                <span class="q-score">({{ q.score }}分)</span>
                <div class="q-stem" v-html="q.content"></div>
              </div>

              <!-- 题目交互层 -->
              <div class="q-answer-box">
                <!-- 单选/判断 -->
                <el-radio-group v-if="q.type === 'single' || q.type === 'judge'" v-model="answers[q.id]">
                  <el-radio 
                    v-for="opt in (q.options && q.options.length > 0 ? q.options : defaultJudgeOptions)" 
                    :key="opt.label" 
                    :value="opt.label"
                    border
                    class="opt-item"
                  >
                    <span class="opt-label">{{ opt.label }}.</span> {{ opt.text }}
                  </el-radio>
                </el-radio-group>

                <!-- 多选 -->
                <el-checkbox-group v-else-if="q.type === 'multiple'" v-model="answers[q.id]">
                  <el-checkbox 
                    v-for="opt in q.options" 
                    :key="opt.label" 
                    :value="opt.label" 
                    border
                    class="opt-item"
                  >
                    <span class="opt-label">{{ opt.label }}.</span> {{ opt.text }}
                  </el-checkbox>
                </el-checkbox-group>

                <!-- 填空/简答 -->
                <el-input
                  v-else
                  v-model="answers[q.id]"
                  type="textarea"
                  :rows="q.type === 'essay' ? 6 : 2"
                  placeholder="请输入您的答案..."
                  class="custom-textarea"
                />
              </div>
            </div>
          </div>
        </main>

        <!-- 2.3 右侧：答题卡 -->
        <aside class="answer-card">
          <h4>答题卡</h4>
          <div class="matrix">
            <div 
              v-for="(q, idx) in questions" 
              :key="q.id"
              class="dot"
              :class="{ 'done': isAnswered(q.id), 'active': currentViewingId === q.id }"
              @click="scrollToQuestion(q.id)"
            >
              {{ idx + 1 }}
            </div>
          </div>
          <div class="legend">
            <div class="l-item"><span class="dot done"></span>已答</div>
            <div class="l-item"><span class="dot"></span>未答</div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getExamPaper, submitExam, saveExamProgress, getExamProgress } from '@/api/exam';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Memo, Timer, Opportunity, CircleCheck } from '@element-plus/icons-vue';
import { debounce } from 'lodash-es';

const route = useRoute();
const router = useRouter();
const examId = Number(route.params.id);

// --- 状态变量 ---
const isStarted = ref(false);
const isOnline = ref(navigator.onLine);
const loading = ref(false);
const isSaving = ref(false);
const examPageRef = ref<HTMLElement | null>(null);

const examInfo = reactive({
  title: '加载中...',
  duration: 0,
  total_score: 0,
  pass_score: 0
});

const questions = ref<any[]>([]);
const answers = reactive<Record<number, any>>({});
const timeLeft = ref(0);
const cheatCount = ref(0);
const currentViewingId = ref(0);

const defaultJudgeOptions = [{ label: 'A', text: '正确' }, { label: 'B', text: '错误' }];

// --- 逻辑处理 ---

// 题目按类型分组
const groupedQuestions = computed(() => {
  const groups: any[] = [];
  const types = ['single', 'multiple', 'judge', 'blank', 'essay'];
  types.forEach(type => {
    const list = questions.value.filter(q => q.type === type);
    if (list.length > 0) {
      groups.push({ type, list });
    }
  });
  return groups;
});

const answeredCount = computed(() => {
  return questions.value.filter(q => isAnswered(q.id)).length;
});

const isAnswered = (id: number) => {
  const val = answers[id];
  if (Array.isArray(val)) return val.length > 0;
  return val !== undefined && val !== '';
};

// 1. 初始化数据
onMounted(async () => {
  try {
    // 这里需要获取试卷元数据和题目
    const res = await getExamPaper(examId);
    questions.value = res.map((item, idx) => ({ ...item, index: idx }));
    // 假设从列表页带过来一些基本信息，或单独请求
    examInfo.title = route.query.title as string || '期中考试';
    examInfo.duration = Number(route.query.duration) || 60;
    examInfo.total_score = Number(route.query.total_score) || 100;
    examInfo.pass_score = Number(route.query.pass_score) || 60;

    timeLeft.value = examInfo.duration * 60;

    // 初始化答案结构
    questions.value.forEach(q => {
      if (q.type === 'multiple') answers[q.id] = [];
      else answers[q.id] = '';
    });

    // 加载暂存的答案
    await loadSavedProgress();

    // 监控网络
    window.addEventListener('online', () => isOnline.value = true);
    window.addEventListener('offline', () => isOnline.value = false);
  } catch (e) {
    ElMessage.error('无法加载试卷内容');
  }
});

// 2. 开始考试逻辑
const startExam = () => {
    if (document.documentElement.requestFullscreen) {
    document.documentElement.requestFullscreen().then(() => {
      isStarted.value = true;
      startTimer();
      setupAntiCheat();
    }).catch((err) => {
      ElMessage.warning('全屏请求被拒绝，请手动开启以获得最佳体验');
      // 即使全屏失败，也允许开始考试
      isStarted.value = true;
      startTimer();
      setupAntiCheat();
    });
  } else {
    isStarted.value = true;
    startTimer();
  }
};

// 3. 计时器
let timerInterval: any = null;
const startTimer = () => {
  timerInterval = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--;
    } else {
      autoSubmit();
    }
  }, 1000);
};

// 4. 保存单题答案（防抖3秒，变化即保存）
const saveSingleAnswer = debounce(async () => {
  isSaving.value = true;
  try {
    // 收集所有已作答的题目
    const answerList = [];
    for (const qid in answers) {
      const val = answers[qid];
      // 只保存有值的答案
      if (val !== undefined && val !== '' && (Array.isArray(val) ? val.length > 0 : true)) {
        answerList.push({
          question_id: Number(qid),
          answer_content: val
        });
      }
    }

    if (answerList.length > 0) {
      await saveExamProgress(examId, answerList);
    }
  } catch (e) {
    console.error('保存失败:', e);
  } finally {
    setTimeout(() => isSaving.value = false, 1000);
  }
}, 3000);

// 5. 监听answers变化，自动保存
watch(
  () => answers,
  () => {
    // 直接触发保存（reactive对象newVal和oldVal是同一个引用）
    saveSingleAnswer();
  },
  { deep: true }
);

// 6. 加载暂存的答案
const loadSavedProgress = async () => {
  try {
    const res = await getExamProgress(examId);
    if (res.answers) {
      // 恢复已保存的答案
      for (const [qid, answer] of Object.entries(res.answers)) {
        answers[Number(qid)] = answer;
      }
    }
  } catch (e) {
    console.error('加载暂存失败:', e);
  }
};

// 5. 防作弊逻辑
const setupAntiCheat = () => {
  document.addEventListener('visibilitychange', handleVisibilityChange);
  window.addEventListener('blur', handleBlur);
};

const handleVisibilityChange = () => {
  if (document.hidden) {
    handleCheatWarning();
  }
};

const handleBlur = () => {
  handleCheatWarning();
};

const handleCheatWarning = () => {
  cheatCount.value++;
  if (cheatCount.value >= 3) {
    ElMessageBox.alert('您切屏次数过多，系统将强制交卷！', '作弊警告', {
      confirmButtonText: '确定',
      callback: () => autoSubmit()
    });
  } else {
    ElMessage.error(`警告：请勿离开考试页面！(切屏 ${cheatCount.value}/3)`);
  }
};

// 6. 提交逻辑
const confirmSubmit = () => {
  console.log("准备提交试卷..."); 
  
  // 确保数据存在
  const totalQuestions = questions.value.length;
  const answered = answeredCount.value;
  const unFinished = totalQuestions - answered;
  
  const msg = unFinished > 0 
    ? `您还有 ${unFinished} 道题未答，确定要交卷吗？` 
    : '确定检查完毕并提交试卷吗？';
    
  ElMessageBox.confirm(msg, '提交确认', {
    confirmButtonText: '确认交卷',
    cancelButtonText: '再检查下',
    type: 'warning',
    // ✅ 关键配置：防止全屏下滚动锁定导致层级错乱
    lockScroll: false,
    // ✅ 关键配置：如果还是看不见，强制将弹窗插入到当前全屏元素内（可选）
    // appendTo: examPageRef.value 
  }).then(() => {
    autoSubmit();
  }).catch(() => {
    console.log("用户取消提交");
  });
};

const autoSubmit = async () => {
  clearInterval(timerInterval);

  try {
    // 传空数组，让后端从Redis读取暂存的答案
    const submitData = {
      answers: [],
      cheat_count: cheatCount.value
    };

    await submitExam(examId, submitData);

    ElMessage.success('提交成功！');
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(err => console.error(err));
    }

    setTimeout(() => {
      router.replace('/dashboard/student/exams');
    }, 500);
  } catch (e) {
    console.error("提交出错：", e);
    ElMessage.error('交卷失败，请检查网络');
  }
};

// 工具函数
const formatTime = (seconds: number) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${h > 0 ? h + ':' : ''}${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
};

const getTypeLabel = (t: string) => {
  return { single: '单选题', multiple: '多选题', judge: '判断题', blank: '填空题', essay: '简答题' }[t];
};

const scrollToQuestion = (id: number) => {
  currentViewingId.value = id;
  document.getElementById('q-' + id)?.scrollIntoView({ behavior: 'smooth' });
};

const scrollToType = (type: string) => {
  document.getElementById('type-' + type)?.scrollIntoView({ behavior: 'smooth' });
};

onUnmounted(() => {
  clearInterval(timerInterval);
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  window.removeEventListener('blur', handleBlur);
});
</script>

<style scoped lang="scss">
$primary: #00c9a7;
$bg-faded: #f4f7f6;
$text-dark: #2A5850;

.exam-engine-container {
  width: 100vw; height: 100vh; background: $bg-faded; overflow: hidden;
}

/* 协议页样式 */
.protocol-wrapper {
  height: 100%; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #e0f2f1 0%, #f4f7f6 100%);
  
  .protocol-card {
    width: 650px; background: white; border-radius: 24px; padding: 40px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.1);
    
    .header {
      text-align: center; margin-bottom: 30px;
      .logo-icon { font-size: 48px; color: $primary; }
      h2 { margin-top: 10px; color: $text-dark; }
    }

    .info-grid {
      display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
      background: #f9f9f9; padding: 20px; border-radius: 16px; margin-bottom: 25px;
      .info-item {
        .label { font-size: 12px; color: #999; display: block; }
        .val { font-size: 16px; font-weight: bold; color: #333; }
      }
    }

    .rules-section {
      margin-bottom: 25px;
      h4 { color: #e67e22; margin-bottom: 10px; }
      ul { padding-left: 18px; color: #666; font-size: 13px; line-height: 1.8; }
    }

    .device-check {
      display: flex; gap: 30px; margin-bottom: 35px; justify-content: center;
      .check-item { 
        display: flex; align-items: center; gap: 6px; font-size: 14px; 
        .success { color: $primary; } .error { color: #f56c6c; }
      }
    }

    .footer-action {
      text-align: center;
      .btn-start {
        background: $primary; color: white; border: none; padding: 15px 50px;
        border-radius: 30px; font-size: 16px; font-weight: bold; cursor: pointer;
        box-shadow: 0 10px 20px rgba(0, 201, 167, 0.3); transition: all 0.3s;
        &:hover { transform: translateY(-2px); box-shadow: 0 15px 30px rgba(0, 201, 167, 0.4); }
      }
      .tip { font-size: 12px; color: #bbb; margin-top: 12px; }
    }
  }
}

/* 考试页布局 */
.exam-main-layout {
  height: 100%; display: flex; flex-direction: column;

  .exam-header {
    height: 70px; background: white; border-bottom: 1px solid #eee;
    display: flex; justify-content: space-between; align-items: center; padding: 0 30px;
    
    .left .title { font-size: 18px; font-weight: bold; color: $text-dark; margin-right: 20px; }
    .save-status { font-size: 12px; color: #999; transition: color 0.3s; &.saving { color: $primary; } }
    
    .timer {
      display: flex; align-items: center; gap: 8px; padding: 8px 20px;
      background: #f0fdfa; border-radius: 30px; color: $primary;
      .time { font-family: monospace; font-size: 24px; font-weight: bold; }
      &.warning { background: #fff1f0; color: #f5222d; animation: blink 1s infinite; }
    }

    .btn-submit {
      background: $primary; color: white; border: none; padding: 8px 25px;
      border-radius: 8px; font-weight: bold; cursor: pointer;
    }
  }

  .layout-body {
    flex: 1; display: flex; overflow: hidden;

    .type-nav {
      width: 120px; border-right: 1px solid #eee; background: white; padding: 20px 0;
      .nav-item {
        padding: 12px 20px; font-size: 14px; color: #666; cursor: pointer;
        &:hover { color: $primary; background: #f0fdfa; }
      }
    }

    .question-scroll-area {
      flex: 1; overflow-y: auto; padding: 40px; scroll-behavior: smooth;

      .type-section {
        max-width: 800px; margin: 0 auto 50px;
        .type-title { border-left: 4px solid $primary; padding-left: 15px; margin-bottom: 30px; span { font-weight: normal; font-size: 14px; color: #999; } }
      }

      .q-card {
        background: white; border-radius: 16px; padding: 30px; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02); border: 1px solid transparent; transition: all 0.3s;
        
        .q-head {
          display: flex; gap: 10px; margin-bottom: 20px;
          .q-num { font-weight: bold; font-size: 18px; color: $primary; }
          .q-score { color: #999; font-size: 14px; margin-top: 3px; }
          .q-stem { font-size: 16px; color: #333; line-height: 1.6; }
        }

        .opt-item {
          display: block; width: 100%; margin: 0 0 12px 0 !important;
          padding: 12px 20px; border-radius: 10px; height: auto;
          .opt-label { font-weight: bold; margin-right: 10px; }
        }

        :deep(.el-radio.is-bordered.is-checked), :deep(.el-checkbox.is-bordered.is-checked) {
          border-color: $primary; background: #f0fdfa;
        }
      }
    }

    .answer-card {
      width: 280px; background: white; border-left: 1px solid #eee; padding: 25px;
      h4 { margin-bottom: 20px; color: $text-dark; }
      .matrix {
        display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 30px;
        .dot {
          height: 36px; border-radius: 8px; border: 1px solid #ddd;
          display: flex; align-items: center; justify-content: center;
          font-size: 13px; color: #999; cursor: pointer; transition: all 0.2s;
          &.done { background: #f0fdfa; border-color: $primary; color: $primary; font-weight: bold; }
          &.active { box-shadow: 0 0 0 2px $primary; }
          &:hover { border-color: $primary; }
        }
      }
      .legend {
        display: flex; gap: 20px; font-size: 12px; color: #999;
        .dot { width: 12px; height: 12px; border-radius: 3px; background: #eee; &.done { background: $primary; } }
        .l-item { display: flex; align-items: center; gap: 6px; }
      }
    }
  }
}

@keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>