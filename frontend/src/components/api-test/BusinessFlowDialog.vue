<template>
  <el-dialog v-model="visible" title="创建业务流程" width="600px">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="流程名称" prop="flow_name">
        <el-input v-model="form.flow_name" placeholder="输入业务流程名称" />
      </el-form-item>
      <el-form-item label="测试类型" prop="test_type">
        <el-select v-model="form.test_type" placeholder="选择测试类型">
          <el-option label="API测试" value="api" />
          <el-option label="UI测试" value="ui" />
        </el-select>
      </el-form-item>
      <el-form-item label="选择用例" prop="case_ids">
        <el-select v-model="form.case_ids" multiple placeholder="选择测试用例">
          <el-option
            v-for="testCase in testCases"
            :key="testCase.id"
            :label="testCase.case_name"
            :value="testCase.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button @click="create" type="primary">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { apiTestsAPI } from '@/api/apiTests'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: [String, Number],
    required: true
  },
  testCases: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'created'])

const formRef = ref()
const visible = ref(false)

const form = reactive({
  flow_name: '',
  test_type: 'api',
  case_ids: [],
  project_id: props.projectId
})

const rules = {
  flow_name: [
    { required: true, message: '请输入流程名称', trigger: 'blur' }
  ],
  test_type: [
    { required: true, message: '请选择测试类型', trigger: 'change' }
  ],
  case_ids: [
    { required: true, message: '请选择测试用例', trigger: 'change' }
  ]
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    form.project_id = props.projectId
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const close = () => {
  visible.value = false
  formRef.value?.resetFields()
  form.case_ids = []
}

const create = async () => {
  if (!formRef.value) return

  formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await apiTestsAPI.createBusinessFlow(props.projectId, form)
        ElMessage.success('业务流程创建成功')
        close()
        emit('created')
      } catch (error) {
        ElMessage.error('创建失败: ' + error.message)
      }
    }
  })
}
</script>