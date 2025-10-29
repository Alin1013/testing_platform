<template>
  <el-dialog
    title="创建业务流程"
    v-model="visible"
    width="500px"
    @closed="handleClose"
  >
    <el-form
      :model="formData"
      :rules="rules"
      ref="formRef"
      label-width="100px"
    >
      <el-form-item label="流程名称：" prop="flow_name">
        <el-input v-model="formData.flow_name" placeholder="请输入流程名称" />
      </el-form-item>
      <el-form-item label="选择用例：" prop="case_ids">
        <el-select
          v-model="formData.case_ids"
          multiple
          placeholder="请选择测试用例"
          style="width: 100%"
        >
          <el-option
            v-for="testcase in testCases"
            :key="testcase.id"
            :label="testcase.case_name"
            :value="testcase.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { businessFlowRules } from '@/utils/uiTestUtils'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  testCases: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

const visible = ref(false)
const formRef = ref()

const formData = reactive({
  flow_name: '',
  case_ids: []
})

const rules = businessFlowRules

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    resetForm()
  }
})

const resetForm = () => {
  Object.assign(formData, {
    flow_name: '',
    case_ids: []
  })
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const handleClose = () => {
  emit('update:modelValue', false)
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

    emit('submit', { ...formData })
    handleClose()
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}
</script>