<template>
  <div class="result-view">
    <div class="view-header">
      <el-button link icon="ArrowLeft" @click="$emit('back')">返回试卷列表</el-button>
      <h3 class="title">考试成绩看板 - ID: {{ examId }}</h3>
    </div>

    <div class="placeholder-content">
      <div class="icon">📊</div>
      <h4>成绩分析模块开发中...</h4>
      <p>后续将在此展示：平均分、最高分、及格率以及学生答题明细列表</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ examId: number | null }>()
defineEmits(['back'])
</script>

<style scoped lang="scss">
.result-view {
  height: 100%; background: white; border-radius: 16px; display: flex; flex-direction: column;
  box-shadow: 0 4px 20px rgba(0,0,0,0.02); overflow: hidden;
}
.view-header {
  padding: 20px 30px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 20px;
  .title { font-size: 18px; color: #333; margin: 0; }
}
.placeholder-content {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #999;
  .icon { font-size: 64px; margin-bottom: 20px; }
  h4 { color: #666; margin-bottom: 10px; }
}
</style>