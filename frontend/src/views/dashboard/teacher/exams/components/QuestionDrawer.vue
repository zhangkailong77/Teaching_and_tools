<template>
  <el-drawer
    v-model="visible"
    :title="isEdit ? '编辑试题' : '录入新题'"
    direction="rtl"
    size="800px"
    class="hw-drawer"
    :close-on-click-modal="true"
    destroy-on-close
    @open="handleOpen"
  >
    <div class="homework-body" v-loading="loading">
      <!-- 1. 头部信息：标题与元数据 -->
      <div class="hw-header">
        <div class="input-group-title">
          <div class="title-display">{{ isEdit ? '编辑试题' : '录入新试题' }}</div>
        </div>
        
        <div class="hw-meta-form">
          <!-- 题型选择 -->
          <div class="meta-item type-item">
            <span class="label">🧩 题型:</span>
            <el-select
              v-model="form.type"
              placeholder="选择题型"
              size="small"
              class="custom-field"
              :disabled="isEdit"
              @change="handleTypeChange"
            >
              <el-option label="单选题" value="single" />
              <el-option label="多选题" value="multiple" />
              <el-option label="判断题" value="judge" />
              <el-option label="填空题" value="blank" />
              <el-option label="简答题" value="essay" />
            </el-select>
          </div>

          <!-- 难度 -->
          <div class="meta-item diff-item">
            <span class="label">📊 难度:</span>
            <el-rate 
              v-model="form.difficulty" 
              :max="3" 
              :texts="['易', '中', '难']" 
              show-text
              class="custom-rate"
            />
          </div>

          <!-- 标签 (可选) -->
          <div class="meta-item tag-item">
            <span class="label">🏷️ 知识点:</span>
            <el-select
              v-model="form.tags"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入标签"
              size="small"
              class="custom-field"
              style="width: 180px;"
            />
          </div>
        </div>
      </div>

      <!-- 2. 题干内容输入 -->
      <div class="hw-requirement edit-mode">
        <h4>📝 题干描述：</h4>
        <div class="textarea-wrapper">
          <textarea 
            v-model="form.content" 
            rows="5" 
            placeholder="请输入题目详细描述..."
            class="content-textarea"
          ></textarea>
        </div>
      </div>

      <!-- 3. 动态选项区 (选择题) -->
      <div v-if="['single', 'multiple'].includes(form.type)" class="hw-answer-area">
        <div class="area-header">
          <h4>🔘 选项设置：</h4>
          <el-button type="primary" link @click="addOption">+ 添加选项</el-button>
        </div>
        
        <div class="options-box">
          <div v-for="(opt, index) in form.options" :key="index" class="option-card">
            <div class="opt-label">{{ generateLabel(index) }}</div>
            <input v-model="opt.text" type="text" placeholder="请输入选项内容" class="opt-input" />
            
            <div class="opt-action">
              <el-radio 
                v-if="form.type === 'single'" 
                v-model="form.answer" 
                :label="generateLabel(index)"
              >正确答案</el-radio>
              
              <el-checkbox 
                v-if="form.type === 'multiple'" 
                v-model="form.answer" 
                :label="generateLabel(index)"
              >正确答案</el-checkbox>

              <span class="remove-btn" v-if="form.options.length > 2" @click="removeOption(index)">×</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. 判断题设置 -->
      <div v-if="form.type === 'judge'" class="hw-answer-area">
        <h4>⚖️ 正确答案：</h4>
        <div class="judge-box">
          <el-radio-group v-model="form.answer" class="custom-radio-group">
            <el-radio :label="true" border>正确 (True)</el-radio>
            <el-radio :label="false" border>错误 (False)</el-radio>
          </el-radio-group>
        </div>
      </div>

      <!-- 5. 填空/简答答案 -->
      <div v-if="['blank', 'essay'].includes(form.type)" class="hw-answer-area">
        <h4>💡 参考答案 / 关键词：</h4>
        <div class="textarea-wrapper grey">
          <textarea 
            v-model="form.answer" 
            rows="4" 
            placeholder="请输入正确答案或自动阅卷关键词..."
            class="content-textarea"
          ></textarea>
        </div>
      </div>

      <!-- 6. 解析区域 -->
      <div class="hw-requirement analysis-mode">
        <h4>📖 题目解析 (可选)：</h4>
        <div class="textarea-wrapper">
          <textarea 
            v-model="form.analysis" 
            rows="3" 
            placeholder="解析内容将在学生交卷后展示..."
            class="content-textarea"
          ></textarea>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="hw-footer">
        <button class="btn-cancel" @click="visible = false">取消</button>
        <button class="btn-primary" @click="submitForm" :disabled="submitting">
          {{ submitting ? '保存中...' : '确认保存题目' }}
        </button>
      </div>

    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { createQuestion, updateQuestion, type QuestionItem } from '@/api/exam'

const props = defineProps<{
  modelValue: boolean
  questionData?: QuestionItem
}>()

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const submitting = ref(false)
const isEdit = ref(false)

const form = reactive<any>({
  id: undefined,
  type: 'single',
  content: '',
  options: [
    { label: 'A', text: '' }, { label: 'B', text: '' }, 
    { label: 'C', text: '' }, { label: 'D', text: '' }
  ],
  answer: '',
  analysis: '',
  difficulty: 1,
  tags: []
})

const handleOpen = () => {
  if (props.questionData) {
    isEdit.value = true
    Object.assign(form, JSON.parse(JSON.stringify(props.questionData)))
  } else {
    isEdit.value = false
    resetForm()
  }
}

const resetForm = () => {
  form.id = undefined
  form.type = 'single'
  form.content = ''
  form.options = [
    { label: 'A', text: '' }, { label: 'B', text: '' }, 
    { label: 'C', text: '' }, { label: 'D', text: '' }
  ]
  form.answer = ''
  form.analysis = ''
  form.difficulty = 1
  form.tags = []
}

const handleTypeChange = (val: string) => {
  form.answer = val === 'multiple' ? [] : (val === 'judge' ? true : '')
}

const generateLabel = (index: number) => String.fromCharCode(65 + index)
const addOption = () => {
  form.options.push({ label: generateLabel(form.options.length), text: '' })
}
const removeOption = (index: number) => {
  form.options.splice(index, 1)
  form.options.forEach((o: any, i: number) => o.label = generateLabel(i))
}

const submitForm = async () => {
  if (!form.content) return ElMessage.warning('请输入题干内容')
  
  submitting.value = true
  try {
    if (isEdit.value && form.id) {
      await updateQuestion(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createQuestion(form)
      ElMessage.success('题目已录入题库')
    }
    visible.value = false
    emit('success')
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
$primary-color: #00c9a7;
$text-color: #2c3e50;
$border-color: #eee;
$bg-input: #f7f8fa;

.homework-body { padding: 15px 20px; }

/* 1. 头部样式 */
.hw-header { 
  border-bottom: 1px solid $border-color; 
  padding-bottom: 25px; margin-bottom: 25px;

  .input-group-title {
    margin-bottom: 20px;
    .title-display { font-size: 24px; font-weight: 700; color: $text-color; }
  }

  .hw-meta-form { 
    display: flex; gap: 20px; align-items: center; flex-wrap: wrap;
    .meta-item {
      display: flex; align-items: center; gap: 8px; font-size: 13px; color: #666;
      .label { font-weight: 600; color: $text-color; }
      &.type-item {
        .custom-field { width: 140px; } // 调整这个数值即可
      }
    }
  }
}

/* 2. 内容区域 */
.hw-requirement { 
  margin-bottom: 25px;
  h4 { margin: 0 0 12px; font-size: 15px; color: $text-color; font-weight: 600; }
  
  .textarea-wrapper {
    background: $bg-input; border-radius: 12px; padding: 15px; border: 1px solid transparent; transition: all 0.3s;
    &:focus-within { background: #fff; border-color: $primary-color; box-shadow: 0 4px 12px rgba(0, 201, 167, 0.1); }
    
    .content-textarea {
      width: 100%; background: transparent; border: none; font-size: 14px; color: #333; line-height: 1.7; resize: none; outline: none; font-family: inherit;
      &::placeholder { color: #aaa; }
    }
  }

  &.analysis-mode {
    .textarea-wrapper { background: #fffef0; border-color: #fceea7; } /* 解析用淡黄色区分 */
  }
}

/* 3. 答案/选项区域 */
.hw-answer-area {
  margin-bottom: 30px;
  .area-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; 
    h4 { margin: 0; font-size: 15px; color: $text-color; font-weight: 600; }
  }

  .options-box {
    display: flex; flex-direction: column; gap: 10px;
    .option-card {
      background: #fff; border: 1px solid $border-color; border-radius: 10px; padding: 10px 15px; display: flex; align-items: center; gap: 12px; transition: all 0.2s;
      &:hover { border-color: $primary-color; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

      .opt-label { width: 28px; height: 28px; background: $bg-input; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px; color: #666; }
      .opt-input { flex: 1; border: none; outline: none; font-size: 14px; color: #333; }
      
      .opt-action { display: flex; align-items: center; gap: 15px;
        .remove-btn { cursor: pointer; color: #ccc; font-size: 18px; &:hover { color: #ff4d4f; } }
      }
    }
  }

  .judge-box {
    padding: 10px 0;
  }
}

/* 4. 底部按钮 */
.hw-footer { 
  margin-top: 20px; display: flex; justify-content: flex-end; gap: 16px;
  border-top: 1px solid $border-color; padding-top: 20px;
  button { padding: 12px 30px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
  .btn-cancel { background: #fff; border: 1px solid #ddd; color: #666; &:hover { background: #f5f5f5; color: #333; } }
  .btn-primary {
    background: $primary-color; color: white; border: none; box-shadow: 0 4px 12px rgba(0, 201, 167, 0.3);
    &:hover { filter: brightness(1.05); transform: translateY(-1px); }
    &:active { transform: translateY(0); }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}

/* 深度美化 */
:deep(.custom-field) {
  .el-input__wrapper, .el-select__wrapper {
    background-color: $bg-input !important; box-shadow: none !important; border-radius: 8px;
    &.is-focus { background-color: #fff !important; box-shadow: 0 0 0 1px $primary-color !important; }
  }
}

:deep(.custom-radio-group) {
  .el-radio.is-bordered.is-checked { border-color: $primary-color; background-color: rgba($primary-color, 0.05); }
  .el-radio__input.is-checked .el-radio__inner { background-color: $primary-color; border-color: $primary-color; }
  .el-radio__input.is-checked + .el-radio__label { color: $primary-color; }
}

:deep(.custom-rate) {
  --el-rate-fill-color: #ff9f43;
}
</style>