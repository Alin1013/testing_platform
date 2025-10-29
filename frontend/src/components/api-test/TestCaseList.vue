<template>
  <div class="test-cases-sidebar">
    <div class="sidebar-header">
      <h3>测试用例列表</h3>
      <div class="header-actions">
        <el-button @click="$emit('refresh')" size="small" type="primary">
          刷新
        </el-button>
        <el-button @click="showAddDialog = true" size="small" type="success">
          添加用例
        </el-button>
      </div>
    </div>
    <div class="test-cases-list">
      <div
        v-for="testCase in testCases"
        :key="testCase.id"
        class="test-case-item"
        :class="{ active: selectedTestCase?.id === testCase.id }"
        @click="$emit('select', testCase)"
      >
        <div class="case-method" :class="getMethodClass(testCase.method)">
          {{ testCase.method }}
        </div>
        <div class="case-info">
          <div class="case-name">{{ testCase.case_name ||testCase.name }}</div>
          <div class="case-url">{{ testCase.url }}</div>
        </div>
        <div class="case-actions">
          <el-button
            @click.stop="handleDelete(testCase.id)"
            size="small"
            type="danger"
            text
          >
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 添加测试用例对话框 -->
    <el-dialog v-model="showAddDialog" title="添加测试用例" width="500px">
      <el-form :model="newTestCaseForm" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="用例名称" prop="case_name">
          <el-input
            v-model="newTestCaseForm.case_name"
            placeholder="输入测试用例名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="请求URL" prop="url">
          <el-input
            v-model="newTestCaseForm.url"
            placeholder="输入请求URL，例如: https://api.example.com/users"
          />
        </el-form-item>
        <el-form-item label="请求方法" prop="method">
          <el-select v-model="newTestCaseForm.method" placeholder="选择请求方法">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button @click="saveNewTestCase" type="primary" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getMethodClass } from '@/utils/apiTestUtils'

const props = defineProps({
  testCases: {
    type: Array,
    default: () => []
  },
  selectedTestCase: {
    type: Object,
    default: null
  },
  projectId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['refresh', 'select', 'delete', 'add'])

// 添加测试用例相关
const showAddDialog = ref(false)
const saving = ref(false)
const formRef = ref()

const newTestCaseForm = reactive({
  case_name: '',
  url: '',
  method: 'GET'
})

const formRules = {
  case_name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' },
    { min: 1, max: 100, message: '用例名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入请求URL', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ]
}

// 添加删除处理方法
const handleDelete = (testCaseId) => {
  emit('delete', testCaseId)
}

// 保存新测试用例
const saveNewTestCase = async () => {
  if (!formRef.value) return

  formRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        // 构建测试用例数据
        const testCaseData = {
          case_name: newTestCaseForm.case_name,
          url: newTestCaseForm.url,
          method: newTestCaseForm.method,
          project_id: props.projectId,
          headers: [],
          params: [],
          body: '',
          bodyType: 'json',
          formData: [],
          rawBody: '',
          expected_data: ''
        }

        // 触发添加事件
        emit('add', testCaseData)

        ElMessage.success('测试用例添加成功')
        showAddDialog.value = false
        resetForm()
      } catch (error) {
        ElMessage.error('添加失败: ' + error.message)
      } finally {
        saving.value = false
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  newTestCaseForm.case_name = ''
  newTestCaseForm.url = ''
  newTestCaseForm.method = 'GET'
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.test-cases-sidebar {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #e6e8eb;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.test-cases-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.test-case-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e6e8eb;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.test-case-item:hover {
  border-color: #409eff;
}

.test-case-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.case-method {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
  margin-right: 10px;
  min-width: 50px;
  text-align: center;
}

.method-get { background: #67c23a; }
.method-post { background: #409eff; }
.method-put { background: #e6a23c; }
.method-patch { background: #909399; }
.method-delete { background: #f56c6c; }
.method-default { background: #909399; }

.case-info {
  flex: 1;
  min-width: 0;
}

.case-name {
  font-weight: 600;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.case-url {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.case-actions {
  margin-left: 10px;
}
</style>