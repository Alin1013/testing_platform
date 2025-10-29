<template>
  <div class="ui-test-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="$router.push('/projects')" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回项目
      </el-button>
      <h2 class="page-title">UI测试</h2>
      <div style="width: 120px"></div>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建UI测试用例
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 单元测试 -->
        <el-tab-pane label="单元测试" name="unit">
          <TestCaseList
            :test-cases="uiTestStore.uiTestCases"
            :loading="uiTestStore.loading"
            @selection-change="uiTestStore.setSelectedCases"
            @edit="handleEditTestCase"
            @delete="handleDeleteTestCase"
            @run-selected="handleRunSelectedTests"
          />
        </el-tab-pane>

        <!-- 业务测试 -->
        <el-tab-pane label="业务测试" name="business">
          <BusinessFlowList
            :business-flows="uiTestStore.businessFlows"
            @create="showBusinessFlowDialog = true"
            @run="handleRunBusinessFlow"
            @delete="handleDeleteBusinessFlow"
          />
        </el-tab-pane>

        <!-- 测试报告 -->
        <el-tab-pane label="测试报告" name="reports">
          <TestReportList
            :test-reports="uiTestStore.testReports"
            @view="handleViewReport"
          />
        </el-tab-pane>

        <!-- 测试结果 -->
        <el-tab-pane label="测试结果" name="results">
          <TestResultList
            :completed-reports="uiTestStore.completedReports"
            @view="handleViewReport"
            @download="handleDownloadArtifacts"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button @click="$router.push('/projects')">返回项目</el-button>
    </div>

    <!-- 对话框组件 -->
    <TestCaseDialog
      v-model="showCreateDialog"
      :editing-data="editingTestCase"
      @submit="handleTestCaseSubmit"
      @cancel="handleDialogCancel"
    />

    <BusinessFlowDialog
      v-model="showBusinessFlowDialog"
      :test-cases="uiTestStore.uiTestCases"
      @submit="handleBusinessFlowSubmit"
      @cancel="handleDialogCancel"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowLeft } from '@element-plus/icons-vue'

// Store
import { useUiTestStore } from '@/stores/uiTestStore'

// Components
import TestCaseDialog from '@/components/ui-test/TestCaseDialog.vue'
import BusinessFlowDialog from '@/components/ui-test/BusinessFlowDialog.vue'
import TestCaseList from '@/components/ui-test/TestCaseList.vue'
import BusinessFlowList from '@/components/ui-test/BusinessFlowList.vue'
import TestReportList from '@/components/ui-test/TestReportList.vue'
import TestResultList from '@/components/ui-test/TestResultList.vue'

// Utils
import { generatePlaywrightScript } from '@/utils/uiTestUtils'
import { uiTestsAPI } from '@/api/uiTests'

const route = useRoute()
const router = useRouter()
const uiTestStore = useUiTestStore()

const projectId = ref(route.query.projectId || 1)

// 响应式数据
const activeTab = ref('unit')
const showCreateDialog = ref(false)
const showBusinessFlowDialog = ref(false)
const editingTestCase = ref(null)

// 轮询相关
let pollingInterval = null

// 事件处理函数
const handleEditTestCase = (testCase) => {
  editingTestCase.value = testCase
  showCreateDialog.value = true
}

const handleDeleteTestCase = async (testCase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例 "${testCase.case_name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await uiTestStore.deleteTestCase(testCase.id, projectId.value)
    ElMessage.success('测试用例删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除测试用例失败:', error)
      if (!error.response) {
        ElMessage.error('删除测试用例失败: 网络连接错误')
      }
    }
  }
}

const handleRunSelectedTests = async () => {
  if (uiTestStore.selectedCases.length === 0) {
    ElMessage.warning('请选择要运行的测试用例')
    return
  }

  try {
    const caseIds = uiTestStore.selectedCases.map(testcase => testcase.id)
    await uiTestStore.runUiTest(projectId.value, caseIds)
    ElMessage.success('测试已开始运行，请稍后查看报告')
    startPollingReports()
  } catch (error) {
    console.error('运行测试失败:', error)
    if (!error.response) {
      ElMessage.error('运行测试失败: 网络连接错误')
    }
  }
}

const handleRunBusinessFlow = async (businessFlow) => {
  if (!businessFlow.case_ids || businessFlow.case_ids.length === 0) {
    ElMessage.warning('该业务流程没有包含任何测试用例')
    return
  }

  try {
    await uiTestStore.runUiTest(projectId.value, businessFlow.case_ids)
    ElMessage.success('业务流程测试已开始运行，请稍后查看报告')
    startPollingReports()
  } catch (error) {
    console.error('运行业务流程测试失败:', error)
    if (!error.response) {
      ElMessage.error('运行业务流程测试失败: 网络连接错误')
    }
  }
}

const handleDeleteBusinessFlow = async (businessFlow) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除业务流程 "${businessFlow.flow_name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await uiTestStore.deleteBusinessFlow(businessFlow.id, projectId.value)
    ElMessage.success('业务流程删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除业务流程失败:', error)
      if (!error.response) {
        ElMessage.error('删除业务流程失败: 网络连接错误')
      }
    }
  }
}

const handleViewReport = (report) => {
  if (!report.report_path) {
    ElMessage.warning('报告路径不存在')
    return
  }

  const reportUrl = report.report_path.startsWith('http')
    ? report.report_path
    : `/reports/${report.report_path}`

  window.open(reportUrl, '_blank')
}

const handleDownloadArtifacts = async (report) => {
  try {
    const response = await uiTestsAPI.getUiTestArtifacts(projectId.value, report.id)
    if (response.data.screenshots.length === 0 && response.data.videos.length === 0) {
      ElMessage.info('该报告没有可下载的附件')
      return
    }

    ElMessage.success('开始下载附件')
  } catch (error) {
    console.error('获取测试附件失败:', error)
    if (!error.response) {
      ElMessage.error('获取测试附件失败: 网络连接错误')
    }
  }
}

const handleTestCaseSubmit = async (formData) => {
  try {
    // 生成Playwright脚本
    const scriptContent = generatePlaywrightScript(formData)

    // 准备提交数据
    const submitData = {
      case_name: formData.case_name,
      base_url: formData.base_url,
      steps: formData.steps,
      script_content: scriptContent,
      record: formData.record,
      project_id: projectId.value
    }

    if (formData.isEditing && editingTestCase.value) {
      await uiTestStore.updateTestCase(editingTestCase.value.id, submitData)
      ElMessage.success('测试用例更新成功')
    } else {
      await uiTestStore.createTestCase(projectId.value, submitData)
      ElMessage.success('测试用例创建成功')
    }

    editingTestCase.value = null
  } catch (error) {
    console.error('提交测试用例失败:', error)
    if (!error.response) {
      ElMessage.error('操作失败: 网络连接错误')
    }
  }
}

const handleBusinessFlowSubmit = async (formData) => {
  try {
    await uiTestStore.createBusinessFlow(projectId.value, formData)
    ElMessage.success('业务流程创建成功')
  } catch (error) {
    console.error('创建业务流程失败:', error)
    if (!error.response) {
      ElMessage.error('创建业务流程失败: 网络连接错误')
    }
  }
}

const handleDialogCancel = () => {
  editingTestCase.value = null
}

// 轮询报告状态
const startPollingReports = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
  }

  uiTestStore.fetchTestReports(projectId.value)

  pollingInterval = setInterval(async () => {
    await uiTestStore.fetchTestReports(projectId.value)

    const runningReports = uiTestStore.testReports.filter(r => r.status === 'running')
    if (runningReports.length === 0) {
      clearInterval(pollingInterval)
      pollingInterval = null
      ElMessage.success('所有测试运行完成')
    }
  }, 3000)

  setTimeout(() => {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
      ElMessage.info('报告轮询已停止')
    }
  }, 600000)
}

// 初始化
onMounted(() => {
  uiTestStore.fetchUITestCases(projectId.value)
  uiTestStore.fetchBusinessFlows(projectId.value)
  uiTestStore.fetchTestReports(projectId.value)
})

onUnmounted(() => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
  }
})
</script>

<style scoped>
.ui-test-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.page-title {
  text-align: center;
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  flex: 1;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.back-button {
  margin-top: 20px;
  text-align: center;
  padding: 20px 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .page-title {
    order: -1;
  }

  .back-button {
    align-self: flex-start;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .ui-test-container {
    padding: 10px;
  }
}
</style>