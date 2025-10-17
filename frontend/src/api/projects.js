import api from './index'

export const projectsAPI = {
  // 获取所有项目
  getProjects() {
    return api.get('/projects')
  },

  // 创建项目
  createProject(projectData) {
    return api.post('/projects', projectData)
  },

  // 获取项目详情
  getProject(projectId) {
    return api.get(`/projects/${projectId}`)
  },

  // 更新项目
  updateProject(projectId, projectData) {
    return api.put(`/projects/${projectId}`, projectData)
  },

  // 删除项目
  deleteProject(projectId) {
    return api.delete(`/projects/${projectId}`)
  }
}

export default projectsAPI