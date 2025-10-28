import api from './index'

export const apiTestsAPI = {
  // 获取接口测试用例
  getApiTestCases(projectId) {
    return api.get(`/projects/${projectId}/api-tests`)
  },

  // 创建接口测试用例
  createApiTestCase(projectId, testCase) {
    return api.post(`/projects/${projectId}/api-tests`, testCase)
  },

  // 更新接口测试用例
  updateApiTestCase(testCaseId, testCase) {
    return api.put(`/api-tests/${testCaseId}`, testCase)
  },

  // 删除接口测试用例
  deleteApiTestCase(testCaseId) {
    return api.delete(`/api-tests/${testCaseId}`)
  },

  // 执行接口测试
  runApiTest(projectId, testCaseIds = []) {
    return api.post(`/projects/${projectId}/api-tests/run`, {
      test_case_ids: testCaseIds
    })
  },

  // 获取测试报告
  getApiTestReports(projectId) {
    return api.get(`/projects/${projectId}/api-tests/reports`)
  },

  // 创建业务流程
  createBusinessFlow(projectId, businessFlow) {
    return api.post(`/projects/${projectId}/business-flows`, businessFlow)
  },

  // 获取业务流程
  getBusinessFlows(projectId) {
    return api.get(`/projects/${projectId}/business-flows`)
  },

  // 获取特定业务流程
  getBusinessFlow(flowId) {
    return api.get(`/business-flows/${flowId}`)
  },

  // 执行业务流程测试
  runBusinessFlow(flowId) {
    return api.post(`/business-flows/${flowId}/run`)
  },

  // 健康检查
  healthCheck() {
    return api.get('/api-test/health')
  }
}

export default apiTestsAPI