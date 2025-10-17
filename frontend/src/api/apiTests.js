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
    return api.post(`/projects/${projectId}/api-tests/run`, { test_case_ids: testCaseIds })
  },

  // 获取测试报告
  getApiTestReports(projectId) {
    return api.get(`/projects/${projectId}/api-tests/reports`)
  }
}

export default apiTestsAPI