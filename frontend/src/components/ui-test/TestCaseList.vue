<template>
  <div class="test-case-list">
    <el-table
      :data="testCases"
      v-loading="loading"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="case_name" label="用例名称" />
      <el-table-column prop="created_at" label="创建时间">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="emit('edit', scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="emit('delete', scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="action-bar">
      <el-button
        @click="emit('run-selected')"
        :disabled="selectedCases.length === 0"
      >
        运行选中用例
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { formatDate } from '@/utils/uiTestUtils'

const props = defineProps({
  testCases: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['selection-change', 'edit', 'delete', 'run-selected'])

const selectedCases = ref([])

const handleSelectionChange = (selection) => {
  selectedCases.value = selection
  emit('selection-change', selection)
}

defineExpose({
  selectedCases
})
</script>

<style scoped>
.test-case-list {
  margin-top: 20px;
}

.action-bar {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}
</style>