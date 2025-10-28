<template>
  <el-dialog v-model="visible" title="保存测试用例" width="500px" :before-close="close">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
      <el-form-item label="用例名称" prop="case_name">
        <el-input
          v-model="form.case_name"
          placeholder="输入测试用例名称"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="项目ID">
        <el-input v-model="form.project_id" disabled />
      </el-form-item>
      <el-form-item label="请求信息">
        <div class="request-preview">
          <div><strong>方法:</strong> {{ currentRequest.method }}</div>
          <div><strong>URL:</strong> {{ currentRequest.url }}</div>
          <div><strong>Headers:</strong> {{ headersCount }} 个</div>
          <div><strong>参数:</strong> {{ paramsCount }} 个</div>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button @click="save" type="primary" :loading="saving">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { apiTestsAPI } from '@/api/apiTests'
import { buildRequestData, validateJson } from '@/utils/apiTestUtils'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: [String, Number],
    required: true
  },
  currentRequest: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const formRef = ref()
const visible = ref(false)
const saving = ref(false)

const form = reactive({
  case_name: '',
  project_id: props.projectId
})

const rules = {
  case_name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' },
    { min: 1, max: 100, message: '用例名称长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const headersCount = computed(() => {
  return props.currentRequest.headers.filter(h => h.key && h.value).length
})

const paramsCount = computed(() => {
  return props.currentRequest.params.filter(p => p.key && p.value).length
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    form.project_id = props.projectId
    // 自动生成用例名称
    if (!form.case_name && props.currentRequest.url) {
      const url = new URL(props.currentRequest.url.startsWith('http') ? props.currentRequest.url : 'https://' + props.currentRequest.url)
      form.case_name = `${props.currentRequest.method} ${url.pathname}`
    }
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const close = () => {
  visible.value = false
  formRef.value?.resetFields()
  form.case_name = ''
  saving.value = false
}

const save = async () => {
  if (!formRef.value) return

  // 验证JSON格式
  if (props.currentRequest.bodyType === 'json' && props.currentRequest.body) {
    if (!validateJson(props.currentRequest.body)) {
      ElMessage.error('请求体JSON格式错误，请检查后重试')
      return
    }
  }

  if (props.currentRequest.expected_data) {
    if (!validateJson(props.currentRequest.expected_data)) {
      ElMessage.error('预期结果JSON格式错误，请检查后重试')
      return
    }
  }

  formRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const requestData = buildRequestData(props.currentRequest, form.case_name)
        requestData.project_id = parseInt(props.projectId)

        console.log('保存测试用例:', requestData)

        await apiTestsAPI.createApiTestCase(props.projectId, requestData)
        ElMessage.success('保存成功')
        close()
        emit('saved')
      } catch (error) {
        console.error('保存失败:', error)
        ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        saving.value = false
      }
    }
  })
}
</script>

<style scoped>
.request-preview {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
}

.request-preview div {
  margin-bottom: 5px;
}
</style>