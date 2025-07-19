<template>
  <div class="projects">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>项目管理</h2>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>项目列表</span>
              <el-button type="primary" @click="showCreateDialog = true">
                <el-icon><Plus /></el-icon>
                新增项目
              </el-button>
            </div>
          </template>
          
          <el-table :data="projects" style="width: 100%">
            <el-table-column prop="name" label="项目名称" />
            <el-table-column prop="type" label="类型" />
            <el-table-column prop="url" label="仓库地址" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
                  {{ scope.row.status === 'active' ? '活跃' : '暂停' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间">
              <template #default="scope">
                {{ formatTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button size="small" @click="editProject(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteProject(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 创建项目对话框 -->
    <el-dialog v-model="showCreateDialog" title="新增项目" width="500px">
      <el-form :model="newProject" label-width="100px">
        <el-form-item label="项目名称">
          <el-input v-model="newProject.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目类型">
          <el-select v-model="newProject.type" placeholder="请选择项目类型">
            <el-option label="GitHub" value="github" />
            <el-option label="GitLab" value="gitlab" />
            <el-option label="Bitbucket" value="bitbucket" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库地址">
          <el-input v-model="newProject.url" placeholder="请输入仓库地址" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newProject.description" type="textarea" placeholder="请输入项目描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createProject">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Projects',
  components: {
    Plus
  },
  setup() {
    const projects = ref([])
    const showCreateDialog = ref(false)
    const newProject = ref({
      name: '',
      type: '',
      url: '',
      description: ''
    })
    
    const loadProjects = async () => {
      // TODO: 调用 API 获取项目列表
      projects.value = [
        {
          id: 1,
          name: 'Vue Project',
          type: 'github',
          url: 'https://github.com/user/vue-project',
          status: 'active',
          created_at: new Date()
        },
        {
          id: 2,
          name: 'React Project',
          type: 'github',
          url: 'https://github.com/user/react-project',
          status: 'inactive',
          created_at: new Date()
        }
      ]
    }
    
    const createProject = async () => {
      if (!newProject.value.name || !newProject.value.type || !newProject.value.url) {
        ElMessage.error('请填写必要信息')
        return
      }
      
      // TODO: 调用 API 创建项目
      const project = {
        ...newProject.value,
        id: Date.now(),
        status: 'active',
        created_at: new Date()
      }
      
      projects.value.push(project)
      showCreateDialog.value = false
      newProject.value = {
        name: '',
        type: '',
        url: '',
        description: ''
      }
      ElMessage.success('项目创建成功')
    }
    
    const editProject = (project) => {
      // TODO: 实现编辑功能
      ElMessage.info('编辑功能待实现')
    }
    
    const deleteProject = (project) => {
      // TODO: 调用 API 删除项目
      const index = projects.value.findIndex(p => p.id === project.id)
      if (index > -1) {
        projects.value.splice(index, 1)
        ElMessage.success('项目删除成功')
      }
    }
    
    const formatTime = (time) => {
      return new Date(time).toLocaleString()
    }
    
    onMounted(() => {
      loadProjects()
    })
    
    return {
      projects,
      showCreateDialog,
      newProject,
      createProject,
      editProject,
      deleteProject,
      formatTime
    }
  }
}
</script>

<style scoped>
.projects {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 