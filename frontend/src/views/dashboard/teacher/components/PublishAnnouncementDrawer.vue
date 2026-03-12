<template>
  <el-drawer
    v-model="visible"
    title="发布新公告"
    size="500px"
    destroy-on-close
    class="publish-drawer"
  >
    <div class="drawer-content">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        
        <!-- 标题 -->
        <el-form-item label="公告标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题 (50字以内)" maxlength="50" show-word-limit />
        </el-form-item>

        <!-- 类型与置顶 -->
        <div class="form-row">
          <el-form-item label="公告类型" prop="type" style="flex: 1">
            <el-select v-model="form.type" placeholder="选择类型" style="width: 100%">
              <el-option label="📢 常规通知" value="normal" />
              <el-option label="📌 紧急通知" value="urgent" />
              <el-option label="📝 课程更新" value="course" />
              <el-option label="💡 温馨提示" value="tip" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="是否置顶" prop="is_pinned" style="width: 100px">
            <el-switch v-model="form.is_pinned" active-color="#00c9a7" />
          </el-form-item>
        </div>

        <!-- 发布范围 -->
        <el-form-item label="发布范围">
          <el-radio-group v-model="form.target_type" class="custom-radio">
            <el-radio label="class">指定班级</el-radio>
            <el-radio label="all">全部班级</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="form.target_type === 'class'" prop="class_ids">
          <el-select 
            v-model="form.class_ids" 
            multiple 
            placeholder="请选择接收班级" 
            style="width: 100%"
            collapse-tags
          >
            <el-option v-for="c in classOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>

        <!-- 正文 -->
        <el-form-item label="公告内容" prop="content">
          <el-input 
            v-model="form.content" 
            type="textarea" 
            :rows="6" 
            placeholder="请输入公告正文..." 
            class="content-input"
          />
        </el-form-item>

      </el-form>
    </div>

    <template #footer>
      <div class="drawer-footer">
        <button class="btn-cancel" @click="visible = false">取消</button>
        <button class="btn-submit" @click="handleSubmit" :disabled="loading">
          {{ loading ? '发布中...' : '立即发布' }}
        </button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { getMyClasses } from '@/api/course'
import { createAnnouncement } from '@/api/announcement'
import { ElMessage, type FormInstance } from 'element-plus'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const formRef = ref<FormInstance>()
const classOptions = ref<any[]>([])

const form = reactive({
  title: '',
  type: 'normal',
  target_type: 'class',
  class_ids: [],
  is_pinned: false,
  content: ''
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  class_ids: [{ required: true, message: '请至少选择一个班级', trigger: 'change' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

onMounted(async () => {
  const res = await getMyClasses()
  classOptions.value = res
})

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (form.target_type === 'class' && form.class_ids.length === 0) {
        return ElMessage.warning('请选择班级')
      }

      loading.value = true
      try {
        await createAnnouncement({
          ...form,
          target_type: form.target_type as 'all' | 'class'
        })
        ElMessage.success('发布成功')
        visible.value = false
        emit('success')
        // 重置表单
        form.title = ''
        form.content = ''
        form.class_ids = []
      } catch (e) {
        console.error(e)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
$primary: #00c9a7;

.drawer-content { padding: 10px 20px; }
.form-row { display: flex; gap: 20px; }

/* 输入框美化 */
:deep(.el-input__wrapper), :deep(.el-textarea__inner) {
  box-shadow: 0 0 0 1px #e0e0e0 inset;
  border-radius: 8px;
  padding: 8px 12px;
  &:focus, &:hover { box-shadow: 0 0 0 1px $primary inset !important; }
}

/* 按钮样式复用 */
.drawer-footer {
  display: flex; justify-content: flex-end; gap: 12px; padding: 20px; border-top: 1px solid #eee;
  
  .btn-cancel {
    background: white; border: 1px solid #ddd; color: #666;
    padding: 10px 24px; border-radius: 8px; cursor: pointer;
    &:hover { background: #f5f5f5; }
  }

  .btn-submit {
    background: $primary; color: white; border: none;
    padding: 10px 24px; border-radius: 8px; cursor: pointer; font-weight: 600;
    box-shadow: 0 4px 12px rgba(0, 201, 167, 0.3);
    &:hover { transform: translateY(-1px); filter: brightness(1.05); }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}
</style>