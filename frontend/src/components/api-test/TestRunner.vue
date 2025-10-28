<template>
  <div class="test-runner">
    <el-button
      @click="runTests"
      :loading="isRunningTests"
      type="warning"
      :disabled="!selectedTestCase"
    >
      {{ isRunningTests ? '运行中...' : '执行测试' }}
    </el-button>

    <el-button @click="runAllTests" :loading="isRunningTests" type="danger">
      执行全部测试
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { apiTestsAPI } from '@/api/apiTests'

const props = defineProps({
  projectId: {
    type: [String, Number],
    required: true
  },
  selectedTestCase: {
    type: Object,
    default: null
  },
  testCases: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['test-completed'])

const isRunningTests = ref(false)

const runTests = async () => {
  if (!props.selectedTestCase) {
    ElMessage.warning('请先选择一个测试用例')
    return
  }

  try {
    isRunningTests.value = true
    await apiTestsAPI.runApiTest(props.projectId, [props.selectedTestCase.id])
    ElMessage.success('测试已开始执行，请查看测试报告')
    emit('test-completed')
  } catch (error) {
    ElMessage.error('执行测试失败: ' + error.message)
  } finally {
    isRunningTests.value = false
  }
}

const runAllTests = async () => {
  if (props.testCases.length === 0) {
    ElMessage.warning('没有可执行的测试用例')
    return
  }

  try {
    isRunningTests.value = true
    const testCaseIds = props.testCases.map(tc => tc.id)
    await apiTestsAPI.runApiTest(props.projectId, testCaseIds)
    ElMessage.success('全部测试已开始执行，请查看测试报告')
    emit('test-completed')
  } catch (error) {
    ElMessage.error('执行测试失败: ' + error.message)
  } finally {
    isRunningTests.value = false
  }
}
</script>

<style scoped>
.test-runner {
  display: flex;
  gap: 10px;
}
</style>