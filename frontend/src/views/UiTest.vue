<template>
  <div class="ui-test-container">
    <!-- 添加返回按钮到顶部 -->
    <div class="page-header">
      <el-button @click="$router.push('/projects')" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回项目
      </el-button>
      <h2 class="page-title">UI测试</h2>
      <div style="width: 120px"></div> <!-- 占位保持对称 -->
    </div>
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建UI测试用例
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 单元测试 -->
        <el-tab-pane label="单元测试" name="unit">
          <el-table :data="uiTestCases" v-loading="loading" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="case_name" label="用例名称" />
            <el-table-column prop="created_at" label="创建时间">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="editTestCase(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteTestCase(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="action-bar">
            <el-button @click="runSelectedTests" :disabled="selectedCases.length === 0">
              运行选中用例
            </el-button>
          </div>
        </el-tab-pane>

        <!-- 业务测试 -->
        <el-tab-pane label="业务测试" name="business">
          <div class="business-flow-section">
            <el-button type="primary" @click="showBusinessFlowDialog = true">
              创建业务流程
            </el-button>

            <el-table :data="businessFlows" style="margin-top: 20px">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="flow_name" label="流程名称" />
              <el-table-column prop="case_ids" label="包含用例数">
                <template #default="scope">
                  {{ scope.row.case_ids ? scope.row.case_ids.length : 0 }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="scope">
                  <el-button size="small" @click="runBusinessFlow(scope.row)">运行</el-button>
                  <el-button size="small" type="danger" @click="deleteBusinessFlow(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 测试报告 -->
        <el-tab-pane label="测试报告" name="reports">
          <el-table :data="testReports">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="report_name" label="报告名称" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button
                  size="small"
                  @click="viewReport(scope.row)"
                  :disabled="scope.row.status !== 'completed'"
                >
                  查看报告
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 测试结果 -->
        <el-tab-pane label="测试结果" name="results">
          <div class="test-results">
            <el-card v-for="report in completedReports" :key="report.id" class="result-card">
              <template #header>
                <div class="result-header">
                  <h3>{{ report.report_name }}</h3>
                  <el-tag type="success">已完成</el-tag>
                </div>
              </template>
              <p>创建时间: {{ formatDate(report.created_at) }}</p>
              <div class="result-actions">
                <el-button type="primary" @click="viewReport(report)">查看详情</el-button>
                <el-button @click="downloadArtifacts(report)">下载附件</el-button>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button @click="$router.push('/projects')">返回项目</el-button>
    </div>

    <!-- 创建/编辑测试用例对话框 -->
    <el-dialog
      :title="isEditing ? '编辑UI测试用例' : '创建UI测试用例'"
      v-model="showCreateDialog"
      width="600px"
    >
      <el-form :model="testCaseForm" :rules="testCaseRules" ref="testCaseFormRef" label-width="100px">
        <el-form-item label="用例名称：" prop="case_name">
          <el-input v-model="testCaseForm.case_name" placeholder="请输入用例名称" />
        </el-form-item>

        <el-form-item label="URL：" prop="base_url">
          <el-input v-model="testCaseForm.base_url" placeholder="请输入URL" />
        </el-form-item>

        <el-form-item label="操作步骤：" prop="steps">
          <div class="simple-steps-container">
            <div v-for="(step, index) in testCaseForm.steps" :key="index" class="simple-step-item">
              <div class="step-number">步骤 {{ index + 1 }}</div>
              <div class="step-fields">
                <div class="field-group">
                  <label class="field-label">路径地址：</label>
                  <el-input
                    v-model="step.selector"
                    placeholder="输入CSS选择器或XPath"
                    class="field-input"
                    :disabled="step.action === 'goto'"
                  />
                </div>

                <div class="field-group">
                  <label class="field-label">输入值：</label>
                  <el-input
                    v-model="step.value"
                    :placeholder="getValuePlaceholder(step.action)"
                    class="field-input"
                  />
                </div>

                <div class="field-group">
                  <label class="field-label">方法：</label>
                  <el-select
                    v-model="step.action"
                    placeholder="选择方法"
                    class="field-input method-select"
                    @change="onStepActionChange(step)"
                  >
                    <el-option label="点击元素" value="click" />
                    <el-option label="输入文本" value="fill" />
                    <el-option label="页面导航" value="goto" />
                    <el-option label="等待元素" value="waitForSelector" />
                    <el-option label="断言验证" value="assert" />
                  </el-select>
                </div>

                <el-button
                  type="danger"
                  size="small"
                  @click="removeStep(index)"
                  class="step-remove-btn"
                  :disabled="testCaseForm.steps.length <= 1"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>

          <div class="add-step-section">
            <el-button
              type="primary"
              @click="addStep"
              icon="Plus"
              class="add-step-btn"
            >
              添加步骤
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="是否录制：">
          <el-checkbox v-model="testCaseForm.record">启用录制功能</el-checkbox>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleTestCaseSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 创建业务流程对话框 -->
    <el-dialog title="创建业务流程" v-model="showBusinessFlowDialog" width="500px">
      <el-form :model="businessFlowForm" :rules="businessFlowRules" ref="businessFlowFormRef" label-width="100px">
        <el-form-item label="流程名称：" prop="flow_name">
          <el-input v-model="businessFlowForm.flow_name" placeholder="请输入流程名称" />
        </el-form-item>
        <el-form-item label="选择用例：" prop="case_ids">
          <el-select
            v-model="businessFlowForm.case_ids"
            multiple
            placeholder="请选择测试用例"
            style="width: 100%"
          >
            <el-option
              v-for="testcase in uiTestCases"
              :key="testcase.id"
              :label="testcase.case_name"
              :value="testcase.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBusinessFlowDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBusinessFlowSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus,ArrowLeft } from '@element-plus/icons-vue'
import { uiTestsAPI } from '../api/uiTests'

const route = useRoute()
const router = useRouter()
const projectId = ref(route.query.projectId || 1)

// 响应式数据
const activeTab = ref('unit')
const loading = ref(false)
const showCreateDialog = ref(false)
const showBusinessFlowDialog = ref(false)
const isEditing = ref(false)
const testCaseFormRef = ref()
const businessFlowFormRef = ref()
const editingTestCaseId = ref(null)

const uiTestCases = ref([])
const businessFlows = ref([])
const testReports = ref([])
const selectedCases = ref([])

// 表单数据
const testCaseForm = reactive({
  case_name: '',
  base_url: '',
  steps: [],
  record: false
})

const businessFlowForm = reactive({
  flow_name: '',
  case_ids: []
})

// 表单验证规则
const testCaseRules = {
  case_name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' },
    { min: 2, max: 50, message: '用例名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  base_url: [
    { required: true, message: '请输入URL', trigger: 'blur' },
    {
      pattern: /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i,
      message: '请输入有效的URL',
      trigger: 'blur'
    }
  ],
  steps: [
    {
      required: true,
      validator: (rule, value, callback) => {
        if (!value || value.length === 0) {
          callback(new Error('至少添加一个操作步骤'))
        } else {
          const invalidSteps = value.filter(step => {
            if (!step.action) return true
            if (step.action === 'goto' && !step.value) return true
            if (['click', 'fill', 'waitForSelector'].includes(step.action) && !step.selector) return true
            return false
          })

          if (invalidSteps.length > 0) {
            callback(new Error('请完善所有步骤的必填字段'))
          } else {
            callback()
          }
        }
      },
      trigger: 'change'
    }
  ]
}

const businessFlowRules = {
  flow_name: [
    { required: true, message: '请输入流程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '流程名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  case_ids: [
    {
      required: true,
      type: 'array',
      min: 1,
      message: '请至少选择一个测试用例',
      trigger: 'change'
    }
  ]
}

// 计算属性
const completedReports = computed(() => {
  return testReports.value.filter(report => report.status === 'completed')
})

const hasTestCases = computed(() => {
  return uiTestCases.value.length > 0
})

// 工具函数
const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch {
    return dateString
  }
}

const getStatusType = (status) => {
  const types = {
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'info'
  }
  return types[status] || 'info'
}

// 步骤管理
const addStep = () => {
  testCaseForm.steps.push({
    action: '',
    selector: '',
    value: ''
  })
}

const removeStep = (index) => {
  if (testCaseForm.steps.length > 1) {
    testCaseForm.steps.splice(index, 1)
  } else {
    ElMessage.warning('至少需要保留一个步骤')
  }
}

// 步骤占位符辅助函数
const getValuePlaceholder = (action) => {
  const placeholders = {
    'click': '点击操作无需输入值',
    'fill': '输入要填充的文本',
    'goto': '输入要导航的URL',
    'waitForSelector': '等待操作无需输入值',
    'assert': '输入期望的值或文本'
  }
  return placeholders[action] || '输入值'
}

const onStepActionChange = (step) => {
  // 根据操作类型清空不需要的字段
  if (step.action === 'goto') {
    step.selector = ''
  } else if (step.action === 'click' || step.action === 'waitForSelector') {
    step.value = ''
  }
}

// 数据获取函数 - 只在网络错误时提示
const fetchUITestCases = async () => {
  loading.value = true
  try {
    const response = await uiTestsAPI.getUiTestCases(projectId.value)
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

const fetchBusinessFlows = async () => {
  try {
    const response = await uiTestsAPI.getBusinessFlows(projectId.value)
    businessFlows.value = response.data || []
  } catch (error) {
    console.error('获取业务流程失败:', error)
    businessFlows.value = []
  }
}


const fetchTestReports = async () => {
  try {
    const response = await uiTestsAPI.getUiTestReports(projectId.value)
    testReports.value = response.data || []
  } catch (error) {
    console.error('获取测试报告失败:', error)
    testReports.value = []
  }
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

// 事件处理函数
const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

const editTestCase = (testCase) => {
  isEditing.value = true
  editingTestCaseId.value = testCase.id

  // 重置表单
  Object.assign(testCaseForm, {
    case_name: testCase.case_name || '',
    base_url: testCase.base_url || '',
    record: testCase.record || false,
    steps: testCase.steps ? JSON.parse(JSON.stringify(testCase.steps)) : []
  })

  // 如果没有步骤，尝试从脚本解析
  if (testCaseForm.steps.length === 0 && testCase.script_content) {
    testCaseForm.steps = parseScriptToSteps(testCase.script_content)
  }

  showCreateDialog.value = true

  // 确保DOM更新后滚动到顶部
  nextTick(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  })
}

const deleteTestCase = async (testCase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例 "${testCase.case_name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await uiTestsAPI.deleteUiTestCase(testCase.id)
    ElMessage.success('测试用例删除成功')
    await fetchUITestCases()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除测试用例失败:', error)
      // 只在网络错误时提示
      if (!error.response) {
        ElMessage.error('删除测试用例失败: 网络连接错误')
      }
    }
  }
}

const runSelectedTests = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请选择要运行的测试用例')
    return
  }

  try {
    const caseIds = selectedCases.value.map(testcase => testcase.id)
    await uiTestsAPI.runUiTest(projectId.value, caseIds)
    ElMessage.success('测试已开始运行，请稍后查看报告')

    // 开始轮询报告状态
    startPollingReports()
  } catch (error) {
    console.error('运行测试失败:', error)
    // 只在网络错误时提示
    if (!error.response) {
      ElMessage.error('运行测试失败: 网络连接错误')
    }
  }
}

const runBusinessFlow = async (businessFlow) => {
  if (!businessFlow.case_ids || businessFlow.case_ids.length === 0) {
    ElMessage.warning('该业务流程没有包含任何测试用例')
    return
  }

  try {
    await uiTestsAPI.runUiTest(projectId.value, businessFlow.case_ids)
    ElMessage.success('业务流程测试已开始运行，请稍后查看报告')

    // 开始轮询报告状态
    startPollingReports()
  } catch (error) {
    console.error('运行业务流程测试失败:', error)
    // 只在网络错误时提示
    if (!error.response) {
      ElMessage.error('运行业务流程测试失败: 网络连接错误')
    }
  }
}

const deleteBusinessFlow = async (businessFlow) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除业务流程 "${businessFlow.flow_name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await uiTestsAPI.deleteBusinessFlow(businessFlow.id)
    ElMessage.success('业务流程删除成功')
    await fetchBusinessFlows()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除业务流程失败:', error)
      // 只在网络错误时提示
      if (!error.response) {
        ElMessage.error('删除业务流程失败: 网络连接错误')
      }
    }
  }
}

const viewReport = (report) => {
  if (!report.report_path) {
    ElMessage.warning('报告路径不存在')
    return
  }

  // 在新窗口中打开报告
  const reportUrl = report.report_path.startsWith('http')
    ? report.report_path
    : `/reports/${report.report_path}`

  window.open(reportUrl, '_blank')
}

const downloadArtifacts = async (report) => {
  try {
    const response = await uiTestsAPI.getUiTestArtifacts(projectId.value, report.id)
    if (response.data.screenshots.length === 0 && response.data.videos.length === 0) {
      ElMessage.info('该报告没有可下载的附件')
      return
    }

    // 实现下载逻辑
    ElMessage.success('开始下载附件')
    // 这里可以根据实际附件URL进行下载
  } catch (error) {
    console.error('获取测试附件失败:', error)
    // 只在网络错误时提示
    if (!error.response) {
      ElMessage.error('获取测试附件失败: 网络连接错误')
    }
  }
}

// 轮询报告状态
let pollingInterval = null
const startPollingReports = () => {
  // 清除之前的轮询
  if (pollingInterval) {
    clearInterval(pollingInterval)
  }

  // 立即获取一次报告
  fetchTestReports()

  // 开始轮询
  pollingInterval = setInterval(async () => {
    await fetchTestReports()

    // 检查是否还有运行中的报告
    const runningReports = testReports.value.filter(r => r.status === 'running')
    if (runningReports.length === 0) {
      clearInterval(pollingInterval)
      pollingInterval = null
      ElMessage.success('所有测试运行完成')
    }
  }, 3000)

  // 10分钟后自动停止轮询
  setTimeout(() => {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
      ElMessage.info('报告轮询已停止')
    }
  }, 600000)
}

// 表单提交处理
const handleTestCaseSubmit = async () => {
  if (!testCaseFormRef.value) return

  try {
    const valid = await testCaseFormRef.value.validate()
    if (!valid) return

    // 生成Playwright脚本
    const scriptContent = generatePlaywrightScript()

    // 准备提交数据
    const submitData = {
      case_name: testCaseForm.case_name,
      base_url: testCaseForm.base_url,
      steps: testCaseForm.steps,
      script_content: scriptContent,
      record: testCaseForm.record,
      project_id: projectId.value
    }

    if (isEditing.value) {
      await uiTestsAPI.updateUiTestCase(editingTestCaseId.value, submitData)
      ElMessage.success('测试用例更新成功')
    } else {
      await uiTestsAPI.createUiTestCase(projectId.value, submitData)
      ElMessage.success('测试用例创建成功')
    }

    showCreateDialog.value = false
    resetTestCaseForm()
    await fetchUITestCases()
  } catch (error) {
    console.error('提交测试用例失败:', error)
    if (error.errors) {
      // 验证错误，不需要额外提示
      return
    }
    // 只在网络错误时提示
    if (!error.response) {
      ElMessage.error('操作失败: 网络连接错误')
    }
  }
}

const handleBusinessFlowSubmit = async () => {
  if (!businessFlowFormRef.value) return

  try {
    const valid = await businessFlowFormRef.value.validate()
    if (!valid) return

    await uiTestsAPI.createUiBusinessFlow(projectId.value, businessFlowForm)
    ElMessage.success('业务流程创建成功')
    showBusinessFlowDialog.value = false
    resetBusinessFlowForm()
    await fetchBusinessFlows()
  } catch (error) {
    console.error('创建业务流程失败:', error)
    if (error.errors) return
    // 只在网络错误时提示
    if (!error.response) {
      ElMessage.error('创建业务流程失败: 网络连接错误')
    }
  }
}

// 生成Playwright脚本
const generatePlaywrightScript = () => {
  const escapeQuote = (str) => str ? str.replace(/'/g, "\\'") : ''

  let script = ''

  // 添加URL导航
  if (testCaseForm.base_url) {
    script += `await page.goto('${escapeQuote(testCaseForm.base_url)}');\n`
  }

  // 如果需要录制，添加录制开始代码
  if (testCaseForm.record) {
    script += `await context.tracing.start({ screenshots: true, snapshots: true });\n`
  }

  // 添加步骤代码
  testCaseForm.steps.forEach((step) => {
    const escapedSelector = escapeQuote(step.selector)
    const escapedValue = escapeQuote(step.value)

    switch(step.action) {
      case 'click':
        script += `await page.locator('${escapedSelector}').click();\n`
        break
      case 'fill':
        script += `await page.locator('${escapedSelector}').fill('${escapedValue}');\n`
        break
      case 'goto':
        script += `await page.goto('${escapedValue}');\n`
        break
      case 'waitForSelector':
        script += `await page.locator('${escapedSelector}').waitFor();\n`
        break
    }
  })

  // 如果需要录制，添加录制结束代码
  if (testCaseForm.record) {
    script += `await context.tracing.stop({ path: 'trace.zip' });\n`
  }

  return script
}

// 重置表单
const resetTestCaseForm = () => {
  Object.assign(testCaseForm, {
    case_name: '',
    base_url: '',
    steps: [{ action: '', selector: '', value: '' }],
    record: false
  })
  isEditing.value = false
  editingTestCaseId.value = null
  if (testCaseFormRef.value) {
    testCaseFormRef.value.clearValidate()
  }
}

const resetBusinessFlowForm = () => {
  Object.assign(businessFlowForm, {
    flow_name: '',
    case_ids: []
  })
  if (businessFlowFormRef.value) {
    businessFlowFormRef.value.clearValidate()
  }
}

// 初始化
onMounted(() => {
  fetchUITestCases()
  fetchBusinessFlows()
  fetchTestReports()

  // 组件卸载时清除轮询
  return () => {
    if (pollingInterval) {
      clearInterval(pollingInterval)
    }
  }
})
</script>

<style scoped>
.ui-test-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
}

/* 新增页面头部样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.page-title {
  text-align: center;
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  flex: 1;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header {
  display: flex;
  justify-content: flex-end; /* 右对齐 */
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.action-bar {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.back-button {
  margin-top: 20px;
  text-align: center;
  padding: 20px 0;
}

.test-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.result-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
  height: fit-content;
}

.result-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 5px;
}

.result-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

/* 简化版步骤表单样式 */
.simple-steps-container {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 16px;
  background: #fafafa;
  margin-bottom: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.simple-step-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.simple-step-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.simple-step-item:last-child {
  margin-bottom: 0;
}

.step-number {
  font-weight: 600;
  color: #409eff;
  margin-bottom: 12px;
  font-size: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.step-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.field-label {
  width: 80px;
  text-align: right;
  font-size: 14px;
  color: #606266;
  flex-shrink: 0;
}

.field-input {
  flex: 1;
}

.method-select {
  min-width: 200px;
}

.step-remove-btn {
  align-self: flex-end;
  margin-top: 8px;
}

.add-step-section {
  display: flex;
  justify-content: center;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
  margin-top: 16px;
}

.add-step-btn {
  padding: 10px 24px;
}

/* 表单标签样式优化 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

/* 响应式调整 */
@media(max-width: 768px){
  .page-header{
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  .page-title{
    order:-1;
  }
  .back-button{
    align-self: flex-start;
  }
}
@media (max-width: 1200px) {
  .ui-test-container {
    padding: 15px;
  }

  .test-results {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }

  .card-header h2 {
    text-align: center;
    margin-bottom: 10px;
  }

  .field-group {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .field-label {
    width: auto;
    text-align: left;
    font-weight: 500;
  }

  .step-remove-btn {
    align-self: stretch;
  }

  .simple-steps-container {
    padding: 12px;
  }

  .simple-step-item {
    padding: 12px;
  }

  .test-results {
    grid-template-columns: 1fr;
  }

  .result-actions {
    flex-direction: column;
  }

  .result-actions .el-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .ui-test-container {
    padding: 10px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto;
  }

  .simple-steps-container {
    padding: 10px;
  }

  .simple-step-item {
    padding: 12px;
  }
}

/* 滚动条样式 */
.simple-steps-container::-webkit-scrollbar {
  width: 6px;
}

.simple-steps-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.simple-steps-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.simple-steps-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>