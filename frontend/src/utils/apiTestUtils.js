// src/utils/apiTestUtils.js
export const getMethodClass = (method) => {
  const methodClasses = {
    GET: 'method-get',
    POST: 'method-post',
    PUT: 'method-put',
    PATCH: 'method-patch',
    DELETE: 'method-delete'
  }
  return methodClasses[method] || 'method-default'
}

export const validateJson = (jsonString) => {
  if (!jsonString) return true
  try {
    JSON.parse(jsonString)
    return true
  } catch {
    return false
  }
}

export const formatJson = (jsonString) => {
  if (!jsonString) return ''
  try {
    return JSON.stringify(JSON.parse(jsonString), null, 2)
  } catch {
    return jsonString
  }
}

export const buildRequestData = (currentRequest, caseName) => {
  const requestData = {
    case_name: caseName,
    method: currentRequest.method,
    url: currentRequest.url,
    headers: currentRequest.headers.reduce((acc, { key, value }) => {
      if (key && value) acc[key] = value
      return acc
    }, {}),
    params: currentRequest.params.reduce((acc, { key, value }) => {
      if (key && value) acc[key] = value
      return acc
    }, {})
  }

  // 处理请求体
  if (currentRequest.bodyType === 'json') {
    try {
      requestData.body = currentRequest.body ? JSON.parse(currentRequest.body) : {}
    } catch (e) {
      requestData.body = {}
    }
  } else if (currentRequest.bodyType === 'form-data') {
    requestData.body = currentRequest.formData.reduce((acc, { key, value }) => {
      if (key && value) acc[key] = value
      return acc
    }, {})
  } else {
    requestData.body = currentRequest.rawBody || ''
  }

  // 处理预期结果
  if (currentRequest.expected_data) {
    try {
      requestData.expected_data = JSON.parse(currentRequest.expected_data)
    } catch (e) {
      requestData.expected_data = {}
    }
  } else {
    requestData.expected_data = {}
  }

  return requestData
}

// 验证URL格式
export const isValidUrl = (string) => {
  try {
    new URL(string)
    return true
  } catch (_) {
    return false
  }
}