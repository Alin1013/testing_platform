<!-- src/views/DebugPage.vue -->
<template>
  <div class="debug-page">
    <h1>API 调试页面</h1>

    <el-card>
      <template #header>
        <h3>API 连接测试</h3>
      </template>

      <div class="test-buttons">
        <el-button @click="testBasicAPI" type="primary">测试基础 API</el-button>
        <el-button @click="testProjectsAPI">测试项目 API</el-button>
        <el-button @click="testApiTests">测试 API 测试端点</el-button>
      </div>

      <div class="results">
        <h4>测试结果:</h4>
        <pre>{{ testResults }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { apiTestsAPI } from '../api/apiTests'
import { projectsAPI } from '../api/projects'

const testResults = ref('')

const testBasicAPI = async () => {
  try {
    testResults.value = '测试基础 API...\n'
    const response = await fetch('http://localhost:8000/api/v1/api-test')
    const data = await response.json()
    testResults.value += `✅ 基础 API 正常: ${JSON.stringify(data, null, 2)}\n`
  } catch (error) {
    testResults.value += `❌ 基础 API 失败: ${error.message}\n`
  }
}

const testProjectsAPI = async () => {
  try {
    testResults.value += '\n测试项目 API...\n'
    const response = await projectsAPI.getProjects()
    testResults.value += `✅ 项目 API 正常: 获取到 ${response.data.length} 个项目\n`
  } catch (error) {
    testResults.value += `❌ 项目 API 失败: ${error.message}\n`
  }
}

const testApiTests = async () => {
  try {
    testResults.value += '\n测试 API 测试端点...\n'
    const response = await apiTestsAPI.getApiTestCases(1)
    testResults.value += `✅ API 测试端点正常: 获取到 ${response.data.length} 个测试用例\n`
  } catch (error) {
    testResults.value += `❌ API 测试端点失败: ${error.message}\n`
    if (error.response) {
      testResults.value += `   状态码: ${error.response.status}\n`
      testResults.value += `   响应数据: ${JSON.stringify(error.response.data, null, 2)}\n`
    }
  }
}
</script>

<style scoped>
.debug-page {
  padding: 20px;
}

.test-buttons {
  margin-bottom: 20px;
}

.test-buttons .el-button {
  margin-right: 10px;
}

.results pre {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  max-height: 400px;
  overflow-y: auto;
}
</style>