import api from './index'
import { mockApiTests } from '@/api/mockApiTests'

// 设置为 true 使用模拟数据，false 使用真实 API
const USE_MOCK_DATA = false;

export const apiTestsAPI = {
  // 获取接口测试用例
  getApiTestCases(projectId) {
    console.log(`[API] 获取测试用例: /projects/${projectId}/api-tests`)
    if (USE_MOCK_DATA) {
      return mockApiTests.getApiTestCases(projectId);
    }
    return api.get(`/projects/${projectId}/api-tests`)
  },

  // 创建接口测试用例
  createApiTestCase(projectId, testCase) {
    console.log(`[API] 创建测试用例: /projects/${projectId}/api-tests`, testCase)
    if (USE_MOCK_DATA) {
      return mockApiTests.createApiTestCase(projectId, testCase);
    }
    return api.post(`/projects/${projectId}/api-tests`, testCase)
  },

  // 更新接口测试用例
  updateApiTestCase(testCaseId, testCase) {
    console.log(`[API] 更新测试用例: /api-tests/${testCaseId}`, testCase)
    if (USE_MOCK_DATA) {
      // 模拟实现
      return Promise.resolve({ data: { ...testCase, id: testCaseId } });
    }
    return api.put(`/api-tests/${testCaseId}`, testCase)
  },

  // 删除接口测试用例
  deleteApiTestCase(testCaseId) {
    console.log(`[API] 删除测试用例: /api-tests/${testCaseId}`)
    if (USE_MOCK_DATA) {
      return mockApiTests.deleteApiTestCase(testCaseId);
    }
    return api.delete(`/api-tests/${testCaseId}`)
  },

  // 执行接口测试
  runApiTest(projectId, testCaseIds = []) {
    console.log(`[API] 执行测试: /projects/${projectId}/api-tests/run`, { test_case_ids: testCaseIds })
    if (USE_MOCK_DATA) {
      return mockApiTests.runApiTest(projectId, testCaseIds);
    }
    return api.post(`/projects/${projectId}/api-tests/run`, { test_case_ids: testCaseIds })
  },

  // 获取测试报告
  getApiTestReports(projectId) {
    console.log(`[API] 获取测试报告: /projects/${projectId}/api-tests/reports`)
    if (USE_MOCK_DATA) {
      // 返回空报告列表
      return Promise.resolve({ data: [] });
    }
    return api.get(`/projects/${projectId}/api-tests/reports`)
  },

  // 创建业务流程
  createBusinessFlow(projectId, businessFlow) {
    console.log(`[API] 创建业务流程: /projects/${projectId}/business-flows`, businessFlow)
    if (USE_MOCK_DATA) {
      return mockApiTests.createBusinessFlow(projectId, businessFlow);
    }
    return api.post(`/projects/${projectId}/business-flows`, businessFlow)
  },

  // 获取业务流程
  getBusinessFlows(projectId) {
    console.log(`[API] 获取业务流程: /projects/${projectId}/business-flows`)
    if (USE_MOCK_DATA) {
      return mockApiTests.getBusinessFlows(projectId);
    }
    return api.get(`/projects/${projectId}/business-flows`)
  },

  // 健康检查
  healthCheck() {
    console.log('[API] 健康检查: /api-test')
    if (USE_MOCK_DATA) {
      return Promise.resolve({ data: { status: "healthy", message: "Mock API is working" } });
    }
    return api.get('/api-test')
  }
}

export default apiTestsAPI