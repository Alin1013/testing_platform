import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { apiTestsAPI } from '@/api/apiTests'

export const useApiTestStore = defineStore('apiTest', () => {
  // 状态
  const testCases = ref([])
  const selectedTestCase = ref(null)
  const isLoading = ref(false)
  const isRunningTests = ref(false)

  // 当前请求配置
  const currentRequest = reactive({
    method: 'GET',
    url: '',
    headers: [{ key: 'Content-Type', value: 'application/json' }],
    params: [{ key: '', value: '' }],
    body: '{}',
    bodyType: 'json',
    formData: [{ key: '', value: '' }],
    rawBody: '',
    expected_data: '{}'
  })

  // 响应数据
  const response = reactive({
    status: null,
    data: null,
    headers: {},
    duration: null,
    error: null
  })

  // UI 状态
  const activeRequestTab = ref('headers')
  const activeResponseTab = ref('body')
  const showSaveDialog = ref(false)
  const showBusinessFlowDialog = ref(false)

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
      if (typeof response.data === 'string') {
        return response.data
      }
      return JSON.stringify(response.data, null, 2)
    } catch {
      return String(response.data)
    }
  })

  // Actions
  const loadTestCases = async (projectId) => {
    try {
      const res = await apiTestsAPI.getApiTestCases(projectId)
      testCases.value = res.data
    } catch (error) {
      ElMessage.error('加载测试用例失败: ' + error.message)
      throw error
    }
  }

  const loadTestCase = (testCase) => {
    selectedTestCase.value = testCase

    // 重置当前请求
    Object.assign(currentRequest, {
      method: testCase.method,
      url: testCase.url,
      headers: Object.entries(testCase.headers || {}).map(([key, value]) => ({ key, value })),
      params: Object.entries(testCase.params || {}).map(([key, value]) => ({ key, value })),
      body: testCase.body ? JSON.stringify(testCase.body, null, 2) : '{}',
      bodyType: 'json',
      formData: [{ key: '', value: '' }],
      rawBody: '',
      expected_data: testCase.expected_data ? JSON.stringify(testCase.expected_data, null, 2) : '{}'
    })

    // 确保至少有一个空的header和param
    if (currentRequest.headers.length === 0) {
      currentRequest.headers.push({ key: 'Content-Type', value: 'application/json' })
    }
    if (currentRequest.params.length === 0) {
      currentRequest.params.push({ key: '', value: '' })
    }
  }

  // src/stores/apiTestStore.js (部分更新)
const sendRequest = async () => {
  if (!canSend.value) return { success: false, message: '无法发送请求' }

  isLoading.value = true
  response.error = null

  try {
    const startTime = Date.now()

    // 构建请求配置
    const config = {
      method: currentRequest.method,
      headers: {},
      mode: 'cors', // 添加 CORS 支持
      credentials: 'omit' // 根据需求调整
    }

    // 添加 headers
    currentRequest.headers.forEach(header => {
      if (header.key && header.value) {
        config.headers[header.key] = header.value
      }
    })

    // 构建 URL 和查询参数
    let url = currentRequest.url
    // 确保URL以http或https开头
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url
    }

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

    // 处理请求体
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(currentRequest.method)) {
      if (currentRequest.bodyType === 'json') {
        try {
          if (currentRequest.body) {
            config.body = JSON.parse(currentRequest.body)
          }
        } catch (e) {
          throw new Error('JSON格式错误: ' + e.message)
        }
        if (!config.headers['Content-Type']) {
          config.headers['Content-Type'] = 'application/json'
        }
      } else if (currentRequest.bodyType === 'form-data') {
        const formData = new FormData()
        currentRequest.formData.forEach(field => {
          if (field.key && field.value) {
            formData.append(field.key, field.value)
          }
        })
        config.body = formData
        // 不要设置 Content-Type，让浏览器自动设置
        delete config.headers['Content-Type']
      } else if (currentRequest.bodyType === 'raw') {
        config.body = currentRequest.rawBody
        if (!config.headers['Content-Type']) {
          config.headers['Content-Type'] = 'text/plain'
        }
      }
    }

    console.log('发送请求:', { url, config })

    // 发送请求
    const result = await fetch(url, config)

    // 计算响应时间
    response.duration = Date.now() - startTime

    // 处理响应
    response.status = result.status
    response.headers = {}

    // 获取响应头
    result.headers.forEach((value, key) => {
      response.headers[key] = value
    })

    // 解析响应数据
    const contentType = result.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      try {
        response.data = await result.json()
      } catch (e) {
        response.data = await result.text()
      }
    } else {
      response.data = await result.text()
    }

    return { success: true, message: '请求成功' }
  } catch (error) {
    console.error('请求错误:', error)
    response.error = error.message
    response.data = null
    response.status = null
    response.duration = null
    return { success: false, message: '请求失败: ' + error.message }
  } finally {
    isLoading.value = false
  }
}

  const clearAll = () => {
    Object.assign(currentRequest, {
      method: 'GET',
      url: '',
      headers: [{ key: 'Content-Type', value: 'application/json' }],
      params: [{ key: '', value: '' }],
      body: '{}',
      bodyType: 'json',
      formData: [{ key: '', value: '' }],
      rawBody: '',
      expected_data: '{}'
    })

    Object.assign(response, {
      status: null,
      data: null,
      headers: {},
      duration: null,
      error: null
    })

    selectedTestCase.value = null
    ElMessage.success('已清空所有数据')
  }

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

  return {
    // 状态
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

    // 计算属性
    canSend,
    statusCodeClass,
    formattedResponse,

    // Actions
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
  }
})