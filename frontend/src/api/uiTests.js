import api from './index'

export const uiTestsAPI = {
  // 获取UI测试用例
  getUiTestCases(projectId) {
    return api.get(`/projects/${projectId}/ui-tests`)
  },

  // 创建UI测试用例
  createUiTestCase(projectId, testCase) {
    return api.post(`/projects/${projectId}/ui-tests`, testCase)
  },

  // 更新UI测试用例
  updateUiTestCase(testCaseId, testCase) {
    return api.put(`/ui-tests/${testCaseId}`, testCase)
  },

  // 删除UI测试用例
  deleteUiTestCase(testCaseId) {
    return api.delete(`/ui-tests/${testCaseId}`)
  },

  // 执行UI测试
  runUiTest(projectId, testCaseIds = []) {
    return api.post(`/projects/${projectId}/ui-tests/run`, { test_case_ids: testCaseIds })
  },

  // 获取UI测试报告
  getUiTestReports(projectId) {
    return api.get(`/projects/${projectId}/ui-tests/reports`)
  },

  // 获取UI测试附件
  getUiTestArtifacts(projectId, reportId) {
    return api.get(`/projects/${projectId}/ui-tests/reports/${reportId}/artifacts`)
  },

  // 创建UI业务流程
  createUiBusinessFlow(projectId, businessFlow) {
    return api.post(`/projects/${projectId}/ui-business-flows`, businessFlow)
  },
    //获取业务流程列表
    getBusinessFlow(projectId) {
      return api.get(`/projects/${projectId}/ui-business-flows`)
    },
    //删除业务流程
    deleteBusinessFlow(flowId) {
      return api.delete(`/ui-business-flows/${flowId})`)
    }
}

export default uiTestsAPI