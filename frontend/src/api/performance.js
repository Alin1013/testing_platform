import api from './index'

export const performanceAPI = {
  // 创建性能测试
  createPerformanceTest(projectId, testConfig) {
    return api.post(`/projects/${projectId}/performance-tests`, testConfig)
  },

  // 执行性能测试
  runPerformanceTest(projectId, testConfig) {
    return api.post(`/projects/${projectId}/performance-tests/run`, testConfig)
  },

  // 获取性能测试报告
  getPerformanceReports(projectId) {
    return api.get(`/projects/${projectId}/performance-tests/reports`)
  },

  // 停止性能测试
  stopPerformanceTest(projectId, testId) {
    return api.post(`/projects/${projectId}/performance-tests/${testId}/stop`)
  }
}

export default performanceAPI