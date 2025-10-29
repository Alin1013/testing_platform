<template>
  <div class="response-section">
    <div class="response-header">
      <h3>响应</h3>
      <div class="response-info">
        <span v-if="response.status !== null && response.status !== undefined"
              class="status-code"
              :class="statusCodeClass">
          状态码: {{ response.status }}
        </span>
        <span v-if="response.duration !== null && response.duration !== undefined"
              class="response-time">
          响应时间: {{ response.duration }}ms
        </span>
        <span v-if="response.error" class="response-error">
          错误: {{ response.error }}
        </span>
      </div>
    </div>

    <!-- 修复：使用 :model-value 和 @update:model-value 替代 v-model -->
    <el-tabs
      :model-value="activeResponseTab"
      @update:model-value="$emit('update:activeResponseTab', $event)"
      class="response-tabs"
    >
      <el-tab-pane label="响应体" name="body">
        <div class="response-body">
          <div v-if="hasResponseData" class="response-content">
            <div class="response-data-container">
              <pre class="response-data">{{ formattedResponse }}</pre>
            </div>
          </div>
          <div v-else-if="response.error" class="no-response error">
            <el-alert
              :title="`请求错误: ${response.error}`"
              type="error"
              :closable="false"
            />
          </div>
          <div v-else class="no-response">
            <el-empty description="点击发送请求获取响应数据" :image-size="100" />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="响应头" name="headers">
        <div class="response-headers">
          <div v-if="hasHeaders" class="headers-content">
            <div class="headers-container">
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
          <div v-else class="no-headers">
            <el-empty description="无响应头信息" :image-size="80" />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="原始信息" name="raw">
        <div class="raw-response">
          <div class="raw-data-container">
            <pre class="raw-data">{{ rawResponseInfo }}</pre>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElEmpty, ElAlert } from 'element-plus'

const props = defineProps({
  response: {
    type: Object,
    required: true
  },
  activeResponseTab: {
    type: String,
    default: 'body'
  }
})

// 明确声明要发出的事件
const emit = defineEmits(['update:activeResponseTab'])

// 计算属性
const statusCodeClass = computed(() => {
  if (props.response.status === null || props.response.status === undefined) return ''
  if (props.response.status < 300) return 'status-success'
  if (props.response.status < 400) return 'status-warning'
  return 'status-error'
})

const hasResponseData = computed(() => {
  return props.response.data !== null && props.response.data !== undefined
})

const hasHeaders = computed(() => {
  return props.response.headers && Object.keys(props.response.headers).length > 0
})

const formattedResponse = computed(() => {
  if (!hasResponseData.value) return ''

  try {
    if (typeof props.response.data === 'string') {
      // 尝试解析JSON字符串
      try {
        const parsed = JSON.parse(props.response.data)
        return JSON.stringify(parsed, null, 2)
      } catch {
        return props.response.data
      }
    } else if (typeof props.response.data === 'object') {
      return JSON.stringify(props.response.data, null, 2)
    } else {
      return String(props.response.data)
    }
  } catch {
    return String(props.response.data)
  }
})

const rawResponseInfo = computed(() => {
  const info = {
    status: props.response.status,
    duration: props.response.duration,
    headers: props.response.headers,
    data: props.response.data,
    error: props.response.error
  }
  return JSON.stringify(info, null, 2)
})
</script>

<style scoped>
.response-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e6e8eb;
  flex-shrink: 0;
}

.response-info {
  display: flex;
  gap: 15px;
  font-size: 14px;
  align-items: center;
}

.status-success {
  color: #67c23a;
  font-weight: bold;
}
.status-warning {
  color: #e6a23c;
  font-weight: bold;
}
.status-error {
  color: #f56c6c;
  font-weight: bold;
}

.response-error {
  color: #f56c6c;
  font-weight: bold;
}

.response-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.el-tabs__content) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.el-tab-pane) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.response-body,
.response-headers,
.raw-response {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.response-content,
.headers-content,
.raw-response {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.response-data-container,
.headers-container,
.raw-data-container {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background: #f8f9fa;
  margin: 0;
  border-radius: 0;
}

.response-data,
.raw-data {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  line-height: 1.5;
  color: #333;
}

/* 响应数据特定样式 */
.response-data {
  background: transparent;
  padding: 0;
}

/* 响应头样式 */
.header-item {
  display: flex;
  margin-bottom: 12px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  padding: 8px 0;
  border-bottom: 1px solid #e8e8e8;
  line-height: 1.4;
}

.header-key {
  font-weight: bold;
  margin-right: 15px;
  min-width: 200px;
  color: #409eff;
  flex-shrink: 0;
}

.header-value {
  flex: 1;
  color: #606266;
  word-break: break-all;
}

.no-response,
.no-headers {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 40px 20px;
}

.error {
  color: #f56c6c;
}

:deep(.el-empty__description) {
  margin-top: 10px;
}

/* 滚动条样式 */
.response-data-container::-webkit-scrollbar,
.headers-container::-webkit-scrollbar,
.raw-data-container::-webkit-scrollbar {
  width: 8px;
}

.response-data-container::-webkit-scrollbar-track,
.headers-container::-webkit-scrollbar-track,
.raw-data-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.response-data-container::-webkit-scrollbar-thumb,
.headers-container::-webkit-scrollbar-thumb,
.raw-data-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.response-data-container::-webkit-scrollbar-thumb:hover,
.headers-container::-webkit-scrollbar-thumb:hover,
.raw-data-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>