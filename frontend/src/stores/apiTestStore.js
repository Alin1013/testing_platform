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
      // 确保 projectId 是数字
      const id = ensureNumber(projectId)
      const res = await apiTestsAPI.getApiTestCases(id)
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
      headers: convertObjectToKeyValueArray(testCase.headers),
      params: convertObjectToKeyValueArray(testCase.params),
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

  // 辅助函数：确保 ID 是数字
  const ensureNumber = (id) => {
    if (typeof id === 'string') {
      const num = parseInt(id, 10)
      return isNaN(num) ? 0 : num
    }
    return id
  }

  // 辅助函数：将对象转换为键值对数组
  const convertObjectToKeyValueArray = (obj) => {
    if (!obj || typeof obj !== 'object') {
      return [{ key: '', value: '' }]
    }
    const entries = Object.entries(obj)
    if (entries.length === 0) {
      return [{ key: '', value: '' }]
    }
    return entries.map(([key, value]) => ({ key, value }))
  }

  // 辅助函数：验证 JSON
  const validateJson = (jsonString) => {
    if (!jsonString || jsonString.trim() === '') return true
    try {
      JSON.parse(jsonString)
      return true
    } catch {
      return false
    }
  }

  // 辅助函数：构建请求数据
  const buildRequestData = (caseName, projectId) => {
    // 处理 headers
    const headers = {}
    currentRequest.headers.forEach(header => {
      if (header.key && header.value) {
        headers[header.key] = header.value
      }
    })

    // 处理 params
    const params = {}
    currentRequest.params.forEach(param => {
      if (param.key && param.value) {
        params[param.key] = param.value
      }
    })

    // 处理 body
    let body = null
    if (currentRequest.bodyType === 'json') {
      try {
        body = currentRequest.body && currentRequest.body.trim() !== '' ?
          JSON.parse(currentRequest.body) : null
      } catch (e) {
        body = null
      }
    } else if (currentRequest.bodyType === 'form-data') {
      body = {}
      currentRequest.formData.forEach(field => {
        if (field.key && field.value) {
          body[field.key] = field.value
        }
      })
      // 如果 formData 为空，设置为 null
      if (Object.keys(body).length === 0) {
        body = null
      }
    } else if (currentRequest.bodyType === 'raw') {
      body = currentRequest.rawBody && currentRequest.rawBody.trim() !== '' ?
        currentRequest.rawBody : null
    }

    // 处理 expected_data
    let expected_data = null
    if (currentRequest.expected_data && currentRequest.expected_data.trim() !== '') {
      try {
        expected_data = JSON.parse(currentRequest.expected_data)
      } catch (e) {
        expected_data = null
      }
    }

    const requestData = {
      case_name: caseName,
      method: currentRequest.method,
      url: currentRequest.url,
      headers: Object.keys(headers).length > 0 ? headers : null,
      params: Object.keys(params).length > 0 ? params : null,
      body: body,
      expected_data: expected_data,
      project_id: ensureNumber(projectId)
    }

    console.log('构建的请求数据:', JSON.stringify(requestData, null, 2))
    return requestData
  }

  // 保存测试用例
  const saveTestCase = async (projectId, caseName) => {
    try {
      // 验证必要字段
      if (!caseName || caseName.trim() === '') {
        throw new Error('测试用例名称不能为空')
      }

      if (!currentRequest.url || currentRequest.url.trim() === '') {
        throw new Error('请求 URL 不能为空')
      }

      // 验证 JSON 格式
      if (currentRequest.bodyType === 'json' && currentRequest.body) {
        if (!validateJson(currentRequest.body)) {
          throw new Error('请求体 JSON 格式错误')
        }
      }

      if (currentRequest.expected_data) {
        if (!validateJson(currentRequest.expected_data)) {
          throw new Error('预期结果 JSON 格式错误')
        }
      }

      const requestData = buildRequestData(caseName, projectId)
      console.log('保存测试用例 - 发送数据:', requestData)

      const response = await apiTestsAPI.createApiTestCase(requestData.project_id, requestData)
      console.log('保存测试用例 - 响应:', response)

      // 重新加载测试用例列表
      await loadTestCases(projectId)

      ElMessage.success('测试用例保存成功')
      return response.data
    } catch (error) {
      console.error('保存测试用例失败:', error)
      const errorMessage = error.response?.data?.detail || error.message || '保存失败'
      ElMessage.error('保存失败: ' + errorMessage)
      throw error
    }
  }

  // 更新测试用例
  const updateTestCase = async (testCaseId, projectId, caseName) => {
    try {
      const requestData = buildRequestData(caseName, projectId)
      const response = await apiTestsAPI.updateApiTestCase(testCaseId, requestData)

      // 重新加载测试用例列表
      await loadTestCases(projectId)

      ElMessage.success('测试用例更新成功')
      return response.data
    } catch (error) {
      console.error('更新测试用例失败:', error)
      const errorMessage = error.response?.data?.detail || error.message || '更新失败'
      ElMessage.error('更新失败: ' + errorMessage)
      throw error
    }
  }

  // 删除测试用例
  const deleteTestCase = async (testCaseId) => {
    try {
      await apiTestsAPI.deleteApiTestCase(testCaseId)
      ElMessage.success('测试用例删除成功')

      // 从本地列表中移除
      const index = testCases.value.findIndex(tc => tc.id === testCaseId)
      if (index !== -1) {
        testCases.value.splice(index, 1)
      }

      // 如果删除的是当前选中的测试用例，清空选中状态
      if (selectedTestCase.value?.id === testCaseId) {
        selectedTestCase.value = null
      }
    } catch (error) {
      console.error('删除测试用例失败:', error)
      const errorMessage = error.response?.data?.detail || error.message || '删除失败'
      ElMessage.error('删除失败: ' + errorMessage)
      throw error
    }
  }

  const sendRequest = async () => {
    if (!canSend.value) return { success: false, message: '无法发送请求' }

    isLoading.value = true
    // 重置响应数据
    Object.assign(response, {
      status: null,
      data: null,
      headers: {},
      duration: null,
      error: null
    })

    try {
      const startTime = Date.now()

      // 构建请求配置
      const config = {
        method: currentRequest.method,
        headers: {},
        mode: 'cors',
        credentials: 'omit'
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
            if (currentRequest.body && currentRequest.body.trim() !== '') {
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
      const fetchResponse = await fetch(url, config)

      // 计算响应时间
      response.duration = Date.now() - startTime

      // 处理响应
      response.status = fetchResponse.status

      // 获取响应头
      const headers = {}
      fetchResponse.headers.forEach((value, key) => {
        headers[key] = value
      })
      response.headers = headers

      // 解析响应数据
      const contentType = fetchResponse.headers.get('content-type') || ''

        try {
          if (contentType.includes('application/json')) {
            const text = await fetchResponse.text()
            try {
              response.data = text ? JSON.parse(text) : null
            } catch (jsonError) {
              console.warn('JSON解析失败，返回原始文本:', jsonError)
              response.data = text
            }
          } else if (contentType.includes('text/')) {
            response.data = await fetchResponse.text()
          } else {
            // 对于其他类型，尝试获取文本，如果失败则使用 blob
            try {
              response.data = await fetchResponse.text()
            } catch (textError) {
              console.warn('文本解析失败，使用blob:', textError)
              const blob = await fetchResponse.blob()
              response.data = `Blob data (${blob.type}, ${blob.size} bytes)`
            }
          }
        } catch (parseError) {
          console.error('解析响应数据失败:', parseError)
          response.data = `无法解析响应数据: ${parseError.message}`
        }

        console.log('收到响应 - 状态:', response.status)
        console.log('收到响应 - 数据:', response.data)
        console.log('收到响应 - 数据类型:', typeof response.data)

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
  // 在 store 的 return 部分添加
    const debugResponse = () => {
  console.log('=== 响应调试信息 ===')
  console.log('状态码:', response.status)
  console.log('响应数据:', response.data)
  console.log('响应数据类型:', typeof response.data)
  console.log('响应头:', response.headers)
  console.log('响应时间:', response.duration)
  console.log('错误:', response.error)
  console.log('===================')
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
    saveTestCase,
    updateTestCase,
    deleteTestCase,
    clearAll,
    addHeader,
    removeHeader,
    addParam,
    removeParam,
    addFormData,
    removeFormData,

    // 辅助函数
    ensureNumber,
    buildRequestData,
    validateJson,
      debugResponse
  }
})