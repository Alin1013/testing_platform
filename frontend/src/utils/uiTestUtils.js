// 日期格式化
export const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch {
    return dateString
  }
}

// 状态类型映射
export const getStatusType = (status) => {
  const types = {
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'info'
  }
  return types[status] || 'info'
}

// 步骤占位符
export const getValuePlaceholder = (action) => {
  const placeholders = {
    'click': '点击操作无需输入值',
    'fill': '输入要填充的文本',
    'goto': '输入要导航的URL',
    'waitForSelector': '等待操作无需输入值',
    'assert': '输入期望的值或文本'
  }
  return placeholders[action] || '输入值'
}

// 生成Playwright脚本
export const generatePlaywrightScript = (testCaseForm) => {
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

// 表单验证规则
export const testCaseRules = {
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

export const businessFlowRules = {
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