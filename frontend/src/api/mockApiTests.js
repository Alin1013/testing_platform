const MockApiTests = (() => {
  // 模拟数据存储 - 在闭包中保护数据
  let mockTestCases = [
{
        id: 1,
        case_name: "获取用户列表",
        project_id: 1,
        method: "GET",
        url: "https://jsonplaceholder.typicode.com/users",
        headers: { "Content-Type": "application/json" },
        params: {},
        body: null,
        expected_data: {},
        created_at: "2023-01-01T00:00:00"
      },
      {
        id: 2,
        case_name: "创建新用户",
        project_id: 1,
        method: "POST",
        url: "https://jsonplaceholder.typicode.com/users",
        headers: { "Content-Type": "application/json" },
        params: {},
        body: {
          name: "John Doe",
          email: "john@example.com",
          username: "johndoe"
        },
        expected_data: { id: 11 },
        created_at: "2023-01-02T00:00:00"
      }
  ];

  let nextId = 3;

  return {
    getApiTestCases(projectId) {
      // 过滤出对应项目的测试用例
      const projectCases = mockTestCases.filter(testCase => testCase.project_id === projectId);
      console.log(`[Mock] 获取测试用例: projectId=${projectId}, 数量=${projectCases.length}`)
      return Promise.resolve({
        data: projectCases
      });
    },

    createApiTestCase(projectId, testCase) {
      const newTestCase = {
        ...testCase,
        id: nextId++,
        project_id: projectId
      };

      mockTestCases.push(newTestCase);
      console.log(`[Mock] 创建测试用例:`, newTestCase)

      return Promise.resolve({
        data: newTestCase
      });
    },

    // 修复删除方法 - 实际从数据中移除
    deleteApiTestCase(projectId, testCaseId) {
      console.log(`[Mock] 删除测试用例: projectId=${projectId}, testCaseId=${testCaseId}`)

      // 找到要删除的测试用例索引
      const index = mockTestCases.findIndex(testCase =>
        testCase.id === testCaseId && testCase.project_id === projectId
      );

      if (index !== -1) {
        // 从数组中移除
        const deletedCase = mockTestCases.splice(index, 1)[0];
        console.log(`[Mock] 成功删除测试用例: ${deletedCase.case_name}, 剩余用例数量: ${mockTestCases.length}`)

        return Promise.resolve({
          data: {
            message: '删除成功',
            deleted_id: testCaseId
          }
        });
      } else {
        // 如果没有找到，返回错误
        return Promise.reject({
          message: '测试用例不存在'
        });
      }
    },

    updateApiTestCase(projectId, testCaseId, testCase) {
      const index = mockTestCases.findIndex(tc =>
        tc.id === testCaseId && tc.project_id === projectId
      );

      if (index !== -1) {
        mockTestCases[index] = { ...testCase, id: testCaseId, project_id: projectId };
        return Promise.resolve({
          data: mockTestCases[index]
        });
      } else {
        return Promise.reject({
          message: '测试用例不存在'
        });
      }
    },

    runApiTest(projectId, testCaseIds) {
      return Promise.resolve({
        data: {
          report_id: Math.floor(Math.random() * 1000),
          status: 'completed',
          results: testCaseIds.map(id => ({
            test_case_id: id,
            status: 'passed',
            duration: Math.random() * 1000
          }))
        }
      });
    },

    createBusinessFlow(projectId, businessFlow) {
      return Promise.resolve({
        data: {
          ...businessFlow,
          id: Math.floor(Math.random() * 1000),
          project_id: projectId
        }
      });
    },

    getBusinessFlows(projectId) {
      return Promise.resolve({
        data: []
      });
    },

    sendApiRequest(requestData) {
      // 模拟 API 响应
      return Promise.resolve({
        data: {
          status: 200,
          data: {
            message: '请求成功',
            timestamp: new Date().toISOString()
          },
          headers: {
            'content-type': 'application/json',
            'x-request-id': Math.random().toString(36).substring(7)
          }
        }
      });
    },

    // 重置模拟数据（用于测试）
    resetMockData() {
      mockTestCases = [
        {
          id: 1,
          case_name: '获取用户列表',
          method: 'GET',
          url: 'https://api.example.com/users',
          project_id: 1,
          headers: [{ key: 'Content-Type', value: 'application/json' }],
          params: [],
          body: '',
          body_type: 'json',
          form_data: [],
          raw_body: '',
          expected_data: '{"status": "success"}'
        },
        {
          id: 2,
          case_name: '创建用户',
          method: 'POST',
          url: 'https://api.example.com/users',
          project_id: 1,
          headers: [{ key: 'Content-Type', value: 'application/json' }],
          params: [],
          body: '{"name": "test", "email": "test@example.com"}',
          body_type: 'json',
          form_data: [],
          raw_body: '',
          expected_data: '{"status": "success", "code": 201}'
        }
      ];
      nextId = 3;
      console.log('[Mock] 重置模拟数据完成')
    },

    // 获取当前模拟数据（用于调试）
    getMockData() {
      return mockTestCases;
    }
  };
})();

export { MockApiTests as mockApiTests };