<template>
  <div class="step-container">
    <div class="config-card">
      <div class="card-header">
        <el-icon><Setting /></el-icon>
        <span>考试参数配置</span>
      </div>

      <el-form label-position="top" class="config-form">
        <!-- 第一行：时长与及格分 -->
        <el-row :gutter="40">
          <el-col :span="12">
            <el-form-item label="考试时长 (分钟)">
              <div class="input-tip">规定学生答题的总限时</div>
              <el-input-number 
                v-model="form.duration" 
                :min="1" 
                :max="300" 
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="及格分数">
              <div class="input-tip">当前试卷总分：<span class="highlight">{{ form.total_score }}</span> 分</div>
              <el-input-number 
                v-model="form.pass_score" 
                :min="0" 
                :max="form.total_score" 
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第二行：起止时间 -->
        <el-row :gutter="40">
          <el-col :span="12">
            <el-form-item label="开考时间">
              <div class="input-tip">学生最早可以开始考试的时间</div>
              <el-date-picker
                v-model="form.start_time"
                type="datetime"
                placeholder="选择开始时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
                :prefix-icon="Calendar"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="结束时间">
              <div class="input-tip">超过此时间将无法进入考试</div>
              <el-date-picker
                v-model="form.end_time"
                type="datetime"
                placeholder="选择结束时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
                :prefix-icon="Timer"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第三行：发布班级 -->
        <el-form-item label="发布对象 (班级)">
          <div class="input-tip">选择参加本次考试的班级</div>
          <el-select
            v-model="form.class_ids"
            multiple
            placeholder="请选择班级"
            style="width: 100%"
            class="custom-select"
          >
            <el-option
              v-for="item in classOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 底部预览统计提示 -->
    <div class="summary-info">
      <div class="info-item">
        <span class="label">试卷名称：</span>
        <span class="val">{{ form.title }}</span>
      </div>
      <div class="info-item">
        <span class="label">组卷模式：</span>
        <span class="val">{{ form.mode === 1 ? '手动组卷' : '随机组卷' }}</span>
      </div>
      <div class="info-item">
        <span class="label">题目总数：</span>
        <span class="val">{{ form.questions.length || '自动计算' }} 题</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Setting, Calendar, Timer } from '@element-plus/icons-vue'
import { getMyClasses } from '@/api/course'

const props = defineProps<{ modelValue: any }>()
const emit = defineEmits(['update:modelValue'])

const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const classOptions = ref<any[]>([])

// 初始化
onMounted(async () => {
  // 1. 获取班级列表
  try {
    const res = await getMyClasses()
    classOptions.value = res.data || res
  } catch (error) {
    console.error('获取班级列表失败', error)
  }

  // 2. 默认及格分为总分的60%
  if (form.value.total_score > 0) {
    form.value.pass_score = Math.floor(form.value.total_score * 0.6)
  }
})
</script>

<style scoped lang="scss">
$primary: #00c9a7;

.step-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 0;
}

.config-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);

  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 1px solid #f5f5f5;
    
    .el-icon {
      color: $primary;
      font-size: 20px;
    }
  }
}

.config-form {
  .input-tip {
    font-size: 12px;
    color: #999;
    margin-bottom: 8px;
    line-height: 1;

    .highlight {
      color: $primary;
      font-weight: bold;
    }
  }
  
  :deep(.el-form-item__label) {
    font-weight: 600;
    color: #333;
    padding-bottom: 0;
  }
}

/* 总结信息栏 */
.summary-info {
  margin-top: 30px;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  .info-item {
    display: flex;
    font-size: 14px;
    .label { color: #666; width: 80px; }
    .val { color: #333; font-weight: 600; }
  }
}

/* 统一样式覆盖 */
:deep(.el-input-number.is-controls-right .el-input__wrapper) {
  padding-left: 15px;
  padding-right: 40px;
}

:deep(.custom-date-picker), :deep(.custom-select) {
  .el-input__wrapper, .el-select__wrapper {
    border-radius: 8px;
  }
}
</style>