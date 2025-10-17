<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <h2>欢迎使用测试平台</h2>
        </div>
      </template>

      <div class="welcome-content">
        <el-empty v-if="projects.length === 0" description="暂无项目">
          <el-button type="primary" @click="$router.push('/projects')">创建项目</el-button>
        </el-empty>

        <div v-else class="projects-grid">
          <el-card
            v-for="project in projects"
            :key="project.id"
            class="project-card"
            @click="goToProject(project)"
          >
            <template #header>
              <div class="project-header">
                <h3>{{ project.project_name }}</h3>
                <el-tag :type="getTestStyleType(project.test_style)">
                  {{ getTestStyleName(project.test_style) }}
                </el-tag>
              </div>
            </template>
            <div class="project-info">
              <p>创建时间: {{ formatDate(project.created_at) }}</p>
            </div>
          </el-card>

          <el-card class="project-card add-project" @click="$router.push('/projects')">
            <div class="add-project-content">
              <el-icon size="48"><Plus /></el-icon>
              <p>添加新项目</p>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { projectsAPI } from '../api/projects'

const router = useRouter()
const projects = ref([])

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

const goToProject = (project) => {
  switch (project.test_style) {
    case 'api':
      router.push('/api-test')
      break
    case 'ui':
      router.push('/ui-test')
      break
    case 'performance':
      router.push('/performance')
      break
    default:
      ElMessage.warning('未知的项目类型')
  }
}

const fetchProjects = async () => {
  try {
    const response = await projectsAPI.getProjects()
    projects.value = response.data
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  }
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  min-height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-content {
  margin-top: 20px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.project-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-info {
  color: #666;
}

.add-project {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #dcdfe6;
  background-color: #fafafa;
}

.add-project-content {
  text-align: center;
  color: #909399;
}

.add-project:hover {
  border-color: #409eff;
  color: #409eff;
}
</style>