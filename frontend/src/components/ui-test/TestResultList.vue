<template>
  <div class="test-result-list">
    <div class="test-results">
      <el-card
        v-for="report in completedReports"
        :key="report.id"
        class="result-card"
      >
        <template #header>
          <div class="result-header">
            <h3>{{ report.report_name }}</h3>
            <el-tag type="success">已完成</el-tag>
          </div>
        </template>
        <p>创建时间: {{ formatDate(report.created_at) }}</p>
        <div class="result-actions">
          <el-button type="primary" @click="emit('view', report)">查看详情</el-button>
          <el-button @click="emit('download', report)">下载附件</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { formatDate } from '@/utils/uiTestUtils'

const props = defineProps({
  completedReports: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['view', 'download'])
</script>

<style scoped>
.test-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.result-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
  height: fit-content;
}

.result-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 5px;
}

.result-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .test-results {
    grid-template-columns: 1fr;
  }

  .result-actions {
    flex-direction: column;
  }

  .result-actions .el-button {
    width: 100%;
  }
}
</style>