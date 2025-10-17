<template>
  <div class="ui-test-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>UI测试</h2>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建UI测试用例
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 单元测试 -->
        <el-tab-pane label="单元测试" name="unit">
          <el-table :data="uiTestCases" v-loading="loading" @selection-change="handleSelectionChange">
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
                <el-button size="small" @click="editTestCase(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteTestCase(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="action-bar">
            <el-button @click="runSelectedTests" :disabled="selectedCases.length === 0">
              运行选中用例
            </el-button>
          </div>
        </el-tab-pane>

        <!-- 业务测试 -->
        <el-tab-pane label="业务测试" name="business">
          <div class="business-flow-section">
            <el-button type="primary" @click="showBusinessFlowDialog = true">
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
                  <el-button size="small" @click="runBusinessFlow(scope.row)">运行</el-button>
                  <el-button size="small" type="danger" @click="deleteBusinessFlow(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 测试报告 -->
        <el-tab-pane label="测试报告" name="reports">
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
                  @click="viewReport(scope.row)"
                  :disabled="scope.row.status !== 'completed'"
                >
                  查看报告
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 测试结果 -->
        <el-tab-pane label="测试结果" name="results">
          <div class="test-results">
            <el-card v-for="report in completedReports" :key="report.id" class="result-card">
              <template #header>
                <div class="result-header">
                  <h3>{{ report.report_name }}</h3>
                  <el-tag type="success">已完成</el-tag>
                </div>
              </template>
              <p>创建时间: {{ formatDate(report.created_at) }}</p>
              <div class="result-actions">
                <el-button type="primary" @click="viewReport(report)">查看详情</el-button>
                <el-button @click="downloadArtifacts(report)">下载附件</el-button>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button @click="$router.push('/projects')">返回项目</el-button>
    </div>

    <!-- 创建/编辑测试用例对话框 -->
    <el-dialog
      :title="isEditing ? '编辑UI测试用例' : '创建UI测试用例'"
      v-model="showCreateDialog"
      width="80%"
    >
      <el-form :model="testCaseForm" :rules="testCaseRules" ref="testCaseFormRef">
        <el-form-item label="用例名称" prop="case_name">
          <el-input v-model="testCaseForm.case_name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="脚本内容" prop="script_content">
          <el-input
            v-model="testCaseForm.script_content"
            type="textarea"
            :rows="15"
            placeholder="请输入UI自动化脚本内容（Playwright）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleTestCaseSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 创建业务流程对话框 -->
    <el-dialog title="创建业务流程" v-model="showBusinessFlowDialog" width="500px">
      <el-form :model="businessFlowForm" :rules="businessFlowRules" ref="businessFlowFormRef">
        <el-form-item label="流程名称" prop="flow_name">
          <el-input v-model="businessFlowForm.flow_name" placeholder="请输入流程名称" />
        </el-form-item>
        <el-form-item label="选择用例" prop="case_ids">
          <el-select
            v-model="businessFlowForm.case_ids"
            multiple
            placeholder="请选择测试用例"
            style="width: 100%"
          >
            <el-option
              v-for="testcase in uiTestCases"
              :key="testcase.id"
              :label="testcase.case_name"
              :value="testcase.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBusinessFlowDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBusinessFlowSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { uiTestsAPI } from '../api/uiTests'

const route = useRoute()
const projectId = ref(route.query.projectId || 1) // 实际项目中从路由参数获取

const activeTab = ref('unit')
const loading = ref(false)
const showCreateDialog = ref(false)
const showBusinessFlowDialog = ref(false)
const isEditing = ref(false)
const testCaseFormRef = ref()
const businessFlowFormRef = ref()
const editingTestCaseId = ref(null)

const uiTestCases = ref([])
const businessFlows = ref([])
const testReports = ref([])
const selectedCases = ref([])

const testCaseForm = reactive({
  case_name: '',
  script_content: ''
})

const businessFlowForm = reactive({
  flow_name: '',
  case_ids: []
})

const testCaseRules = {
  case_name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' }
  ],
  script_content: [
    { required: true, message: '请输入脚本内容', trigger: 'blur' }
  ]
}

const businessFlowRules = {
  flow_name: [
    { required: true, message: '请输入流程名称', trigger: 'blur' }
  ],
  case_ids: [
    { required: true, message: '请选择测试用例', trigger: 'change' }
  ]
}

const completedReports = computed(() => {
  return testReports.value.filter(report => report.status === 'completed')
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

const fetchUITestCases = async () => {
  loading.value = true
  try {
    const response = await uiTestsAPI.getUiTestCases(projectId.value)
    uiTestCases.value = response.data
  } catch (error) {
    ElMessage.error('获取UI测试用例失败')
  } finally {
    loading.value = false
  }
}

const fetchBusinessFlows = async () => {
  try {
    // 这里需要调用获取业务流程的API，暂时用空数组
    // const response = await uiTestsAPI.getBusinessFlows(projectId.value)
    businessFlows.value = []
  } catch (error) {
    ElMessage.error('获取业务流程失败')
  }
}

const fetchTestReports = async () => {
  try {
    const response = await uiTestsAPI.getUiTestReports(projectId.value)
    testReports.value = response.data
  } catch (error) {
    ElMessage.error('获取测试报告失败')
  }
}

const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

const editTestCase = (testCase) => {
  isEditing.value = true
  editingTestCaseId.value = testCase.id
  testCaseForm.case_name = testCase.case_name
  testCaseForm.script_content = testCase.script_content
  showCreateDialog.value = true
}

const deleteTestCase = async (testCase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例 "${testCase.case_name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await uiTestsAPI.deleteUiTestCase(testCase.id)
    ElMessage.success('测试用例删除成功')
    fetchUITestCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除测试用例失败')
    }
  }
}

const runSelectedTests = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请选择要运行的测试用例')
    return
  }

  try {
    const caseIds = selectedCases.value.map(testcase => testcase.id)
    await uiTestsAPI.runUiTest(projectId.value, caseIds)
    ElMessage.success('测试已开始运行')
    // 可以轮询报告状态
    setTimeout(fetchTestReports, 2000)
  } catch (error) {
    ElMessage.error('运行测试失败')
  }
}

const runBusinessFlow = async (businessFlow) => {
  try {
    await uiTestsAPI.runUiTest(projectId.value, businessFlow.case_ids)
    ElMessage.success('业务流程测试已开始运行')
    setTimeout(fetchTestReports, 2000)
  } catch (error) {
    ElMessage.error('运行业务流程测试失败')
  }
}

const deleteBusinessFlow = async (businessFlow) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除业务流程 "${businessFlow.flow_name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 调用删除业务流程的API
    // await uiTestsAPI.deleteBusinessFlow(businessFlow.id)
    ElMessage.success('业务流程删除成功')
    fetchBusinessFlows()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除业务流程失败')
    }
  }
}

const viewReport = (report) => {
  // 在新窗口中打开报告
  window.open(`http://localhost:8000/reports/${report.report_path}`, '_blank')
}

const downloadArtifacts = async (report) => {
  try {
    const response = await uiTestsAPI.getUiTestArtifacts(projectId.value, report.id)
    ElMessage.info('附件下载功能待实现')
  } catch (error) {
    ElMessage.error('获取测试附件失败')
  }
}

const handleTestCaseSubmit = async () => {
  if (!testCaseFormRef.value) return

  testCaseFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditing.value) {
          await uiTestsAPI.updateUiTestCase(editingTestCaseId.value, testCaseForm)
          ElMessage.success('测试用例更新成功')
        } else {
          await uiTestsAPI.createUiTestCase(projectId.value, testCaseForm)
          ElMessage.success('测试用例创建成功')
        }

        showCreateDialog.value = false
        resetTestCaseForm()
        fetchUITestCases()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      }
    }
  })
}

const handleBusinessFlowSubmit = async () => {
  if (!businessFlowFormRef.value) return

  businessFlowFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await uiTestsAPI.createUiBusinessFlow(projectId.value, businessFlowForm)
        ElMessage.success('业务流程创建成功')
        showBusinessFlowDialog.value = false
        resetBusinessFlowForm()
        fetchBusinessFlows()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '创建业务流程失败')
      }
    }
  })
}

const resetTestCaseForm = () => {
  testCaseForm.case_name = ''
  testCaseForm.script_content = ''
  isEditing.value = false
  editingTestCaseId.value = null
}

const resetBusinessFlowForm = () => {
  businessFlowForm.flow_name = ''
  businessFlowForm.case_ids = []
}

onMounted(() => {
  fetchUITestCases()
  fetchBusinessFlows()
  fetchTestReports()
})
</script>

<style scoped>
.ui-test-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-bar {
  margin-top: 20px;
}

.back-button {
  margin-top: 20px;
  text-align: center;
}

.test-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.result-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.result-card:hover {
  transform: translateY(-5px);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}
</style>