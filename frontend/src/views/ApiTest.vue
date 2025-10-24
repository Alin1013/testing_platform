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
        <!-- 单元测试 -->
        <el-tab-pane label="单元测试" name="unit">
          <el-table :data="apiTestCases" v-loading="loading" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="case_name" label="用例名称" />
            <el-table-column prop="method" label="请求方法" />
            <el-table-column prop="url" label="请求URL" />
            <el-table-column prop="created_at" label="创建时间">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="240">
              <template #default="scope">
                <el-button size="small" @click="editTestCase(scope.row)">编辑</el-button>
                <el-button size="small" @click="runTestCase(scope.row)">运行</el-button>
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

        <!-- 测试工具 -->
        <el-tab-pane label="测试工具" name="tester">
          <div class="api-tester">
            <div class="tester-header">
              <h3>API测试工具</h3>
              <div class="header-actions">
                <button @click="saveAsTestCase" class="btn btn-secondary">保存为用例</button>
                <button @click="clearAllTester" class="btn btn-outline">清空</button>
              </div>
            </div>

            <div class="tester-body">
              <!-- 请求配置区域 -->
              <div class="request-section">
                <div class="request-config">
                  <div class="config-row">
                    <div class="method-selector">
                      <select v-model="currentRequest.method" class="form-select">
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="PUT">PUT</option>
                        <option value="DELETE">DELETE</option>
                      </select>
                    </div>
                    <div class="url-input">
                      <input
                        v-model="currentRequest.url"
                        type="text"
                        placeholder="输入 API URL"
                        class="form-input"
                      />
                    </div>
                    <div class="send-button">
                      <button
                        @click="sendRequest"
                        :disabled="!canSend"
                        class="btn btn-primary"
                      >
                        {{ isLoading ? '发送中...' : '发送请求' }}
                      </button>
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
                        <input
                          v-model="header.key"
                          placeholder="Header 名称"
                          class="form-input"
                        />
                        <input
                          v-model="header.value"
                          placeholder="Header 值"
                          class="form-input"
                        />
                        <button
                          @click="removeHeader(index)"
                          class="btn btn-danger"
                        >
                          删除
                        </button>
                      </div>
                      <button @click="addHeader" class="btn btn-outline">
                        添加 Header
                      </button>
                    </div>

                    <!-- Query Parameters -->
                    <div v-if="activeRequestTab === 'params'" class="key-value-pairs">
                      <div
                        v-for="(param, index) in currentRequest.params"
                        :key="index"
                        class="key-value-row"
                      >
                        <input
                          v-model="param.key"
                          placeholder="参数名"
                          class="form-input"
                        />
                        <input
                          v-model="param.value"
                          placeholder="参数值"
                          class="form-input"
                        />
                        <button
                          @click="removeParam(index)"
                          class="btn btn-danger"
                        >
                          删除
                        </button>
                      </div>
                      <button @click="addParam" class="btn btn-outline">
                        添加参数
                      </button>
                    </div>

                    <!-- Body -->
                    <div v-if="activeRequestTab === 'body'" class="body-editor">
                      <div class="body-type-selector">
                        <select v-model="currentRequest.bodyType" class="form-select">
                          <option value="json">JSON</option>
                          <option value="form-data">Form Data</option>
                          <option value="raw">Raw Text</option>
                        </select>
                      </div>

                      <div v-if="currentRequest.bodyType === 'json'" class="json-editor">
                        <textarea
                          v-model="currentRequest.body"
                          placeholder='输入 JSON 数据，例如: {"key": "value"}'
                          class="form-textarea"
                          rows="8"
                        ></textarea>
                      </div>

                      <div v-if="currentRequest.bodyType === 'form-data'" class="key-value-pairs">
                        <div
                          v-for="(field, index) in currentRequest.formData"
                          :key="index"
                          class="key-value-row"
                        >
                          <input
                            v-model="field.key"
                            placeholder="字段名"
                            class="form-input"
                          />
                          <input
                            v-model="field.value"
                            placeholder="字段值"
                            class="form-input"
                          />
                          <button
                            @click="removeFormData(index)"
                            class="btn btn-danger"
                          >
                            删除
                          </button>
                        </div>
                        <button @click="addFormData" class="btn btn-outline">
                          添加字段
                        </button>
                      </div>

                      <div v-if="currentRequest.bodyType === 'raw'" class="raw-editor">
                        <textarea
                          v-model="currentRequest.rawBody"
                          placeholder="输入原始文本数据"
                          class="form-textarea"
                          rows="8"
                        ></textarea>
                      </div>
                    </div>

                    <!-- 预期结果 -->
                    <div v-if="activeRequestTab === 'expect'" class="expect-editor">
                      <textarea
                        v-model="currentRequest.expect"
                        placeholder='输入预期结果，例如: {"status": 200}'
                        class="form-textarea"
                        rows="8"
                      ></textarea>
                      <div class="expect-hint">
                        <p>支持JSON格式验证，如状态码、响应字段等</p>
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
                    <span v-if="response.testResult" class="test-result" :class="testResultClass">
                      测试结果: {{ response.testResult }}
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

                  <!-- 测试结果 -->
                  <div v-if="activeResponseTab === 'testResult'" class="test-result-content">
                    <div v-if="response.testDetails && response.testDetails.length">
                      <div v-for="(detail, index) in response.testDetails" :key="index" class="test-detail-item">
                        <span :class="detail.passed ? 'test-passed' : 'test-failed'">
                          {{ detail.passed ? '✓' : '✗' }} {{ detail.message }}
                        </span>
                      </div>
                    </div>
                    <div v-else class="no-test-result">
                      暂无测试结果
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 测试报告 -->
        <el-tab-pane label="测试报告" name="reports">
          <el-table :data="testReports">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="report_name" label="报告名称" />
            <el-table-column prop="type" label="测试类型">
              <template #default="scope">
                {{ scope.row.type === 'unit' ? '单元测试' : '业务测试' }}
              </template>
            </el-table-column>
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
    >
      <el-form :model="testCaseForm" :rules="testCaseRules" ref="testCaseFormRef" label-width="100px">
        <el-form-item label="用例名称：" prop="case_name">
          <el-input v-model="testCaseForm.case_name" placeholder="请输入用例名称" />
        </el-form-item>

        <el-form-item label="请求方法：" prop="method">
          <el-select v-model="testCaseForm.method" placeholder="请选择请求方法">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>

        <el-form-item label="请求URL：" prop="url">
          <el-input v-model="testCaseForm.url" placeholder="请输入URL" />
        </el-form-item>

        <el-form-item label="请求头：">
          <el-button type="text" @click="showHeadersDialog = true">编辑请求头</el-button>
        </el-form-item>

        <el-form-item label="查询参数：">
          <el-button type="text" @click="showParamsDialog = true">编辑查询参数</el-button>
        </el-form-item>

        <el-form-item label="请求体类型：" prop="bodyType">
          <el-select v-model="testCaseForm.bodyType" placeholder="请选择请求体类型">
            <el-option label="JSON" value="json" />
            <el-option label="Form Data" value="form-data" />
            <el-option label="Raw Text" value="raw" />
          </el-select>
        </el-form-item>

        <el-form-item label="请求体：" prop="body" v-if="testCaseForm.bodyType === 'json'">
          <el-input
            type="textarea"
            v-model="testCaseForm.body"
            placeholder='{"key": "value"}'
            rows="4"
          />
        </el-form-item>

        <el-form-item label="Form Data：" v-if="testCaseForm.bodyType === 'form-data'">
          <el-button type="text" @click="showFormDataDialog = true">编辑Form Data</el-button>
        </el-form-item>

        <el-form-item label="原始文本：" prop="rawBody" v-if="testCaseForm.bodyType === 'raw'">
          <el-input
            type="textarea"
            v-model="testCaseForm.rawBody"
            placeholder="输入原始文本"
            rows="4"
          />
        </el-form-item>

        <el-form-item label="预期结果：" prop="expect">
          <el-input
            type="textarea"
            v-model="testCaseForm.expect"
            placeholder='{"status": 200, "data.key": "value"}'
            rows="4"
          />
          <div class="form-hint">支持JSON格式，可验证状态码和响应字段</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleTestCaseSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 创建业务流程对话框 -->
    <el-dialog
      title="创建业务流程"
      v-model="showBusinessFlowDialog"
      width="600px"
    >
      <el-form :model="businessFlowForm" :rules="businessFlowRules" ref="businessFlowFormRef" label-width="100px">
        <el-form-item label="流程名称：" prop="flow_name">
          <el-input v-model="businessFlowForm.flow_name" placeholder="请输入流程名称" />
        </el-form-item>
        <el-form-item label="选择用例：" prop="case_ids">
          <el-select
            v-model="businessFlowForm.case_ids"
            multiple
            placeholder="请选择测试用例"
            style="width: 100%"
          >
            <el-option
              v-for="testcase in apiTestCases"
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

    <!-- 请求头编辑对话框 -->
    <el-dialog title="编辑请求头" v-model="showHeadersDialog" width="500px">
      <div class="key-value-pairs">
        <div
          v-for="(header, index) in editingHeaders"
          :key="index"
          class="key-value-row"
        >
          <el-input
            v-model="header.key"
            placeholder="Header名称"
            style="flex: 1"
          />
          <el-input
            v-model="header.value"
            placeholder="Header值"
            style="flex: 1"
          />
          <el-button
            @click="removeHeader(index, true)"
            type="danger"
            size="small"
          >
            删除
          </el-button>
        </div>
        <el-button @click="addHeader(true)" type="primary" size="small">
          添加Header
        </el-button>
      </div>
      <template #footer>
        <el-button @click="showHeadersDialog = false">确定</el-button>
      </template>
    </el-dialog>

    <!-- 其他编辑对话框（参数、FormData）结构类似，省略 -->
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElDialog, ElForm } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { apiTestsAPI } from '../api/apiTests'

// 路由和项目信息
const route = useRoute()
const router = useRouter()
const projectId = ref(route.query.projectId || 1)

// 标签页状态
const activeTab = ref('unit')
const loading = ref(false)

// 对话框状态
const showCreateDialog = ref(false)
const showBusinessFlowDialog = ref(false)
const showHeadersDialog = ref(false)
const showParamsDialog = ref(false)
const showFormDataDialog = ref(false)
const isEditing = ref(false)

// 表单引用
const testCaseFormRef = ref()
const businessFlowFormRef = ref()
const editingTestCaseId = ref(null)

// 数据存储
const apiTestCases = ref([])
const businessFlows = ref([])
const testReports = ref([])
const selectedCases = ref([])

// 测试工具状态
const response = reactive({
  status: null,
  data: null,
  headers: {},
  duration: null,
  error: null,
  testResult: null,
  testDetails: []
})

const currentRequest = reactive({
  method: 'GET',
  url: '',
  headers: [{ key: 'Content-Type', value: 'application/json' }],
  params: [{ key: '', value: '' }],
  body: '{}',
  bodyType: 'json',
  formData: [{ key: '', value: '' }],
  rawBody: '',
  expect: '{"status": 200}'
})

// 编辑用例时的临时存储
const editingHeaders = ref([])
const editingParams = ref([])
const editingFormData = ref([])

// UI状态
const isLoadingTester = ref(false)
const activeRequestTab = ref('headers')
const activeResponseTab = ref('body')

// 表单数据
const testCaseForm = reactive({
  case_name: '',
  method: 'GET',
  url: '',
  headers: [{ key: 'Content-Type', value: 'application/json' }],
  params: [{ key: '', value: '' }],
  body: '{}',
  bodyType: 'json',
  formData: [{ key: '', value: '' }],
  rawBody: '',
  expect: '{"status": 200}'
})

const businessFlowForm = reactive({
  flow_name: '',
  case_ids: []
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
    { required: true, message: '请输入URL', trigger: 'blur' },
    {
      pattern: /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i,
      message: '请输入有效的URL',
      trigger: 'blur'
    }
  ],
  expect: [
    { required: true, message: '请输入预期结果', trigger: 'blur' }
  ]
}

const businessFlowRules = {
  flow_name: [
    { required: true, message: '请输入流程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '流程名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  case_ids: [
    {
      required: true,
      type: 'array',
      min: 1,
      message: '请至少选择一个测试用例',
      trigger: 'change'
    }
  ]
}

// 标签页配置
const requestTabs = [
  { key: 'headers', name: '请求头' },
  { key: 'params', name: '查询参数' },
  { key: 'body', name: '请求体' },
  { key: 'expect', name: '预期结果' }
]

const responseTabs = [
  { key: 'body', name: '响应体' },
  { key: 'headers', name: '响应头' },
  { key: 'testResult', name: '测试结果' }
]

// 计算属性
const canSend = computed(() => {
  return currentRequest.url.trim() !== '' && !isLoadingTester.value
})

const statusCodeClass = computed(() => {
  if (!response.status) return ''
  if (response.status < 300) return 'status-success'
  if (response.status < 400) return 'status-warning'
  return 'status-error'
})

const testResultClass = computed(() => {
  return response.testResult === '通过' ? 'status-success' : 'status-error'
})

const formattedResponse = computed(() => {
  if (!response.data) return ''
  try {
    return JSON.stringify(response.data, null, 2)
  } catch {
    return response.data
  }
})

// 工具函数
const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch {
    return dateString
  }
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

// 请求配置方法
const addHeader = (isEditing = false) => {
  if (isEditing) {
    editingHeaders.value.push({ key: '', value: '' })
  } else {
    currentRequest.headers.push({ key: '', value: '' })
  }
}

const removeHeader = (index, isEditing = false) => {
  if (isEditing) {
    editingHeaders.value.splice(index, 1)
  } else {
    currentRequest.headers.splice(index, 1)
  }
}

// 其他参数操作方法（addParam, removeParam等）省略

// 发送请求方法
const sendRequest = async () => {
  if (!canSend.value) return

  isLoadingTester.value = true
  response.error = null
  response.testResult = null
  response.testDetails = []

  try {
    const startTime = Date.now()

    // 构建请求配置（与原逻辑相同）
    const config = {
      method: currentRequest.method,
      headers: {}
    }

    currentRequest.headers.forEach(header => {
      if (header.key && header.value) {
        config.headers[header.key] = header.value
      }
    })

    let url = currentRequest.url
    const searchParams = new URLSearchParams()
    currentRequest.params.forEach(param => {
      if (param.key && param.value) {
        searchParams.append(param.key, param.value)
      }
    })

    const queryString = searchParams.toString()
    if (queryString) {
      url += (url.includes('?') ? '&' : '?') + queryString
    }

    // 处理请求体（与原逻辑相同）
    if (['POST', 'PUT'].includes(currentRequest.method)) {
      if (currentRequest.bodyType === 'json') {
        config.body = currentRequest.body
        config.headers['Content-Type'] = 'application/json'
      } else if (currentRequest.bodyType === 'form-data') {
        const formData = new FormData()
        currentRequest.formData.forEach(field => {
          if (field.key && field.value) {
            formData.append(field.key, field.value)
          }
        })
        config.body = formData
        delete config.headers['Content-Type']
      } else if (currentRequest.bodyType === 'raw') {
        config.body = currentRequest.rawBody
      }
    }

    // 发送请求
    const result = await fetch(url, config)

    // 处理响应（与原逻辑相同）
    response.duration = Date.now() - startTime
    response.status = result.status
    response.headers = {}

    result.headers.forEach((value, key) => {
      response.headers[key] = value
    })

    const contentType = result.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      response.data = await result.json()
    } else {
      response.data = await result.text()
    }

    // 验证预期结果
    validateExpectResult()

  } catch (error) {
    response.error = error.message
    response.data = null
    response.status = null
  } finally {
    isLoadingTester.value = false
  }
}

// 验证预期结果
const validateExpectResult = () => {
  try {
    const expect = JSON.parse(currentRequest.expect)
    const details = []
    let allPassed = true

    // 验证状态码
    if (expect.status !== undefined) {
      const passed = response.status === expect.status
      details.push({
        passed,
        message: `状态码验证: 预期 ${expect.status}, 实际 ${response.status}`
      })
      if (!passed) allPassed = false
    }

    // 验证响应字段（简单实现）
    Object.keys(expect).forEach(key => {
      if (key === 'status') return

      // 简单路径解析，如 data.key
      const value = getNestedValue(response.data, key)
      const passed = value === expect[key]

      details.push({
        passed,
        message: `字段验证 [${key}]: 预期 ${expect[key]}, 实际 ${value}`
      })

      if (!passed) allPassed = false
    })

    response.testDetails = details
    response.testResult = allPassed ? '通过' : '失败'
  } catch (error) {
    response.testResult = '验证失败'
    response.testDetails = [{
      passed: false,
      message: `预期结果格式错误: ${error.message}`
    }]
  }
}

// 获取嵌套对象属性
const getNestedValue = (obj, path) => {
  return path.split('.').reduce((acc, key) => {
    return acc && acc[key] !== undefined ? acc[key] : null
  }, obj)
}

// 用例管理方法
const fetchAPITestCases = async () => {
  loading.value = true
  try {
    const response = await apiTestsAPI.getApiTestCases(projectId.value)
    apiTestCases.value = response.data
  } catch (error) {
    ElMessage.error('获取API测试用例失败')
  } finally {
    loading.value = false
  }
}

// 其他用例管理方法（创建、编辑、删除、运行等）省略

// 保存为测试用例
const saveAsTestCase = () => {
  testCaseForm.case_name = `API测试_${new Date().getTime()}`
  testCaseForm.method = currentRequest.method
  testCaseForm.url = currentRequest.url
  testCaseForm.headers = JSON.parse(JSON.stringify(currentRequest.headers))
  testCaseForm.params = JSON.parse(JSON.stringify(currentRequest.params))
  testCaseForm.body = currentRequest.body
  testCaseForm.bodyType = currentRequest.bodyType
  testCaseForm.formData = JSON.parse(JSON.stringify(currentRequest.formData))
  testCaseForm.rawBody = currentRequest.rawBody
  testCaseForm.expect = currentRequest.expect

  isEditing.value = false
  editingTestCaseId.value = null
  showCreateDialog.value = true
}

// 清空测试工具
const clearAllTester = () => {
  if (confirm('确定要清空所有请求配置吗？')) {
    Object.assign(currentRequest, {
      method: 'GET',
      url: '',
      headers: [{ key: 'Content-Type', value: 'application/json' }],
      params: [{ key: '', value: '' }],
      body: '{}',
      bodyType: 'json',
      formData: [{ key: '', value: '' }],
      rawBody: '',
      expect: '{"status": 200}'
    })

    Object.assign(response, {
      status: null,
      data: null,
      headers: {},
      duration: null,
      error: null,
      testResult: null,
      testDetails: []
    })
  }
}

// 初始化
onMounted(() => {
  fetchAPITestCases()
  fetchBusinessFlows()
  fetchTestReports()
})
</script>

<style scoped>
/* 保留原有样式并添加新样式 */
.api-test-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
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

/* 测试工具样式复用原有样式并添加新样式 */
.expect-editor {
  margin-top: 10px;
}

.test-result {
  font-weight: bold;
}

.test-detail-item {
  margin-bottom: 8px;
  padding: 4px;
  border-radius: 4px;
}

.test-passed {
  color: #28a745;
}

.test-failed {
  color: #dc3545;
}

.form-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #6c757d;
}

.expect-hint {
  margin-top: 10px;
  font-size: 12px;
  color: #6c757d;
}
</style>