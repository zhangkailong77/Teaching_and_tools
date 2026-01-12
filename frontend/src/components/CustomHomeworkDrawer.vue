<template>
  <el-drawer
    v-model="visible"
    title="发布自定义作业"
    direction="rtl"
    size="800px"
    class="hw-drawer"
    :close-on-click-modal="false"
    destroy-on-close
    @open="handleOpen"
  >
    <div class="homework-body" v-loading="loading">
      
      <!-- 1. 头部信息：标题与元数据设置 -->
      <div class="hw-header">
        <div class="input-group-title">
          <input 
            v-model="form.title" 
            type="text" 
            placeholder="请输入作业标题..." 
            class="title-input"
          />
        </div>
        
        <div class="hw-meta-form">
          <!-- 班级选择 -->
          <div class="meta-item">
            <span class="label">📚 发布对象:</span>
            <el-select
              v-model="form.class_ids"
              multiple
              collapse-tags
              collapse-tags-tooltip
              placeholder="选择班级"
              size="small"
              class="meta-select"
            >
              <el-option
                v-for="item in classOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </div>

          <!-- 截止时间 -->
          <div class="meta-item">
            <span class="label">📅 截止:</span>
            <el-date-picker
              v-model="form.deadline"
              type="datetime"
              placeholder="设置截止时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
              size="small"
              style="width: 160px;"
            />
          </div>

          <!-- 满分 -->
          <div class="meta-item">
            <span class="label">💯 满分:</span>
            <el-input-number 
              v-model="form.max_score" 
              :min="1" 
              :max="1000" 
              size="small" 
              controls-position="right"
              style="width: 100px;" 
            />
          </div>
        </div>
      </div>

      <!-- 2. 作业内容输入 (仿照 hw-requirement 样式) -->
      <div class="hw-requirement edit-mode">
        <h4>📝 作业要求详情：</h4>
        <textarea 
          v-model="form.content" 
          rows="12" 
          placeholder="在此输入详细的作业要求、评分标准或注意事项..."
          class="content-textarea"
        ></textarea>
      </div>

      <!-- 3. 附件上传区 (仿照 hw-answer-area 样式) -->
      <div class="hw-answer-area">
        <h4>📎 参考附件 (可选)：</h4>
        
        <div class="attachment-box">
          <!-- 文件列表展示 -->
          <div v-if="form.attachments.length > 0" class="file-list">
             <div v-for="(url, index) in form.attachments" :key="index" class="file-item">
                <span class="file-icon">📄</span>
                <span class="file-link">{{ getFileName(url) }}</span>
                <span class="remove-btn" @click="removeAttachment(index)">×</span>
             </div>
          </div>

          <!-- 上传按钮 -->
          <el-upload
            action="#"
            :http-request="customUpload"
            :show-file-list="false"
            class="upload-trigger"
          >
            <button class="btn-icon">
              <span class="plus">+</span> 上传参考资料 (PDF/图片)
            </button>
          </el-upload>
        </div>
      </div>

      <!-- 4. 底部操作 -->
      <div class="hw-footer">
        <button class="btn-cancel" @click="visible = false">取消</button>
        <button class="btn-primary" @click="submitForm" :disabled="submitting">
          {{ submitting ? '发布中...' : '确认发布' }}
        </button>
      </div>

    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, type UploadRequestOptions } from 'element-plus'
import { createCustomHomework } from '@/api/homework'
// ✅ 使用你要求的 API 引用
import { getMyClasses } from '@/api/course' 
import { uploadImage } from '@/api/common'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const submitting = ref(false)
const classOptions = ref<any[]>([])

const form = reactive({
  title: '',
  class_ids: [] as number[],
  deadline: '',
  max_score: 100,
  content: '',
  attachments: [] as string[]
})

// 打开时初始化
const handleOpen = async () => {
  // 重置数据
  form.title = ''
  form.class_ids = []
  form.deadline = ''
  form.max_score = 100
  form.content = ''
  form.attachments = []
  
  loading.value = true
  try {
    // ✅ 调用 getMyClasses
    const res = await getMyClasses()
    classOptions.value = res.data || res
  } catch (error) {
    console.error('获取班级列表失败', error)
  } finally {
    loading.value = false
  }
}

// 上传逻辑
const customUpload = async (options: UploadRequestOptions) => {
  try {
    // ✅ 调用 uploadImage (传递 File 对象)
    const res = await uploadImage(options.file as File, 'homework')
    const fileUrl = res.data?.url || res.url 
    form.attachments.push(fileUrl)
    ElMessage.success('上传成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('上传失败')
  }
}

const removeAttachment = (index: number) => {
  form.attachments.splice(index, 1)
}

const getFileName = (url: string) => {
  return url.split('/').pop() || '未命名文件'
}

// 提交
const submitForm = async () => {
  if (!form.title) return ElMessage.warning('请输入作业标题')
  if (form.class_ids.length === 0) return ElMessage.warning('请至少选择一个班级')
  if (!form.content) return ElMessage.warning('请输入作业要求')

  submitting.value = true
  try {
    await createCustomHomework({
      title: form.title,
      content: form.content,
      class_ids: form.class_ids,
      deadline: form.deadline || null,
      max_score: form.max_score,
      attachments: form.attachments
    })
    
    ElMessage.success('作业发布成功')
    visible.value = false
    emit('success')
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
$primary-color: #00c9a7;
$text-color: #2c3e50;
$gray-light: #f9f9f9;
$border-color: #eee;

.homework-body { 
  padding: 10px; 
  font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* 1. 头部样式 (Header) */
.hw-header { 
  border-bottom: 1px solid $border-color; 
  padding-bottom: 20px; 
  margin-bottom: 20px;

  .input-group-title {
    margin-bottom: 15px;
    .title-input {
      width: 100%;
      border: none;
      font-size: 22px;
      font-weight: bold;
      color: $text-color;
      padding: 10px 0;
      outline: none;
      border-bottom: 2px solid transparent;
      transition: border-color 0.3s;
      
      &::placeholder { color: #ccc; font-weight: normal; }
      &:focus { border-bottom-color: $primary-color; }
    }
  }

  .hw-meta-form { 
    display: flex; 
    gap: 25px; 
    align-items: center; 
    flex-wrap: wrap;

    .meta-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: #666;

      .label { font-weight: 600; color: $text-color; }

      .meta-select {
        width: 200px; // 你可以根据需要调整这个数值
      }
    }
  }
}

/* 2. 要求区域 (Requirement) - 编辑模式 */
.hw-requirement { 
  background: $gray-light; 
  padding: 20px; 
  border-radius: 12px; 
  margin-bottom: 25px;
  border: 1px solid transparent;
  transition: all 0.3s;

  &.edit-mode:focus-within {
    background: #fff;
    border-color: rgba($primary-color, 0.5);
    box-shadow: 0 4px 15px rgba(0, 201, 167, 0.08);
  }

  h4 { margin: 0 0 15px; font-size: 14px; color: $text-color; font-weight: 600; }
  
  .content-textarea {
    width: 100%;
    background: transparent;
    border: none;
    font-size: 14px;
    color: #555;
    line-height: 1.8;
    resize: none;
    outline: none;
    font-family: inherit;
    
    &::placeholder { color: #bbb; }
  }
}

/* 3. 附件区域 (Answer/Attachment Area) */
.hw-answer-area {
  margin-bottom: 30px;
  h4 { margin: 0 0 10px; font-size: 14px; color: $text-color; }

  .attachment-box {
    border: 1px dashed #ddd;
    border-radius: 8px;
    padding: 15px;
    background: #fafafa;
    
    .file-list {
      margin-bottom: 15px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;

      .file-item {
        background: #fff;
        border: 1px solid $border-color;
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 12px;
        color: #555;
        display: flex;
        align-items: center;
        gap: 6px;
        
        .remove-btn { 
          cursor: pointer; color: #999; font-weight: bold; font-size: 14px; 
          &:hover { color: #ff4d4f; }
        }
      }
    }

    .btn-icon { 
      background: white; 
      border: 1px solid $border-color; 
      padding: 8px 15px; 
      border-radius: 6px; 
      cursor: pointer; 
      font-size: 13px; 
      color: #666;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 5px;

      .plus { font-size: 16px; font-weight: bold; color: $primary-color; line-height: 1; }

      &:hover { 
        color: $primary-color; 
        border-color: $primary-color; 
        background: rgba($primary-color, 0.05);
      } 
    }
  }
}

/* 4. 底部操作 (Footer) */
.hw-footer { 
  margin-top: 30px; 
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  border-top: 1px solid $border-color;
  padding-top: 20px;

  button { 
    padding: 10px 25px; 
    border-radius: 8px; 
    font-size: 14px; 
    font-weight: 600; 
    cursor: pointer; 
    transition: all 0.3s;
  }

  .btn-cancel {
    background: transparent;
    border: 1px solid #ddd;
    color: #666;
    &:hover { border-color: #999; color: #333; }
  }

  .btn-primary {
    background: $primary-color; 
    color: white; 
    border: none; 
    box-shadow: 0 4px 10px rgba(0, 201, 167, 0.3);
    
    &:hover { background: lighten($primary-color, 5%); transform: translateY(-1px); }
    &:active { transform: translateY(0); }
    &:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
  }
}

/* 覆盖 Element Plus 组件默认样式，使其融合 */
:deep(.el-input__wrapper), :deep(.el-select__wrapper) {
  box-shadow: none !important;
  background-color: #f5f5f5;
  border-radius: 6px;
  
  &.is-focus {
    background-color: #fff;
    box-shadow: 0 0 0 1px $primary-color !important;
  }
}
</style>