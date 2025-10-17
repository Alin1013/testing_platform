<template>
  <div class="projects-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>项目管理</h2>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建项目
          </el-button>
        </div>
      </template>

      <el-table :data="projects" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="project_name" label="项目名称" />
        <el-table-column prop="test_style" label="测试类型">
          <template #default="scope">
            <el-tag :type="getTestStyleType(scope.row.test_style)">
              {{ getTestStyleName(scope.row.test_style) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editProject(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteProject(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      :title="isEditing ? '编辑项目' : '创建项目'"
      v-model="showCreateDialog"
      width="500px"
    >
      <el-form :model="projectForm" :rules="projectRules" ref="projectFormRef">
        <el-form-item label="项目名称" prop="project_name">
          <el-input v-model="projectForm.project_name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="测试类型" prop="test_style">
          <el-select v-model="projectForm.test_style" placeholder="请选择测试类型" style="width: 100%">
            <el-option label="接口测试" value="api" />
            <el-option label="UI测试" value="ui" />
            <el-option label="性能测试" value="performance" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleProjectSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { projectsAPI } from '../api/projects'

const projects = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const isEditing = ref(false)
const projectFormRef = ref()
const editingProjectId = ref(null)

const projectForm = reactive({
  project_name: '',
  test_style: ''
})

const projectRules = {
  project_name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ],
  test_style: [
    { required: true, message: '请选择测试类型', trigger: 'change' }
  ]
}

const getTestStyleType = (style) => {
  const types = {
    'api': 'primary',
    'ui': 'success',
    'performance': 'warning'
  }
  return types[style] || 'info'
}

const getTestStyleName = (style) => {
  const names = {
    'api': '接口测试',
    'ui': 'UI测试',
    'performance': '性能测试'
  }
  return names[style] || '未知类型'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const fetchProjects = async () => {
  loading.value = true
  try {
    const response = await projectsAPI.getProjects()
    projects.value = response.data
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

const editProject = (project) => {
  isEditing.value = true
  editingProjectId.value = project.id
  projectForm.project_name = project.project_name
  projectForm.test_style = project.test_style
  showCreateDialog.value = true
}

const deleteProject = async (project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${project.project_name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await projectsAPI.deleteProject(project.id)
    ElMessage.success('项目删除成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除项目失败')
    }
  }
}

const handleProjectSubmit = async () => {
  if (!projectFormRef.value) return

  projectFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditing.value) {
          await projectsAPI.updateProject(editingProjectId.value, projectForm)
          ElMessage.success('项目更新成功')
        } else {
          await projectsAPI.createProject(projectForm)
          ElMessage.success('项目创建成功')
        }

        showCreateDialog.value = false
        resetForm()
        fetchProjects()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      }
    }
  })
}

const resetForm = () => {
  projectForm.project_name = ''
  projectForm.test_style = ''
  isEditing.value = false
  editingProjectId.value = null
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.projects-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>