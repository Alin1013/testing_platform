<template>
  <el-dialog
    :title="isEditing ? '编辑UI测试用例' : '创建UI测试用例'"
    v-model="visible"
    width="600px"
    @closed="handleClose"
  >
    <el-form
      :model="formData"
      :rules="rules"
      ref="formRef"
      label-width="100px"
    >
      <el-form-item label="用例名称：" prop="case_name">
        <el-input v-model="formData.case_name" placeholder="请输入用例名称" />
      </el-form-item>

      <el-form-item label="URL：" prop="base_url">
        <el-input v-model="formData.base_url" placeholder="请输入URL" />
      </el-form-item>

      <el-form-item label="操作步骤：" prop="steps">
        <div class="simple-steps-container">
          <div
            v-for="(step, index) in formData.steps"
            :key="index"
            class="simple-step-item"
          >
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
                :disabled="formData.steps.length <= 1"
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
        <el-checkbox v-model="formData.record">启用录制功能</el-checkbox>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { getValuePlaceholder, testCaseRules } from '@/utils/uiTestUtils'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  editingData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

const visible = ref(false)
const formRef = ref()
const isEditing = ref(false)

const formData = reactive({
  case_name: '',
  base_url: '',
  steps: [],
  record: false
})

const rules = testCaseRules

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.editingData) {
    isEditing.value = true
    Object.assign(formData, {
      case_name: props.editingData.case_name || '',
      base_url: props.editingData.base_url || '',
      record: props.editingData.record || false,
      steps: props.editingData.steps ? JSON.parse(JSON.stringify(props.editingData.steps)) : []
    })
  } else if (val) {
    isEditing.value = false
    resetForm()
  }
})

// 步骤管理
const addStep = () => {
  formData.steps.push({
    action: '',
    selector: '',
    value: ''
  })
}

const removeStep = (index) => {
  if (formData.steps.length > 1) {
    formData.steps.splice(index, 1)
  }
}

const onStepActionChange = (step) => {
  if (step.action === 'goto') {
    step.selector = ''
  } else if (step.action === 'click' || step.action === 'waitForSelector') {
    step.value = ''
  }
}

const resetForm = () => {
  Object.assign(formData, {
    case_name: '',
    base_url: '',
    steps: [{ action: '', selector: '', value: '' }],
    record: false
  })
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const handleClose = () => {
  emit('update:modelValue', false)
  resetForm()
}

const handleCancel = () => {
  emit('cancel')
  handleClose()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    emit('submit', { ...formData, isEditing: isEditing.value })
    handleClose()
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}
</script>

<style scoped>
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

/* 响应式调整 */
@media (max-width: 768px) {
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
}
</style>