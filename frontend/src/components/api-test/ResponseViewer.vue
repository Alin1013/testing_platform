<!-- src/components/api-test/ResponseViewer.vue -->
<template>
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

    <el-tabs :model-value="activeResponseTab" @update:model-value="$emit('update:activeResponseTab', $event)" class="response-tabs">
      <el-tab-pane label="响应体" name="body">
        <div class="response-body">
          <pre v-if="response.data" class="response-data">{{ formattedResponse }}</pre>
          <div v-else class="no-response">
            {{
              response.error
                ? `错误: ${response.error}`
                : '点击发送请求获取响应数据'
            }}
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="响应头" name="headers">
        <div class="response-headers">
          <div
            v-for="(value, key) in response.headers"
            :key="key"
            class="header-item"
          >
            <span class="header-key">{{ key }}:</span>
            <span class="header-value">{{ value }}</span>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
defineProps({
  response: {
    type: Object,
    required: true
  },
  activeResponseTab: {
    type: String,
    default: 'body'
  },
  statusCodeClass: {
    type: String,
    default: ''
  },
  formattedResponse: {
    type: String,
    default: ''
  }
})

defineEmits(['update:activeResponseTab'])
</script>

<style scoped>
.response-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e6e8eb;
}

.response-info {
  display: flex;
  gap: 15px;
  font-size: 14px;
}

.status-success { color: #67c23a; }
.status-warning { color: #e6a23c; }
.status-error { color: #f56c6c; }

.response-content {
  padding: 20px;
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

.no-response {
  text-align: center;
  color: #909399;
  padding: 40px 20px;
}
</style>