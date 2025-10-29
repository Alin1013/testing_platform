<template>
  <div class="request-section">
    <div class="request-config">
      <div class="config-row">
        <div class="method-selector">
          <el-select v-model="currentRequest.method" placeholder="选择方法">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </div>
        <div class="url-input">
          <el-input
            v-model="currentRequest.url"
            placeholder="输入 API URL"
            clearable
          />
        </div>
        <div class="send-button">
          <el-button
            @click="$emit('send')"
            :disabled="!canSend"
            :loading="isLoading"
            type="primary"
          >
            {{ isLoading ? '发送中...' : '发送请求' }}
          </el-button>
        </div>
      </div>

      <!-- 请求参数标签页 -->
      <el-tabs :model-value="activeRequestTab" @update:model-value="$emit('update:activeRequestTab', $event)" class="request-tabs">
        <el-tab-pane label="请求头" name="headers">
          <div class="key-value-pairs">
            <div class="key-value-list">
              <div
                v-for="(header, index) in currentRequest.headers"
                :key="index"
                class="key-value-row"
              >
                <el-input
                  v-model="header.key"
                  placeholder="Header 名称"
                  class="key-input"
                />
                <el-input
                  v-model="header.value"
                  placeholder="Header 值"
                  class="value-input"
                />
                <el-button
                  @click="$emit('remove-header', index)"
                  type="danger"
                  text
                >
                  删除
                </el-button>
              </div>
            </div>
            <el-button @click="$emit('add-header')" type="primary" text>
              添加 Header
            </el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="查询参数" name="params">
          <div class="key-value-pairs">
            <div class="key-value-list">
              <div
                v-for="(param, index) in currentRequest.params"
                :key="index"
                class="key-value-row"
              >
                <el-input
                  v-model="param.key"
                  placeholder="参数名"
                  class="key-input"
                />
                <el-input
                  v-model="param.value"
                  placeholder="参数值"
                  class="value-input"
                />
                <el-button
                  @click="$emit('remove-param', index)"
                  type="danger"
                  text
                >
                  删除
                </el-button>
              </div>
            </div>
            <el-button @click="$emit('add-param')" type="primary" text>
              添加参数
            </el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="请求体" name="body">
          <div class="body-editor">
            <div class="body-type-selector">
              <el-select v-model="currentRequest.bodyType" placeholder="选择Body类型">
                <el-option label="JSON" value="json" />
                <el-option label="Form Data" value="form-data" />
                <el-option label="Raw Text" value="raw" />
              </el-select>
            </div>

            <div v-if="currentRequest.bodyType === 'json'" class="json-editor">
              <el-input
                v-model="currentRequest.body"
                type="textarea"
                placeholder='输入 JSON 数据，例如: {"key": "value"}'
                :rows="8"
                class="json-textarea"
              />
            </div>

            <div v-if="currentRequest.bodyType === 'form-data'" class="key-value-pairs">
              <div class="key-value-list">
                <div
                  v-for="(field, index) in currentRequest.formData"
                  :key="index"
                  class="key-value-row"
                >
                  <el-input
                    v-model="field.key"
                    placeholder="字段名"
                    class="key-input"
                  />
                  <el-input
                    v-model="field.value"
                    placeholder="字段值"
                    class="value-input"
                  />
                  <el-button
                    @click="$emit('remove-form-data', index)"
                    type="danger"
                    text
                  >
                    删除
                  </el-button>
                </div>
              </div>
              <el-button @click="$emit('add-form-data')" type="primary" text>
                添加字段
              </el-button>
            </div>

            <div v-if="currentRequest.bodyType === 'raw'" class="raw-editor">
              <el-input
                v-model="currentRequest.rawBody"
                type="textarea"
                placeholder="输入原始文本数据"
                :rows="8"
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="预期结果" name="expected">
          <div class="expected-editor">
            <el-input
              v-model="currentRequest.expected_data"
              type="textarea"
              placeholder='输入预期结果 JSON，例如: {"status": "success", "code": 200}'
              :rows="8"
              class="expected-textarea"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentRequest: {
    type: Object,
    required: true
  },
  activeRequestTab: {
    type: String,
    default: 'headers'
  },
  canSend: {
    type: Boolean,
    default: false
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits([
  'update:activeRequestTab',
  'send',
  'add-header',
  'remove-header',
  'add-param',
  'remove-param',
  'add-form-data',
  'remove-form-data'
])
</script>

<style scoped>
.request-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.request-config {
  padding: 20px;
}

.config-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
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

.request-tabs {
  margin-top: 20px;
}

.key-value-pairs {
  display: flex;
  flex-direction: column;
  height: 300px;
}

.key-value-list {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 10px;
  border: 1px solid #e6e8eb;
  border-radius: 4px;
  padding: 10px;
  max-height: 250px;
}

.key-value-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.key-input, .value-input {
  flex: 1;
}

.body-type-selector {
  margin-bottom: 15px;
  width: 200px;
}

.json-textarea, .expected-textarea {
  font-family: 'Courier New', monospace;
}

/* 滚动条样式 */
.key-value-list::-webkit-scrollbar {
  width: 6px;
}

.key-value-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.key-value-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.key-value-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>