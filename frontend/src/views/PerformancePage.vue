<template>
  <div class="performance-container">
    <div class="page-header">
      <el-button @click="$router.push('/projects')" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回项目
      </el-button>
      <h2 class="page-title">性能测试</h2>
      <div style="width: 120px"></div> <!-- 占位保持对称 -->
    </div>
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button type="primary" @click="showTestConfigDialog = true">
            <el-icon><Plus /></el-icon>
            创建性能测试
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 测试配置 -->
        <el-tab-pane label="测试配置" name="config">
          <el-table :data="testConfigs" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="配置名称" />
            <el-table-column prop="users" label="用户数" />
            <el-table-column prop="spawn_rate" label="孵化率" />
            <el-table-column prop="run_time" label="运行时间" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="runTest(scope.row)">运行</el-button>
                <el-button size="small" type="danger" @click="deleteConfig(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
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
      </el-tabs>
    </el-card>

    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button @click="$router.push('/projects')">返回项目</el-button>
    </div>

    <!-- 创建测试配置对话框 -->
    <el-dialog title="创建性能测试配置" v-model="showTestConfigDialog" width="600px">
      <el-form :model="testConfigForm" :rules="testConfigRules" ref="testConfigFormRef">
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="testConfigForm.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="目标URL" prop="host">
          <el-input v-model="testConfigForm.host" placeholder="http://example.com" />
        </el-form-item>
        <el-form-item label="用户数" prop="users">
          <el-input-number v-model="testConfigForm.users" :min="1" :max="10000" />
        </el-form-item>
        <el-form-item label="孵化率" prop="spawn_rate">
          <el-input-number v-model="testConfigForm.spawn_rate" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="运行时间" prop="run_time">
          <el-input v-model="testConfigForm.run_time" placeholder="例如: 1m, 5m, 1h" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTestConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="handleTestConfigSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus,ArrowLeft } from '@element-plus/icons-vue'
import { performanceAPI } from '../api/performance'

const route = useRoute()
const projectId = ref(route.query.projectId || 1)

const activeTab = ref('config')
const loading = ref(false)
const showTestConfigDialog = ref(false)
const testConfigFormRef = ref()

const testConfigs = ref([])
const testReports = ref([])

const testConfigForm = reactive({
  name: '',
  host: '',
  users: 10,
  spawn_rate: 2,
  run_time: '1m'
})

const testConfigRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' }
  ],
  host: [
    { required: true, message: '请输入目标URL', trigger: 'blur' }
  ],
  users: [
    { required: true, message: '请输入用户数', trigger: 'blur' }
  ]
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

const fetchTestConfigs = async () => {
  loading.value = true
  try {
    // 这里应该调用获取性能测试配置的API，暂时用模拟数据
    testConfigs.value = [
      { id: 1, name: '基础压力测试', users: 100, spawn_rate: 10, run_time: '5m' },
      { id: 2, name: '高负载测试', users: 1000, spawn_rate: 50, run_time: '10m' }
    ]
  } catch (error) {
    ElMessage.error('获取测试配置失败')
  } finally {
    loading.value = false
  }
}

const fetchTestReports = async () => {
  try {
    const response = await performanceAPI.getPerformanceReports(projectId.value)
    testReports.value = response.data
  } catch (error) {
    ElMessage.error('获取测试报告失败')
  }
}

const runTest = async (config) => {
  try {
    await performanceAPI.runPerformanceTest(projectId.value, config)
    ElMessage.success('性能测试已开始运行')
    setTimeout(fetchTestReports, 2000)
  } catch (error) {
    ElMessage.error('运行性能测试失败')
  }
}

const deleteConfig = async (config) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试配置 "${config.name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 调用删除配置的API
    ElMessage.success('测试配置删除成功')
    fetchTestConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除测试配置失败')
    }
  }
}

const viewReport = (report) => {
  // 在新窗口中打开报告
  window.open(`http://localhost:8000/reports/${report.report_path}`, '_blank')
}

const handleTestConfigSubmit = async () => {
  if (!testConfigFormRef.value) return

  testConfigFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 调用创建性能测试配置的API
        // await performanceAPI.createPerformanceTest(projectId.value, testConfigForm)
        ElMessage.success('测试配置创建成功')
        showTestConfigDialog.value = false
        resetTestConfigForm()
        fetchTestConfigs()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '创建测试配置失败')
      }
    }
  })
}

const resetTestConfigForm = () => {
  testConfigForm.name = ''
  testConfigForm.host = ''
  testConfigForm.users = 10
  testConfigForm.spawn_rate = 2
  testConfigForm.run_time = '1m'
}

onMounted(() => {
  fetchTestConfigs()
  fetchTestReports()
})
</script>

<style scoped>
.performance-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
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
}

/* 响应式调整 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .page-title {
    order: -1; /* 标题移到最前面 */
  }

  .back-button {
    align-self: flex-start;
  }
}
</style>