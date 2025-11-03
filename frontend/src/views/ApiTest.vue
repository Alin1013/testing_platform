<template>
  <div class="api-tester">
    <!-- 添加返回按钮到顶部 -->
    <div class="page-header">
      <el-button @click="$router.push('/projects')" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回项目
      </el-button>
      <h2 class="page-title">API 测试工具</h2>
      <div style="width: 120px"></div>
    </div>
    <div class="tester-header">
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
        :project-id="projectId"
        @refresh="loadTestCases"
        @select="loadTestCase"
        @delete="deleteTestCase"
        @add="addTestCase"
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import { apiTestsAPI } from '../api/apiTests'
import { ArrowLeft } from '@element-plus/icons-vue'

// 组件导入
import TestCaseList from '../components/api-test/TestCaseList.vue'
import RequestEditor from '../components/api-test/RequestEditor.vue'
import ResponseViewer from '../components/api-test/ResponseViewer.vue'
import TestCaseSaveDialog from '../components/api-test/TestCaseSaveDialog.vue'
import BusinessFlowDialog from '../components/api-test/BusinessFlowDialog.vue'
import TestRunner from '../components/api-test/TestRunner.vue'

const route = useRoute()

// 响应式数据
const testCases = ref([])
const selectedTestCase = ref(null)
const isLoading = ref(false)
const showSaveDialog = ref(false)
const showBusinessFlowDialog = ref(false)
const activeRequestTab = ref('headers')
const activeResponseTab = ref('body')

const currentRequest = reactive({
  method: 'GET',
  url: '',
  headers: [{ key: '', value: '' }],
  params: [{ key: '', value: '' }],
  bodyType: 'json',
  body: '',
  formData: [{ key: '', value: '' }],
  rawBody: '',
  expected_data: ''
})

const response = reactive({
  status: null,
  duration: null,
  data: null,
  headers: null,
  error: null
})

// 计算属性
const projectId = computed(() => {
  const id = route.params.projectId || 1
  return typeof id === 'string' ? parseInt(id, 10) : id
})

const canSend = computed(() => {
  return currentRequest.url && currentRequest.url.trim() !== ''
})

// 方法
const updateActiveRequestTab = (tab) => {
  activeRequestTab.value = tab
}

const updateActiveResponseTab = (tab) => {
  activeResponseTab.value = tab
}

// 加载测试用例列表
const loadTestCases = async () => {
  try {
    const result = await apiTestsAPI.getApiTestCases(projectId.value)
    testCases.value = result.data || []
    console.log('加载测试用例成功:', testCases.value)
  } catch (error) {
    console.error('加载测试用例失败:', error)
    ElMessage.error('加载测试用例失败: ' + error.message)
  }
}

// 加载单个测试用例
const loadTestCase = (testCase) => {
  selectedTestCase.value = testCase
  console.log('加载测试用例:', testCase)
// 重置当前请求
  Object.assign(currentRequest, {
    method: testCase.method || 'GET',
    url: testCase.url || '',
    headers: testCase.headers ? convertObjectToArray(testCase.headers) : [{ key: '', value: '' }],
    params: testCase.params ? convertObjectToArray(testCase.params) : [{ key: '', value: '' }],
    bodyType: testCase.body_type || 'json',
    body: testCase.body || '',
    formData: testCase.form_data ? convertObjectToArray(testCase.form_data) : [{ key: '', value: '' }],
    rawBody: testCase.raw_body || '',
    expected_data: testCase.expected_data || ''
  })

  console.log('填充后的当前请求:', currentRequest)
}

// 辅助函数：将对象转换为数组格式
const convertObjectToArray = (obj) => {
  if (Array.isArray(obj)) {
    return obj.length > 0 ? obj : [{ key: '', value: '' }]
  }

  if (obj && typeof obj === 'object') {
    const array = Object.keys(obj).map(key => ({
      key: key,
      value: obj[key]
    }))
    return array.length > 0 ? array : [{ key: '', value: '' }]
  }

  return [{ key: '', value: '' }]
}

// 添加测试用例
const addTestCase = async (testCaseData) => {
  try {
    // 构建完整的测试用例数据
    const fullTestCaseData = {
      ...testCaseData,
      project_id: projectId.value,
      headers: currentRequest.headers.filter(h => h.key && h.value),
      params: currentRequest.params.filter(p => p.key && p.value),
      body_type: currentRequest.bodyType,
      body: currentRequest.body,
      form_data: currentRequest.formData.filter(f => f.key && f.value),
      raw_body: currentRequest.rawBody,
      expected_data: currentRequest.expected_data,
      case_name:testCaseData.case_name || `测试用例_${Date.now()}`
    }

    await apiTestsAPI.createApiTestCase(projectId.value, fullTestCaseData)
    ElMessage.success('测试用例添加成功')
    await loadTestCases()
  } catch (error) {
    ElMessage.error('添加测试用例失败: ' + error.message)
  }
}

// 删除测试用例
const deleteTestCase = async (testCaseId) => {
  try {
    // 使用更安全的方式显示确认对话框
    const confirmResult = await new Promise((resolve) => {
      ElMessageBox.confirm(
        '确定删除这个测试用例吗？',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
        .then(() => resolve(true))
        .catch(() => resolve(false))
    })

    if (!confirmResult) {
      return // 用户取消删除
    }

    console.log('开始删除测试用例:', testCaseId, '项目ID:', projectId.value)

    // 调用删除 API
    await apiTestsAPI.deleteApiTestCase(projectId.value, testCaseId)

    ElMessage.success('删除成功')

    // 重新加载测试用例列表
    await loadTestCases()

    // 如果删除的是当前选中的测试用例，清空选中状态
    if (selectedTestCase.value?.id === testCaseId) {
      selectedTestCase.value = null
      clearAll()
    }
  } catch (error) {
    console.error('删除测试用例错误:', error)
    // 更详细的错误处理
    if (error?.response?.status === 404) {
      ElMessage.error('测试用例不存在或已被删除')
    } else if (error?.response?.status === 403) {
      ElMessage.error('没有权限删除此测试用例')
    } else if (error?.message?.includes('cancel')) {
      // 用户取消操作，不显示错误
      return
    } else {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

// 发送请求
const handleSendRequest = async () => {
  if (!canSend.value) return

  isLoading.value = true
  // 重置响应数据
  Object.assign(response, {
    status: null,
    duration: null,
    data: null,
    headers: null,
    error: null
  })

  try {
    const startTime = Date.now()

    // 构建请求数据
    const requestData = {
      method: currentRequest.method,
      url: currentRequest.url,
      headers: {},
      params: {},
      data: null
    }

    // 处理 headers
    currentRequest.headers.forEach(header => {
      if (header.key && header.value) {
        requestData.headers[header.key] = header.value
      }
    })

    // 处理 params
    currentRequest.params.forEach(param => {
      if (param.key && param.value) {
        requestData.params[param.key] = param.value
      }
    })

    // 处理请求体
    if (currentRequest.bodyType === 'json' && currentRequest.body) {
      try {
        requestData.data = JSON.parse(currentRequest.body)
      } catch (e) {
        throw new Error('JSON格式错误')
      }
    } else if (currentRequest.bodyType === 'form-data') {
      const formData = new FormData()
      currentRequest.formData.forEach(field => {
        if (field.key && field.value) {
          formData.append(field.key, field.value)
        }
      })
      requestData.data = formData
    } else if (currentRequest.bodyType === 'raw' && currentRequest.rawBody) {
      requestData.data = currentRequest.rawBody
    }

    // 发送请求
    const result = await apiTestsAPI.sendApiRequest(requestData)
    const duration = Date.now() - startTime

    Object.assign(response, {
      status: result.status || 200,
      duration: duration,
      data: result.data,
      headers: result.headers || {},
      error: null
    })

    ElMessage.success('请求发送成功')
  } catch (error) {
    Object.assign(response, {
      status: null,
      duration: null,
      data: null,
      headers: null,
      error: error.message
    })
    ElMessage.error('请求发送失败: ' + error.message)
  } finally {
    isLoading.value = false
  }
}

// 清空所有数据
const clearAll = () => {
  Object.assign(currentRequest, {
    method: 'GET',
    url: '',
    headers: [{ key: '', value: '' }],
    params: [{ key: '', value: '' }],
    bodyType: 'json',
    body: '',
    formData: [{ key: '', value: '' }],
    rawBody: '',
    expected_data: ''
  })

  Object.assign(response, {
    status: null,
    duration: null,
    data: null,
    headers: null,
    error: null
  })

  selectedTestCase.value = null
  activeRequestTab.value = 'headers'
  activeResponseTab.value = 'body'
}

// 请求编辑器相关方法
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

// 事件处理
const handleTestCaseSaved = () => {
  loadTestCases()
  ElMessage.success('测试用例保存成功')
}

const handleBusinessFlowCreated = () => {
  ElMessage.success('业务流程创建成功')
}

const handleTestCompleted = () => {
  ElMessage.success('测试执行完成，请查看测试报告')
}

// 监听项目ID变化
watch(projectId, (newProjectId) => {
  if (newProjectId) {
    loadTestCases()
  }
})

// 生命周期
onMounted(() => {
  loadTestCases()
})
</script>

<style scoped>
.api-tester {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 新增页面头部样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #e6e8eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
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

.tester-header {
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #e6e8eb;
}

.tester-body {
  flex: 1;
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.request-editor {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

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

  .tester-body {
    grid-template-columns: 1fr;
  }

  .header-actions {
    justify-content: center;
  }
}
</style>