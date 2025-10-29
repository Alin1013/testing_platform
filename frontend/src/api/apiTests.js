// src/api/apiTests.js
import api from './index'
import { mockApiTests } from '@/api/mockApiTests'

// 设置为 true 使用模拟数据，false 使用真实 API
const USE_MOCK_DATA = false; // 确保启用模拟数据

// 确保 projectId 是数字
const ensureNumber = (id) => {
  if (typeof id === 'string') {
    const num = parseInt(id, 10);
    return isNaN(num) ? 0 : num;
  }
  return id;
}

export const apiTestsAPI = {
  // 获取接口测试用例
  getApiTestCases(projectId) {
    const id = ensureNumber(projectId);
    console.log(`[API] 获取测试用例: /projects/${id}/api-test-cases`)
    if (USE_MOCK_DATA) {
      return mockApiTests.getApiTestCases(id);
    }
    return api.get(`/projects/${id}/api-test-cases`)
  },

  // 创建接口测试用例
  createApiTestCase(projectId, testCase) {
    const id = ensureNumber(projectId);
    console.log(`[API] 创建测试用例: /projects/${id}/api-test-cases`, testCase)
    if (USE_MOCK_DATA) {
      return mockApiTests.createApiTestCase(id, testCase);
    }
    return api.post(`/projects/${id}/api-test-cases`, testCase)
  },

  // 更新接口测试用例
  updateApiTestCase(projectId, testCaseId, testCase) {
    const pid = ensureNumber(projectId);
    const tid = ensureNumber(testCaseId);
    console.log(`[API] 更新测试用例: /projects/${pid}/api-test-cases/${tid}`, testCase)
    if (USE_MOCK_DATA) {
      return mockApiTests.updateApiTestCase(pid, tid, testCase);
    }
    return api.put(`/projects/${pid}/api-test-cases/${tid}`, testCase)
  },

  // 删除接口测试用例
  deleteApiTestCase(projectId, testCaseId) {
    const pid = ensureNumber(projectId);
    const tid = ensureNumber(testCaseId);
    console.log(`[API] 删除测试用例: /projects/${pid}/api-test-cases/${tid}`)

    if (USE_MOCK_DATA) {
      return mockApiTests.deleteApiTestCase(pid, tid);
    }

    return api.delete(`/projects/${pid}/api-test-cases/${tid}`)
  },

  // 执行接口测试
  runApiTest(projectId, testCaseIds = []) {
    const id = ensureNumber(projectId);
    console.log(`[API] 执行测试: /projects/${id}/api-test-cases/run`, { test_case_ids: testCaseIds })
    if (USE_MOCK_DATA) {
      return mockApiTests.runApiTest(id, testCaseIds);
    }
    return api.post(`/projects/${id}/api-test-cases/run`, { test_case_ids: testCaseIds })
  },

  // 获取测试报告
  getApiTestReports(projectId) {
    const id = ensureNumber(projectId);
    console.log(`[API] 获取测试报告: /projects/${id}/api-test-cases/reports`)
    if (USE_MOCK_DATA) {
      // 返回空报告列表
      return Promise.resolve({ data: [] });
    }
    return api.get(`/projects/${id}/api-test-cases/reports`)
  },

  // 创建业务流程
  createBusinessFlow(projectId, businessFlow) {
    const id = ensureNumber(projectId);
    console.log(`[API] 创建业务流程: /projects/${id}/business-flows`, businessFlow)
    if (USE_MOCK_DATA) {
      return mockApiTests.createBusinessFlow(id, businessFlow);
    }
    return api.post(`/projects/${id}/business-flows`, businessFlow)
  },

  // 获取业务流程
  getBusinessFlows(projectId) {
    const id = ensureNumber(projectId);
    console.log(`[API] 获取业务流程: /projects/${id}/business-flows`)
    if (USE_MOCK_DATA) {
      return mockApiTests.getBusinessFlows(id);
    }
    return api.get(`/projects/${id}/business-flows`)
  },

  // 发送API请求
  sendApiRequest(requestData) {
    console.log('[API] 发送API请求: /api-test-cases/send', requestData)
    if (USE_MOCK_DATA) {
      return mockApiTests.sendApiRequest(requestData);
    }
    return api.post('/api-test-cases/send', requestData)
  },

  // 健康检查
  healthCheck() {
    console.log('[API] 健康检查: /api-test')
    if (USE_MOCK_DATA) {
      return Promise.resolve({ data: { status: "healthy", message: "Mock API is working" } });
    }
    return api.get('/api-test')
  },

  // 重置模拟数据（用于测试）
  resetMockData() {
    if (USE_MOCK_DATA && mockApiTests.resetMockData) {
      return mockApiTests.resetMockData();
    }
    return Promise.resolve();
  }
}

export default apiTestsAPI