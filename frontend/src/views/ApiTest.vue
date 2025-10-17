<template>
  <div class="api-tester">
    <div class="tester-header">
      <h2>API 测试工具</h2>
      <div class="header-actions">
        <button @click="saveRequest" class="btn btn-secondary">保存请求</button>
        <button @click="clearAll" class="btn btn-outline">清空</button>
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
                <option value="PATCH">PATCH</option>
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

    <!-- 历史记录侧边栏 -->
    <div class="history-sidebar" :class="{ open: showHistory }">
      <div class="sidebar-header">
        <h3>历史记录</h3>
        <button @click="toggleHistory" class="btn btn-icon">
          <span>×</span>
        </button>
      </div>
      <div class="history-list">
        <div
          v-for="(item, index) in requestHistory"
          :key="index"
          @click="loadRequest(item)"
          class="history-item"
        >
          <div class="history-method">{{ item.method }}</div>
          <div class="history-url">{{ item.url }}</div>
          <div class="history-time">{{ formatTime(item.timestamp) }}</div>
          <button
            @click.stop="deleteHistory(index)"
            class="btn btn-icon btn-danger"
          >
            ×
          </button>
        </div>
        <div v-if="requestHistory.length === 0" class="no-history">
          暂无历史记录
        </div>
      </div>
    </div>

    <!-- 历史记录触发按钮 -->
    <button @click="toggleHistory" class="history-toggle">
      📜 历史记录
    </button>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

// 响应状态
const response = reactive({
  status: null,
  data: null,
  headers: {},
  duration: null,
  error: null
})

// 当前请求配置
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

// UI 状态
const isLoading = ref(false)
const showHistory = ref(false)
const activeRequestTab = ref('headers')
const activeResponseTab = ref('body')

// 历史记录
const requestHistory = ref([])

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

// 方法
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

  try {
    const startTime = Date.now()

    // 构建请求配置
    const config = {
      method: currentRequest.method,
      headers: {}
    }

    // 添加 headers
    currentRequest.headers.forEach(header => {
      if (header.key && header.value) {
        config.headers[header.key] = header.value
      }
    })

    // 构建 URL 和查询参数
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

    // 处理请求体
    if (['POST', 'PUT', 'PATCH'].includes(currentRequest.method)) {
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
        // 注意：使用 FormData 时不要设置 Content-Type，浏览器会自动设置
        delete config.headers['Content-Type']
      } else if (currentRequest.bodyType === 'raw') {
        config.body = currentRequest.rawBody
      }
    }

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
      response.data = await result.json()
    } else {
      response.data = await result.text()
    }

  } catch (error) {
    response.error = error.message
    response.data = null
    response.status = null
  } finally {
    isLoading.value = false
  }
}

const saveRequest = () => {
  const historyItem = {
    ...JSON.parse(JSON.stringify(currentRequest)),
    timestamp: Date.now()
  }
  requestHistory.value.unshift(historyItem)
  saveToLocalStorage()
}

const loadRequest = (item) => {
  Object.assign(currentRequest, JSON.parse(JSON.stringify(item)))
  showHistory.value = false
}

const deleteHistory = (index) => {
  requestHistory.value.splice(index, 1)
  saveToLocalStorage()
}

const toggleHistory = () => {
  showHistory.value = !showHistory.value
}

const clearAll = () => {
  if (confirm('确定要清空所有数据吗？')) {
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
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

// 本地存储
const saveToLocalStorage = () => {
  localStorage.setItem('apiTesterHistory', JSON.stringify(requestHistory.value))
}

const loadFromLocalStorage = () => {
  const saved = localStorage.getItem('apiTesterHistory')
  if (saved) {
    requestHistory.value = JSON.parse(saved)
  }
}

// 生命周期
onMounted(() => {
  loadFromLocalStorage()
})
</script>

<style scoped>
.api-tester {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tester-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
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
  border-bottom-color: #007bff;
  color: #007bff;
}

.tab-content {
  padding: 15px;
}

.key-value-pairs {
  space-y: 10px;
}

.key-value-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.key-value-row .form-input {
  flex: 1;
}

.body-type-selector {
  margin-bottom: 15px;
  width: 200px;
}

.form-select, .form-input, .form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-textarea {
  font-family: 'Courier New', monospace;
  resize: vertical;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-outline {
  background: transparent;
  border: 1px solid #ddd;
  color: #333;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-icon {
  padding: 4px 8px;
  background: none;
  border: none;
  cursor: pointer;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.response-info {
  display: flex;
  gap: 15px;
  font-size: 14px;
}

.status-success { color: #28a745; }
.status-warning { color: #ffc107; }
.status-error { color: #dc3545; }

.response-content {
  padding: 15px;
  max-height: 400px;
  overflow: auto;
}

.response-data {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.header-item {
  display: flex;
  margin-bottom: 8px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.header-key {
  font-weight: bold;
  margin-right: 10px;
  min-width: 150px;
}

.history-sidebar {
  position: fixed;
  top: 0;
  right: -400px;
  width: 400px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  transition: right 0.3s;
  z-index: 1000;
}

.history-sidebar.open {
  right: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
}

.history-list {
  padding: 20px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background: #f8f9fa;
}

.history-method {
  background: #007bff;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: bold;
}

.history-url {
  flex: 1;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-time {
  font-size: 12px;
  color: #6c757d;
}

.history-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 10px 15px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  z-index: 999;
}

.no-response, .no-history {
  text-align: center;
  color: #6c757d;
  padding: 40px 20px;
}

@media (max-width: 768px) {
  .tester-body {
    grid-template-columns: 1fr;
  }

  .config-row {
    flex-direction: column;
  }

  .history-sidebar {
    width: 100%;
    right: -100%;
  }
}
</style>