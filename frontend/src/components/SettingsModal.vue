<template>
  <el-dialog
    v-model="visible"
    title="修改登录密码"
    width="400px"
    :close-on-click-modal="false"
    destroy-on-close
    class="settings-modal-premium"
    append-to-body
    align-center
  >
    <div class="modal-body-content">
      <el-form 
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="premium-form"
      >
        <el-form-item label="当前旧密码" prop="old_password">
          <el-input 
            v-model="form.old_password" 
            type="password" 
            show-password 
            placeholder="验证当前密码"
            class="custom-input"
          />
        </el-form-item>

        <el-form-item label="设置新密码" prop="new_password">
          <el-input 
            v-model="form.new_password" 
            type="password" 
            show-password 
            placeholder="新密码 (至少6位)"
            class="custom-input"
          />
        </el-form-item>

        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input 
            v-model="form.confirm_password" 
            type="password" 
            show-password 
            placeholder="再次输入以确认"
            class="custom-input"
          />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="modal-footer-content">
        <button class="btn-cancel" @click="visible = false">取消</button>
        <button class="btn-confirm" @click="handleSubmit">
          <span v-if="!loading">确认修改</span>
          <span v-else>提交中...</span>
        </button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { changePassword } from '@/api/auth'
import { ElMessage, type FormInstance } from 'element-plus'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validatePass2 = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.new_password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const rules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [{ validator: validatePass2, trigger: 'blur' }]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await changePassword({
          old_password: form.old_password,
          new_password: form.new_password
        })
        ElMessage.success('密码修改成功，下次登录生效')
        visible.value = false
        form.old_password = ''
        form.new_password = ''
        form.confirm_password = ''
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="scss">
/* 全局覆盖 el-dialog 样式 (必须放在非 scoped 块中) */
.settings-modal-premium {
  border-radius: 20px !important; /* 大圆角 */
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;

  .el-dialog__header {
    padding: 30px 30px 10px;
    margin-right: 0;
    text-align: center;
    .el-dialog__title {
      font-size: 18px;
      font-weight: 800;
      color: #2c3e50;
      letter-spacing: 0.5px;
    }
    .el-dialog__headerbtn {
      top: 25px;
      right: 25px;
      .el-dialog__close { font-size: 20px; color: #999; transition: color 0.2s; }
      &:hover .el-dialog__close { color: #333; }
    }
  }

  .el-dialog__body {
    padding: 10px 35px 20px;
  }

  .el-dialog__footer {
    padding: 0 35px 35px;
  }
}
</style>

<style scoped lang="scss">
$primary: #00c9a7;

.premium-form {
  :deep(.el-form-item__label) {
    font-size: 13px;
    color: #606266;
    font-weight: 600;
    margin-bottom: 6px !important;
  }

  /* 输入框核心美化：浅灰背景，无边框风格 */
  :deep(.el-input__wrapper) {
    background-color: #f7f8fa; /* 浅灰底 */
    box-shadow: none !important; /* 去掉默认边框 */
    border: 1px solid transparent;
    border-radius: 12px; /* 圆角更大 */
    padding: 10px 15px;
    transition: all 0.3s ease;
    
    input { color: #333; font-weight: 500; }

    &:hover {
      background-color: #f0f2f5;
    }

    /* 聚焦时变白，加主色边框和柔和阴影 */
    &.is-focus {
      background-color: #fff;
      border-color: $primary;
      box-shadow: 0 0 0 4px rgba(0, 201, 167, 0.1) !important;
    }
  }
}

.modal-footer-content {
  display: flex;
  gap: 15px;
  margin-top: 10px;

  button {
    flex: 1;
    padding: 12px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
  }

  .btn-cancel {
    background-color: #f5f7fa;
    color: #909399;
    &:hover { background-color: #eef0f4; color: #606266; }
  }

  .btn-confirm {
    background: $primary;
    color: white;
    box-shadow: 0 4px 12px rgba(0, 201, 167, 0.3);
    &:hover { 
      filter: brightness(1.05); 
      transform: translateY(-1px); 
      box-shadow: 0 6px 16px rgba(0, 201, 167, 0.4);
    }
    &:active { transform: translateY(0); }
  }
}
</style>