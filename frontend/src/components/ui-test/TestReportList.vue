<template>
  <div class="test-report-list">
    <el-table :data="testReports">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="report_name" label="报告名称" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button
            size="small"
            @click="emit('view', scope.row)"
            :disabled="scope.row.status !== 'completed'"
          >
            查看报告
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { formatDate, getStatusType } from '@/utils/uiTestUtils'

const props = defineProps({
  testReports: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['view'])
</script>