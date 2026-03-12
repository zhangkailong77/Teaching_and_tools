<template>
  <div class="step-container">
    <el-form label-position="top">
      <el-form-item label="试卷标题">
        <el-input v-model="form.title" placeholder="例如：2025年跨境电商期末考试A卷" size="large" />
      </el-form-item>

      <el-form-item label="组卷方式">
        <div class="mode-cards">
          <div 
            class="mode-card" 
            :class="{ active: form.mode === 1 }"
            @click="form.mode = 1"
          >
            <div class="icon">🖐</div>
            <h4>手动组卷</h4>
            <p>从题库中逐一挑选题目，适合精准命题。</p>
          </div>

          <div 
            class="mode-card" 
            :class="{ active: form.mode === 2 }"
            @click="form.mode = 2"
          >
            <div class="icon">🎲</div>
            <h4>随机组卷</h4>
            <p>设置策略（如：单选10题+判断5题），系统自动生成。</p>
          </div>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ modelValue: any }>()
const emit = defineEmits(['update:modelValue'])

const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>

<style scoped lang="scss">
.mode-cards {
  display: flex; gap: 20px;
  .mode-card {
    flex: 1; border: 2px solid #eee; border-radius: 12px; padding: 20px; cursor: pointer; transition: all 0.2s;
    text-align: center;
    &:hover { border-color: #b2ebf2; background: #e0f7fa; }
    &.active { border-color: #00c9a7; background: #e0f2f1; }
    
    .icon { font-size: 32px; margin-bottom: 10px; }
    h4 { margin: 0 0 5px; color: #333; }
    p { font-size: 12px; color: #999; margin: 0; }
  }
}
</style>