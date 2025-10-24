<template>
  <div class="api-test-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>API测试</h2>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建API测试用例
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 测试用例 -->
        <el-tab-pane label="测试用例" name="cases">
          <el-table
            :data="apiTestCases"
            v-loading="loading"
            @selection-change="handleSelectionChange"
            ref="casesTable"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="case_name" label="用例名称" />
            <el-table-column prop="method" label="请求方法">
              <template #default="scope">
                <el-tag :type="getMethodType(scope.row.method)">
                  {{ scope.row.method }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="url" label="请求URL" />
            <el-table-column prop="created_at" label="创建时间">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280">
              <template #default="scope">
                <el-button size="small" @click="editTestCase(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteTestCase(scope.row)">删除</el-button>
                <el-button size="small" type="success" @click="runSingleTest(scope.row)">运行</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="action-bar">
            <el-button @click="runSelectedTests" :disabled="selectedCases.length === 0">
              运行选中用例
            </el-button>
          </div>
        </el-tab-pane>

        <!-- 测试工具 -->
        <el-tab-pane label="测试工具" name="tester">
          <div class="tester-container">
            <div class="tester-header">
              <h3>API测试工具</h3>
              <div class="header-actions">
                <el-button @click="saveRequest" type="secondary">保存请求</el-button>
                <el-button @click="clearAll" type="default">清空</el-button>
              </div>
            </div>

            <div class="tester-body">
              <!-- 请求配置区域 -->
              <div class="request-section">
                <div class="request-config">
                  <div class="config-row">
                    <div class="method-selector">
                      <el-select v-model="currentRequest.method" class="form-select">
                        <el-option value="GET">GET</el-option>
                        <el-option value="POST">POST</el-option>
                        <el-option value="PUT">PUT</el-option>
                        <el-option value="DELETE">DELETE</el-option>
                      </el-select>
                    </div>
                    <div class="url-input">
                      <el-input
                        v-model="currentRequest.url"
                        placeholder="输入 API URL"
                        class="form-input"
                      />
                    </div>
                    <div class="send-button">
                      <el-button
                        @click="sendRequest"
                        :loading="isLoading"
                        :disabled="!canSend"
                        type="primary"
                      >
                        发送请求
                      </el-button>
                    </div>
                  </div>

                  <!-- 请求参数标签页 -->
                  <div class="tabs">
                    <button
                      v-for="tab in requestTabs"
                      :key="tab.key"
                      @click="activeRequestTab = tab.key"
                      :class="{ active: activeRequestTab === tab.key }"
                      class="tab-btn"
                    >
                      {{ tab.name }}
                    </button>
                  </div>

                  <!-- 参数内容 -->
                  <div class="tab-content">
                    <!-- Headers -->
                    <div v-if="activeRequestTab === 'headers'" class="key-value-pairs">
                      <div
                        v-for="(header, index) in currentRequest.headers"
                        :key="index"
                        class="key-value-row"
                      >
                        <el-input
                          v-model="header.key"
                          placeholder="Header 名称"
                          class="form-input"
                        />
                        <el-input
                          v-model="header.value"
                          placeholder="Header 值"
                          class="form-input"
                        />
                        <el-button
                          @click="removeHeader(index)"
                          type="danger"
                          size="small"
                        >
                          删除
                        </el-button>
                      </div>
                      <el-button @click="addHeader" type="primary" size="small">
                        添加 Header
                      </el-button>
                    </div>

                    <!-- Query Parameters -->
                    <div v-if="activeRequestTab === 'params'" class="key-value-pairs">
                      <div
                        v-for="(param, index) in currentRequest.params"
                        :key="index"
                        class="key-value-row"
                      >
                        <el-input
                          v-model="param.key"
                          placeholder="参数名"
                          class="form-input"
                        />
                        <el-input
                          v-model="param.value"
                          placeholder="参数值"
                          class="form-input"
                        />
                        <el-button
                          @click="removeParam(index)"
                          type="danger"
                          size="small"
                        >
                          删除
                        </el-button>
                      </div>
                      <el-button @click="addParam" type="primary" size="small">
                        添加参数
                      </el-button>
                    </div>

                    <!-- Body -->
                    <div v-if="activeRequestTab === 'body'" class="body-editor">
                      <div class="body-type-selector">
                        <el-select v-model="currentRequest.bodyType" class="form-select">
                          <el-option value="json">JSON</el-option>
                          <el-option value="form-data">Form Data</el-option>
                          <el-option value="raw">Raw Text</el-option>
                        </el-select>
                      </div>

                      <div v-if="currentRequest.bodyType === 'json'" class="json-editor">
                        <el-input
                          v-model="currentRequest.body"
                          placeholder='输入 JSON 数据，例如: {"key": "value"}'
                          type="textarea"
                          rows="8"
                        />
                      </div>

                      <div v-if="currentRequest.bodyType === 'form-data'" class="key-value-pairs">
                        <div
                          v-for="(field, index) in currentRequest.formData"
                          :key="index"
                          class="key-value-row"
                        >
                          <el-input
                            v-model="field.key"
                            placeholder="字段名"
                            class="form-input"
                          />
                          <el-input
                            v-model="field.value"
                            placeholder="字段值"
                            class="form-input"
                          />
                          <el-button
                            @click="removeFormData(index)"
                            type="danger"
                            size="small"
                          >
                            删除
                          </el-button>
                        </div>
                        <el-button @click="addFormData" type="primary" size="small">
                          添加字段
                        </el-button>
                      </div>

                      <div v-if="currentRequest.bodyType === 'raw'" class="raw-editor">
                        <el-input
                          v-model="currentRequest.rawBody"
                          placeholder="输入原始文本数据"
                          type="textarea"
                          rows="8"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 响应区域 -->
              <div class="response-section">
                <div class="response-header">
                  <h3>响应</h3>
                  <div class="response-info">
                    <span v-if="response.status" class="status-code" :class="statusCodeClass">
                      状态码: {{ response.status }}
                    </span>
                    <span v-if="response.duration" class="response-time">
                      响应时间: {{ response.duration }}ms
                    </span>
                  </div>
                </div>

                <div class="response-tabs">
                  <button
                    v-for="tab in responseTabs"
                    :key="tab.key"
                    @click="activeResponseTab = tab.key"
                    :class="{ active: activeResponseTab === tab.key }"
                    class="tab-btn"
                  >
                    {{ tab.name }}
                  </button>
                </div>

                <div class="response-content">
                  <!-- 响应体 -->
                  <div v-if="activeResponseTab === 'body'" class="response-body">
                    <pre v-if="response.data" class="response-data">{{ formattedResponse }}</pre>
                    <div v-else class="no-response">
                      {{
                        response.error
                          ? `错误: ${response.error}`
                          : '点击发送请求获取响应数据'
                      }}
                    </div>
                  </div>

                  <!-- 响应头 -->
                  <div v-if="activeResponseTab === 'headers'" class="response-headers">
                    <div
                      v-for="(value, key) in response.headers"
                      :key="key"
                      class="header-item"
                    >
                      <span class="header-key">{{ key }}:</span>
                      <span class="header-value">{{ value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 测试报告 -->
        <el-tab-pane label="测试报告" name="reports">
          <el-table :data="testReports" ref="reportsTable">
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
      </el-tabs>
    </el-card>

    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button @click="$router.push('/projects')">返回项目</el-button>
    </div>

    <!-- 创建/编辑测试用例对话框 -->
    <el-dialog
      :title="isEditing ? '编辑API测试用例' : '创建API测试用例'"
      v-model="showCreateDialog"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="testCaseForm"
        :rules="testCaseRules"
        ref="testCaseFormRef"
        label-width="100px"
      >
        <el-form-item label="用例名称：" prop="case_name">
          <el-input v-model="testCaseForm.case_name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="请求方法：" prop="method">
          <el-select v-model="testCaseForm.method" placeholder="请选择请求方法">
            <el-option value="GET">GET</el-option>
            <el-option value="POST">POST</el-option>
            <el-option value="PUT">PUT</el-option>
            <el-option value="DELETE">DELETE</el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="请求URL：" prop="url">
          <el-input v-model="testCaseForm.url" placeholder="请输入请求URL" />
        </el-form-item>
        <!-- 可根据需要添加更多表单项 -->
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleTestCaseSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import apiTestsAPI from '../api/apiTests'

// 项目ID
const route = useRoute()
const router = useRouter()
const projectId = ref(route.query.projectId || 1)

// 标签页状态
const activeTab = ref('tester')
const loading = ref(false)
const showCreateDialog = ref(false)
const isEditing = ref(false)
const editingTestCaseId = ref(null)
const selectedCases = ref([])
const pollingInterval = ref(null)

// 表单引用
const testCaseFormRef = ref(null)
const casesTable = ref(null)
const reportsTable = ref(null)

// 测试用例数据
const apiTestCases = ref([])
const testReports = ref([])

// 请求相关状态
const currentRequest = reactive({
  method: 'GET',
  url: '',
  headers: [{ key: 'Content-Type', value: 'application/json' }],
  params: [{ key: '', value: '' }],
  body: '{}',
  bodyType: 'json',
  formData: [{ key: '', value: '' }],
  rawBody: ''
})

// 响应状态
const response = reactive({
  status: null,
  data: null,
  headers: {},
  duration: null,
  error: null
})

// UI状态
const isLoading = ref(false)
const activeRequestTab = ref('headers')
const activeResponseTab = ref('body')

// 用例表单数据
const testCaseForm = reactive({
  case_name: '',
  method: 'GET',
  url: '',
  headers: [],
  params: [],
  body: ''
})

// 表单验证规则
const testCaseRules = {
  case_name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' },
    { min: 2, max: 50, message: '用例名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  url: [
    { required: true, message: '请输入请求URL', trigger: 'blur' },
    {
      pattern: /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i,
      message: '请输入有效的URL',
      trigger: 'blur'
    }
  ]
}

// 标签页配置
const requestTabs = [
  { key: 'headers', name: '请求头' },
  { key: 'params', name: '查询参数' },
  { key: 'body', name: '请求体' }
]

const responseTabs = [
  { key: 'body', name: '响应体' },
  { key: 'headers', name: '响应头' }
]

// 计算属性
const canSend = computed(() => {
  return currentRequest.url.trim() !== '' && !isLoading.value
})

const statusCodeClass = computed(() => {
  if (!response.status) return ''
  if (response.status < 300) return 'status-success'
  if (response.status < 400) return 'status-warning'
  return 'status-error'
})

const formattedResponse = computed(() => {
  if (!response.data) return ''
  try {
    return JSON.stringify(response.data, null, 2)
  } catch {
    return response.data
  }
})

// 工具方法
const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch {
    return dateString
  }
}

const getMethodType = (method) => {
  const types = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger'
  }
  return types[method] || 'default'
}

const getStatusType = (status) => {
  const types = {
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'info'
  }
  return types[status] || 'info'
}

// 请求处理方法
const addHeader = () => {
  currentRequest.headers.push({ key: '', value: '' })
}

const removeHeader = (index) => {
  currentRequest.headers.splice(index, 1)
}

const addParam = () => {
  currentRequest.params.push({ key: '', value: '' })
}

const removeParam = (index) => {
  currentRequest.params.splice(index, 1)
}

const addFormData = () => {
  currentRequest.formData.push({ key: '', value: '' })
}

const removeFormData = (index) => {
  currentRequest.formData.splice(index, 1)
}

const sendRequest = async () => {
  if (!canSend.value) return

  isLoading.value = true
  response.error = null
  const startTime = Date.now()

  try {
    // 实际项目中替换为真实的请求逻辑
    // 这里仅作示例
    setTimeout(() => {
      response.status = 200
      response.data = { success: true, message: '模拟响应数据' }
      response.headers = { 'Content-Type': 'application/json' }
      response.duration = Date.now() - startTime
      isLoading.value = false
    }, 1000)
  } catch (error) {
    response.error = error.message || '请求失败'
    response.status = null
    response.data = null
    isLoading.value = false
  }
}

const saveRequest = () => {
  // 将当前请求保存为测试用例
  testCaseForm.case_name = `API测试_${new Date().getTime()}`
  testCaseForm.method = currentRequest.method
  testCaseForm.url = currentRequest.url
  testCaseForm.headers = currentRequest.headers
  testCaseForm.params = currentRequest.params
  testCaseForm.body = currentRequest.body

  isEditing.value = false
  editingTestCaseId.value = null
  showCreateDialog.value = true
}

const clearAll = () => {
  ElMessageBox.confirm(
    '确定要清空所有请求配置吗？',
    '确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    Object.assign(currentRequest, {
      method: 'GET',
      url: '',
      headers: [{ key: 'Content-Type', value: 'application/json' }],
      params: [{ key: '', value: '' }],
      body: '{}',
      bodyType: 'json',
      formData: [{ key: '', value: '' }],
      rawBody: ''
    })

    Object.assign(response, {
      status: null,
      data: null,
      headers: {},
      duration: null,
      error: null
    })
  })
}

// 测试用例方法
const fetchApiTestCases = async () => {
  loading.value = true
  try {
    const response = await apiTestsAPI.getApiTestCases(projectId.value)
    apiTestsAPI.value = response.data
  } catch (error) {
    ElMessage.error('获取测试用例失败')
  } finally {
    loading.value = false
  }
}

const fetchTestReports = async () => {
  try {
    const response = await apiTestsAPI.getApiTestReports(projectId.value)
    testReports.value = response.data
  } catch (error) {
    ElMessage.error('获取测试报告失败')
  }
}

const handleSelectionChange = (val) => {
  selectedCases.value = val
}

const editTestCase = (testCase) => {
  isEditing.value = true
  editingTestCaseId.value = testCase.id
  Object.assign(testCaseForm, {
    case_name: testCase.case_name,
    method: testCase.method,
    url: testCase.url,
    headers: testCase.headers || [],
    params: testCase.params || [],
    body: testCase.body || ''
  })
  showCreateDialog.value = true
}

const deleteTestCase = async (testCase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例 "${testCase.case_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await apiTestsAPI.deleteApiTestCase(testCase.id)
    ElMessage.success('测试用例删除成功')
    fetchApiTestCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除测试用例失败')
    }
  }
}

const runSingleTest = async (testCase) => {
  try {
    await apiTestsAPI.runApiTest(projectId.value, [testCase.id])
    ElMessage.success('测试已开始运行')
    startPollingReports()
  } catch (error) {
    ElMessage.error('运行测试失败')
  }
}

const runSelectedTests = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请选择要运行的测试用例')
    return
  }

  try {
    const caseIds = selectedCases.value.map(item => item.id)
    await apiTestsAPI.runApiTest(projectId.value, caseIds)
    ElMessage.success('测试已开始运行')
    startPollingReports()
  } catch (error) {
    ElMessage.error('运行测试失败')
  }
}

const viewReport = (report) => {
  // 打开报告详情
  window.open(`/reports/${report.id}`, '_blank')
}

const handleTestCaseSubmit = async () => {
  if (!testCaseFormRef.value) return

  try {
    await testCaseFormRef.value.validate()

    if (isEditing.value) {
      await apiTestsAPI.updateApiTestCase(editingTestCaseId.value, testCaseForm)
      ElMessage.success('测试用例更新成功')
    } else {
      await apiTestsAPI.createApiTestCase(projectId.value, testCaseForm)
      ElMessage.success('测试用例创建成功')
    }

    showCreateDialog.value = false
    fetchApiTestCases()
  } catch (error) {
    // 验证失败不提示错误
    if (error.name !== 'ValidationError') {
      ElMessage.error('操作失败')
    }
  }
}

// 报告轮询
const startPollingReports = () => {
  // 清除已有轮询
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }

  // 开始新轮询
  pollingInterval.value = setInterval(() => {
    fetchTestReports()
  }, 5000)
}

// 本地存储相关
const loadFromLocalStorage = () => {
  const saved = localStorage.getItem('apiTesterHistory')
  if (saved) {
    try {
      // 可以在这里加载历史记录
    } catch (error) {
      console.error('加载本地存储失败:', error)
    }
  }
}

// 生命周期
onMounted(() => {
  loadFromLocalStorage()
  fetchApiTestCases()
  fetchTestReports()
})

// 组件卸载时清理
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
})
</script>

<style scoped>
.api-test-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
}

.tester-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-top: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.action-bar {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.back-button {
  margin-top: 20px;
  text-align: center;
  padding: 20px 0;
}

.tester-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.tester-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  padding: 20px;
  min-height: 600px;
}

.request-section, .response-section {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  overflow: hidden;
}

.config-row {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.method-selector {
  width: 120px;
}

.url-input {
  flex: 1;
}

.send-button {
  width: 120px;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e9ecef;
}

.tab-btn {
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.tab-btn.active {
  border-bottom-color: #409eff;
  color: #409eff;
}

.tab-content {
  padding: 15px;
}

.key-value-pairs {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.key-value-row {
  display: flex;
  gap: 10px;
}

.key-value-row .form-input {
  flex: 1;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #e9ecef;
}

.response-data {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
  padding: 15px;
  margin: 0;
  background: #f8f9fa;
  border-radius: 4px;
}

.no-response {
  padding: 15px;
  color: #666;
  text-align: center;
}

.status-success {
  color: #10b981;
}

.status-warning {
  color: #f59e0b;
}

.status-error {
  color: #ef4444;
}

@media (max-width: 1200px) {
  .api-test-container {
    padding: 15px;
  }
}

@media (max-width: 768px) {
  .tester-body {
    grid-template-columns: 1fr;
  }

  .config-row {
    flex-direction: column;
  }

  .method-selector, .send-button {
    width: 100%;
  }
}
</style>