import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { uiTestsAPI } from '@/api/uiTests'

export const useUiTestStore = defineStore('uiTest', () => {
  // 状态
  const uiTestCases = ref([])
  const businessFlows = ref([])
  const testReports = ref([])
  const selectedCases = ref([])
  const loading = ref(false)

  // 计算属性
  const completedReports = computed(() => {
    return testReports.value.filter(report => report.status === 'completed')
  })

  const hasTestCases = computed(() => {
    return uiTestCases.value.length > 0
  })

  // Actions
  const fetchUITestCases = async (projectId) => {
    loading.value = true
    try {
      const response = await uiTestsAPI.getUiTestCases(projectId)
      uiTestCases.value = response.data || []

      // 处理步骤数据
      uiTestCases.value.forEach(caseItem => {
        if (!caseItem.steps && caseItem.script_content) {
          try {
            caseItem.steps = parseScriptToSteps(caseItem.script_content)
          } catch (e) {
            console.warn('解析测试用例步骤失败', e)
            caseItem.steps = []
          }
        }
      })
    } catch (error) {
      console.error('获取UI测试用例失败:', error)
      uiTestCases.value = []
    } finally {
      loading.value = false
    }
  }

  const fetchBusinessFlows = async (projectId) => {
    try {
      const response = await uiTestsAPI.getBusinessFlows(projectId)
      businessFlows.value = response.data || []
    } catch (error) {
      console.error('获取业务流程失败:', error)
      businessFlows.value = []
    }
  }

  const fetchTestReports = async (projectId) => {
    try {
      const response = await uiTestsAPI.getUiTestReports(projectId)
      testReports.value = response.data || []
    } catch (error) {
      console.error('获取测试报告失败:', error)
      testReports.value = []
    }
  }

  const createTestCase = async (projectId, data) => {
    const response = await uiTestsAPI.createUiTestCase(projectId, data)
    await fetchUITestCases(projectId)
    return response
  }

  const updateTestCase = async (caseId, data) => {
    const response = await uiTestsAPI.updateUiTestCase(caseId, data)
    return response
  }

  const deleteTestCase = async (caseId, projectId) => {
    await uiTestsAPI.deleteUiTestCase(caseId)
    await fetchUITestCases(projectId)
  }

  const createBusinessFlow = async (projectId, data) => {
    const response = await uiTestsAPI.createUiBusinessFlow(projectId, data)
    await fetchBusinessFlows(projectId)
    return response
  }

  const deleteBusinessFlow = async (flowId, projectId) => {
    await uiTestsAPI.deleteBusinessFlow(flowId)
    await fetchBusinessFlows(projectId)
  }

  const runUiTest = async (projectId, caseIds) => {
    const response = await uiTestsAPI.runUiTest(projectId, caseIds)
    return response
  }

  const setSelectedCases = (selection) => {
    selectedCases.value = selection
  }

  // 解析脚本为步骤
  const parseScriptToSteps = (scriptContent) => {
    const steps = []
    if (!scriptContent) return steps

    const lines = scriptContent.split('\n').filter(line => line.trim())

    lines.forEach(line => {
      const trimmedLine = line.trim()

      if (trimmedLine.startsWith('await page.goto')) {
        const urlMatch = trimmedLine.match(/'([^']+)'|"([^"]+)"/)
        if (urlMatch) {
          steps.push({
            action: 'goto',
            selector: '',
            value: urlMatch[1] || urlMatch[2]
          })
        }
      } else if (trimmedLine.includes('page.locator')) {
        const selectorMatch = trimmedLine.match(/'([^']+)'|"([^"]+)"/)
        if (selectorMatch) {
          const selector = selectorMatch[1] || selectorMatch[2]

          if (trimmedLine.includes('.click()')) {
            steps.push({ action: 'click', selector, value: '' })
          } else if (trimmedLine.includes('.fill(')) {
            const valueMatch = trimmedLine.match(/fill\(['"]([^'"]*)['"]\)/)
            steps.push({
              action: 'fill',
              selector,
              value: valueMatch ? valueMatch[1] : ''
            })
          } else if (trimmedLine.includes('.waitFor()')) {
            steps.push({ action: 'waitForSelector', selector, value: '' })
          }
        }
      }
    })

    return steps
  }

  return {
    // 状态
    uiTestCases,
    businessFlows,
    testReports,
    selectedCases,
    loading,

    // 计算属性
    completedReports,
    hasTestCases,

    // Actions
    fetchUITestCases,
    fetchBusinessFlows,
    fetchTestReports,
    createTestCase,
    updateTestCase,
    deleteTestCase,
    createBusinessFlow,
    deleteBusinessFlow,
    runUiTest,
    setSelectedCases
  }
})