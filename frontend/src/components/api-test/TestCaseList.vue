<template>
  <div class="test-cases-sidebar">
    <div class="sidebar-header">
      <h3>测试用例列表</h3>
      <el-button @click="$emit('refresh')" size="small" type="primary">
        刷新
      </el-button>
    </div>
    <div class="test-cases-list">
      <div
        v-for="testCase in testCases"
        :key="testCase.id"
        class="test-case-item"
        :class="{ active: selectedTestCase?.id === testCase.id }"
        @click="$emit('select', testCase)"
      >
        <div class="case-method" :class="getMethodClass(testCase.method)">
          {{ testCase.method }}
        </div>
        <div class="case-info">
          <div class="case-name">{{ testCase.case_name }}</div>
          <div class="case-url">{{ testCase.url }}</div>
        </div>
        <div class="case-actions">
          <el-button @click.stop="$emit('delete', testCase.id)" size="small" type="danger" text>
            删除
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getMethodClass } from '@/utils/apiTestUtils'

defineProps({
  testCases: {
    type: Array,
    default: () => []
  },
  selectedTestCase: {
    type: Object,
    default: null
  }
})

defineEmits(['refresh', 'select', 'delete'])
</script>

<style scoped>
.test-cases-sidebar {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #e6e8eb;
}

.test-cases-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.test-case-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e6e8eb;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.test-case-item:hover {
  border-color: #409eff;
}

.test-case-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.case-method {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
  margin-right: 10px;
  min-width: 50px;
  text-align: center;
}

.method-get { background: #67c23a; }
.method-post { background: #409eff; }
.method-put { background: #e6a23c; }
.method-patch { background: #909399; }
.method-delete { background: #f56c6c; }
.method-default { background: #909399; }

.case-info {
  flex: 1;
  min-width: 0;
}

.case-name {
  font-weight: 600;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.case-url {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.case-actions {
  margin-left: 10px;
}
</style>