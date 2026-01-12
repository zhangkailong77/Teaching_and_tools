<template>
  <el-drawer
    v-model="visible"
    title="批量导入试题"
    direction="rtl"
    size="600px"
    class="hw-drawer"
    destroy-on-close
  >
    <div class="homework-body">
      <!-- 1. 引导步骤 -->
      <div class="import-steps">
        <div class="step-item">
          <div class="step-num">1</div>
          <div class="step-content">
            <p class="step-title">下载标准模板</p>
            <p class="step-desc">请务必使用系统提供的模板填写，确保题型、答案格式正确。</p>
            <el-button type="primary" link icon="Download" @click="downloadTemplate">下载试题模板.xlsx</el-button>
          </div>
        </div>

        <div class="step-item">
          <div class="step-num">2</div>
          <div class="step-content">
            <p class="step-title">上传填写好的文件</p>
            <p class="step-desc">仅支持 .xlsx 格式，单次建议不超过 200 道题。</p>
          </div>
        </div>
      </div>

      <!-- 2. 上传区域 -->
      <div class="upload-section">
        <el-upload
          class="upload-dragger-area"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :show-file-list="true"
          accept=".xlsx"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或 <em>点击上传</em>
          </div>
        </el-upload>
      </div>

      <!-- 3. 结果反馈区域 (仅在上传后显示) -->
      <div v-if="result" class="result-panel" :class="result.fail > 0 ? 'has-error' : 'all-success'">
        <div class="res-header">
          <el-icon><InfoFilled /></el-icon> 导入任务结束
        </div>
        <div class="res-stats">
          <div class="stat">总数 <span>{{ result.total }}</span></div>
          <div class="stat success">成功 <span>{{ result.success }}</span></div>
          <div class="stat fail">失败 <span>{{ result.fail }}</span></div>
        </div>
        <div v-if="result.logs.length > 0" class="error-logs">
          <p class="log-title">异常详情列表：</p>
          <ul>
            <li v-for="(msg, idx) in result.logs" :key="idx">{{ msg }}</li>
          </ul>
        </div>
      </div>

      <!-- 4. 底部操作 -->
      <div class="hw-footer">
        <button class="btn-cancel" @click="visible = false">关闭</button>
        <button 
          class="btn-primary" 
          @click="startUpload" 
          :disabled="!selectedFile || uploading"
        >
          {{ uploading ? '正在导入数据...' : '开始执行导入' }}
        </button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { batchImportQuestions } from '@/api/exam';
import { UploadFilled, InfoFilled } from '@element-plus/icons-vue';

const props = defineProps<{ modelValue: boolean }>();
const emit = defineEmits(['update:modelValue', 'success']);

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const selectedFile = ref<any>(null);
const uploading = ref(false);
const result = ref<any>(null);

const handleFileChange = (file: any) => {
  selectedFile.value = file;
  result.value = null; // 重置结果
};

const startUpload = async () => {
  if (!selectedFile.value) return;
  
  uploading.value = true;
  try {
    const res = await batchImportQuestions(selectedFile.value.raw);
    result.value = res;
    if (res.fail === 0) {
      ElMessage.success('全部题目导入成功！');
      emit('success');
    } else {
      ElMessage.warning(`导入完成，但有 ${res.fail} 条异常`);
      emit('success'); // 依然触发成功，因为部分可能已导入
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '导入失败');
  } finally {
    uploading.value = false;
  }
};

const downloadTemplate = () => {
  // 1. 获取后端基础地址 (从环境变量获取)
  let baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
  
  // 2. 同样的逻辑：去掉路径中的 /api/v1，得到服务器根地址
  baseUrl = baseUrl.replace('/api/v1', '');
  
  // 3. 确保末尾没有多余斜杠
  if (baseUrl.endsWith('/')) {
    baseUrl = baseUrl.slice(0, -1);
  }

  // 4. 拼接完整的文件路径
  const templateUrl = `${baseUrl}/static/templates/试题批量导入模板.xlsx`;
  
  // 5. 使用 window.open 下载
  window.open(templateUrl, '_blank');
};
</script>

<style scoped lang="scss">
$primary-color: #00c9a7;

.import-steps {
  margin-bottom: 30px;
  .step-item {
    display: flex; gap: 15px; margin-bottom: 20px;
    .step-num { 
      width: 24px; height: 24px; background: $primary-color; color: white; 
      border-radius: 50%; display: flex; align-items: center; justify-content: center;
      font-size: 13px; font-weight: bold; flex-shrink: 0;
    }
    .step-title { font-weight: 600; color: #2c3e50; margin: 0 0 4px; }
    .step-desc { font-size: 13px; color: #999; margin: 0; }
  }
}

.upload-section {
  margin-bottom: 30px;
  :deep(.el-upload-dragger) {
    border-radius: 12px;
    &:hover { border-color: $primary-color; }
  }
}

.result-panel {
  background: #f8f9fa; border-radius: 12px; padding: 20px; border: 1px solid #eee;
  .res-header { display: flex; align-items: center; gap: 8px; font-weight: 600; margin-bottom: 15px; }
  .res-stats {
    display: flex; gap: 25px; margin-bottom: 15px;
    .stat { 
      font-size: 13px; color: #666; 
      span { font-size: 18px; font-weight: bold; color: #333; margin-left: 5px; }
      &.success span { color: $primary-color; }
      &.fail span { color: #ff4d4f; }
    }
  }
  .error-logs {
    background: #fff; border: 1px solid #ffeef0; padding: 10px; border-radius: 8px;
    max-height: 150px; overflow-y: auto;
    .log-title { font-size: 12px; color: #ff4d4f; font-weight: 600; margin-bottom: 5px; }
    ul { padding-left: 20px; margin: 0; }
    li { font-size: 12px; color: #666; margin-bottom: 3px; }
  }
}

.hw-footer {
  display: flex; justify-content: flex-end; gap: 15px; border-top: 1px solid #eee; padding-top: 20px;
  button { padding: 10px 25px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s; }
  .btn-cancel { background: white; border: 1px solid #ddd; color: #666; }
  .btn-primary { 
    background: $primary-color; color: white; border: none;
    &:disabled { opacity: 0.5; cursor: not-allowed; }
  }
}
</style>