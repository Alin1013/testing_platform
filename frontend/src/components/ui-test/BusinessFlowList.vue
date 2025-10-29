<template>
  <div class="business-flow-list">
    <el-button type="primary" @click="emit('create')">
      创建业务流程
    </el-button>

    <el-table :data="businessFlows" style="margin-top: 20px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="flow_name" label="流程名称" />
      <el-table-column prop="case_ids" label="包含用例数">
        <template #default="scope">
          {{ scope.row.case_ids ? scope.row.case_ids.length : 0 }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="emit('run', scope.row)">运行</el-button>
          <el-button size="small" type="danger" @click="emit('delete', scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
const props = defineProps({
  businessFlows: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['create', 'run', 'delete'])
</script>

<style scoped>
.business-flow-list {
  margin-top: 20px;
}
</style>