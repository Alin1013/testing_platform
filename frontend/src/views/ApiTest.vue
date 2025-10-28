<template>
  <div class="api-tester">
    <div class="tester-header">
      <h2>API 测试工具</h2>
      <div class="header-actions">
        <el-button @click="showSaveDialog = true" type="primary" :disabled="!currentRequest.url">
          保存测试用例
        </el-button>
        <el-button @click="showBusinessFlowDialog = true" type="success" :disabled="testCases.length === 0">
          创建业务流程
        </el-button>
        <TestRunner
          :project-id="projectId"
          :selected-test-case="selectedTestCase"
          :test-cases="testCases"
          @test-completed="handleTestCompleted"
        />
        <el-button @click="clearAll" plain>清空</el-button>
      </div>
    </div>

    <div class="tester-body">
      <!-- 左侧：测试用例列表 -->
      <TestCaseList
        :test-cases="testCases"
        :selected-test-case="selectedTestCase"
        @refresh="loadTestCases"
        @select="loadTestCase"
        @delete="deleteTestCase"
      />

      <!-- 右侧：请求编辑和响应区域 -->
      <div class="request-editor">
        <RequestEditor
          :current-request="currentRequest"
          :active-request-tab="activeRequestTab"
          :can-send="canSend"
          :is-loading="isLoading"
          @update:activeRequestTab="updateActiveRequestTab"
          @send="handleSendRequest"
          @add-header="addHeader"
          @remove-header="removeHeader"
          @add-param="addParam"
          @remove-param="removeParam"
          @add-form-data="addFormData"
          @remove-form-data="removeFormData"
        />

        <ResponseViewer
          :response="response"
          :active-response-tab="activeResponseTab"
          :status-code-class="statusCodeClass"
          :formatted-response="formattedResponse"
          @update:activeResponseTab="updateActiveResponseTab"
        />
      </div>
    </div>

    <!-- 保存测试用例对话框 -->
    <TestCaseSaveDialog
      v-model="showSaveDialog"
      :project-id="projectId"
      :current-request="currentRequest"
      @saved="handleTestCaseSaved"
    />

    <!-- 创建业务流程对话框 -->
    <BusinessFlowDialog
      v-model="showBusinessFlowDialog"
      :project-id="projectId"
      :test-cases="testCases"
      @created="handleBusinessFlowCreated"
    />
  </div>
</template>

<script setup>
import { onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import { useApiTestStore } from '../stores/apiTestStore'
import { apiTestsAPI } from '../api/apiTests'

// 组件导入
import TestCaseList from '../components/api-test/TestCaseList.vue'
import RequestEditor from '../components/api-test/RequestEditor.vue'
import ResponseViewer from '../components/api-test/ResponseViewer.vue'
import TestCaseSaveDialog from '../components/api-test/TestCaseSaveDialog.vue'
import BusinessFlowDialog from '../components/api-test/BusinessFlowDialog.vue'
import TestRunner from '../components/api-test/TestRunner.vue'

const route = useRoute()
const store = useApiTestStore()

// 从store中获取状态和actions
const {
  testCases,
  selectedTestCase,
  isLoading,
  isRunningTests,
  currentRequest,
  response,
  activeRequestTab,
  activeResponseTab,
  showSaveDialog,
  showBusinessFlowDialog,
  canSend,
  statusCodeClass,
  formattedResponse,
  loadTestCases,
  loadTestCase,
  sendRequest,
  clearAll,
  addHeader,
  removeHeader,
  addParam,
  removeParam,
  addFormData,
  removeFormData
} = store

// 计算属性
const projectId = computed(() => route.params.projectId || 1)

// 更新方法
const updateActiveRequestTab = (tab) => {
  activeRequestTab.value = tab
}

const updateActiveResponseTab = (tab) => {
  activeResponseTab.value = tab
}

// 处理发送请求
const handleSendRequest = async () => {
  const result = await sendRequest()
  if (result.success) {
    ElMessage.success(result.message)
  } else {
    ElMessage.error(result.message)
  }
}

// 方法
const handleTestCaseSaved = () => {
  loadTestCases(projectId.value)
  ElMessage.success('测试用例保存成功')
}

const handleBusinessFlowCreated = () => {
  ElMessage.success('业务流程创建成功')
}

const handleTestCompleted = () => {
  ElMessage.success('测试执行完成，请查看测试报告')
  // 可以在这里刷新测试报告列表
}

const deleteTestCase = async (testCaseId) => {
  try {
    await ElMessageBox.confirm('确定删除这个测试用例吗？', '提示', {
      type: 'warning'
    })

    await apiTestsAPI.deleteApiTestCase(testCaseId)
    ElMessage.success('删除成功')
    loadTestCases(projectId.value)

    if (selectedTestCase.value?.id === testCaseId) {
      selectedTestCase.value = null
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 监听项目ID变化
watch(projectId, (newProjectId) => {
  if (newProjectId) {
    loadTestCases(newProjectId)
  }
})

// 生命周期
onMounted(() => {
  loadTestCases(projectId.value)
})
</script>

<style scoped>
.api-tester {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.tester-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e6e8eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tester-body {
  flex: 1;
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.request-editor {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

@media (max-width: 768px) {
  .tester-body {
    grid-template-columns: 1fr;
  }
}
</style>