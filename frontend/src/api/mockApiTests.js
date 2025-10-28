// src/api/mockApiTests.js
class MockApiTests {
  constructor() {
    this.testCases = [
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
    this.businessFlows = [];
    this.nextId = 3;
  }

  // 模拟网络延迟
  delay(ms = 500) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async getApiTestCases(projectId) {
    await this.delay();
    const cases = this.testCases.filter(tc => tc.project_id == projectId);
    return { data: cases };
  }

  async createApiTestCase(projectId, testCase) {
    await this.delay();
    const newCase = {
      id: this.nextId++,
      project_id: parseInt(projectId),
      ...testCase,
      created_at: new Date().toISOString()
    };
    this.testCases.push(newCase);
    return { data: newCase };
  }

  async deleteApiTestCase(testCaseId) {
    await this.delay();
    const index = this.testCases.findIndex(tc => tc.id === testCaseId);
    if (index !== -1) {
      this.testCases.splice(index, 1);
    }
    return { data: { message: "Test case deleted successfully" } };
  }

  async createBusinessFlow(projectId, businessFlow) {
    await this.delay();
    const newFlow = {
      id: this.businessFlows.length + 1,
      project_id: parseInt(projectId),
      ...businessFlow,
      created_at: new Date().toISOString()
    };
    this.businessFlows.push(newFlow);
    return { data: newFlow };
  }

  async getBusinessFlows(projectId) {
    await this.delay();
    const flows = this.businessFlows.filter(bf => bf.project_id == projectId);
    return { data: flows };
  }

  async runApiTest(projectId, testCaseIds = []) {
    await this.delay(2000);
    return {
      data: {
        message: `Tests started for ${testCaseIds.length} test cases`,
        test_count: testCaseIds.length
      }
    };
  }
}

export const mockApiTests = new MockApiTests();