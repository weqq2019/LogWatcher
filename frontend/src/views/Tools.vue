<template>
  <div class="tools">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>工具</h2>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据采集器管理</span>
            </div>
          </template>
          
          <div class="tool-content">
            <el-table :data="collectors" style="width: 100%">
              <el-table-column prop="name" label="采集器名称" />
              <el-table-column prop="type" label="类型" />
              <el-table-column prop="status" label="状态">
                <template #default="scope">
                  <el-switch
                    v-model="scope.row.status"
                    :active-value="true"
                    :inactive-value="false"
                    @change="toggleCollector(scope.row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button size="small" @click="configureCollector(scope.row)">配置</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统监控</span>
            </div>
          </template>
          
          <div class="tool-content">
            <div class="monitor-item">
              <span>CPU 使用率:</span>
              <el-progress :percentage="systemInfo.cpu" />
            </div>
            <div class="monitor-item">
              <span>内存使用率:</span>
              <el-progress :percentage="systemInfo.memory" />
            </div>
            <div class="monitor-item">
              <span>磁盘使用率:</span>
              <el-progress :percentage="systemInfo.disk" />
            </div>
            <div class="monitor-item">
              <span>网络状态:</span>
              <el-tag :type="systemInfo.network ? 'success' : 'danger'">
                {{ systemInfo.network ? '正常' : '异常' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据库管理</span>
            </div>
          </template>
          
          <div class="tool-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-statistic title="数据库连接数" :value="dbInfo.connections" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="数据表数量" :value="dbInfo.tables" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="数据总量" :value="dbInfo.records" suffix="条" />
              </el-col>
            </el-row>
            
            <div style="margin-top: 20px;">
              <el-button type="primary" @click="backupDatabase">
                <el-icon><Download /></el-icon>
                备份数据库
              </el-button>
              <el-button type="warning" @click="optimizeDatabase">
                <el-icon><Tools /></el-icon>
                优化数据库
              </el-button>
              <el-button type="danger" @click="clearCache">
                <el-icon><Delete /></el-icon>
                清理缓存
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 配置对话框 -->
    <el-dialog v-model="showConfigDialog" title="采集器配置" width="600px">
      <div v-if="selectedCollector">
        <el-form :model="collectorConfig" label-width="120px">
          <el-form-item label="采集器名称">
            <el-input v-model="collectorConfig.name" disabled />
          </el-form-item>
          <el-form-item label="采集频率">
            <el-select v-model="collectorConfig.frequency" placeholder="请选择采集频率">
              <el-option label="每分钟" value="1m" />
              <el-option label="每5分钟" value="5m" />
              <el-option label="每小时" value="1h" />
              <el-option label="每天" value="1d" />
            </el-select>
          </el-form-item>
          <el-form-item label="目标URL">
            <el-input v-model="collectorConfig.url" placeholder="请输入目标URL" />
          </el-form-item>
          <el-form-item label="关键词">
            <el-input v-model="collectorConfig.keywords" placeholder="请输入关键词，多个用逗号分隔" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCollectorConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Download, Tools, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Tools',
  components: {
    Download,
    Tools,
    Delete
  },
  setup() {
    const collectors = ref([])
    const systemInfo = ref({
      cpu: 45,
      memory: 67,
      disk: 82,
      network: true
    })
    const dbInfo = ref({
      connections: 15,
      tables: 8,
      records: 15420
    })
    const showConfigDialog = ref(false)
    const selectedCollector = ref(null)
    const collectorConfig = ref({
      name: '',
      frequency: '',
      url: '',
      keywords: ''
    })
    
    const loadCollectors = async () => {
      // TODO: 调用 API 获取采集器列表
      collectors.value = [
        { id: 1, name: 'GitHub 采集器', type: 'github', status: true },
        { id: 2, name: 'RSS 采集器', type: 'rss', status: false },
        { id: 3, name: 'Twitter 采集器', type: 'twitter', status: true }
      ]
    }
    
    const loadSystemInfo = async () => {
      // TODO: 调用 API 获取系统信息
      setInterval(() => {
        systemInfo.value.cpu = Math.floor(Math.random() * 100)
        systemInfo.value.memory = Math.floor(Math.random() * 100)
        systemInfo.value.disk = Math.floor(Math.random() * 100)
      }, 5000)
    }
    
    const loadDbInfo = async () => {
      // TODO: 调用 API 获取数据库信息
    }
    
    const toggleCollector = async (collector) => {
      // TODO: 调用 API 切换采集器状态
      ElMessage.success(`${collector.name} 已${collector.status ? '启用' : '禁用'}`)
    }
    
    const configureCollector = (collector) => {
      selectedCollector.value = collector
      collectorConfig.value = {
        name: collector.name,
        frequency: '1h',
        url: '',
        keywords: ''
      }
      showConfigDialog.value = true
    }
    
    const saveCollectorConfig = async () => {
      // TODO: 调用 API 保存采集器配置
      showConfigDialog.value = false
      ElMessage.success('采集器配置保存成功')
    }
    
    const backupDatabase = async () => {
      // TODO: 调用 API 备份数据库
      ElMessage.success('数据库备份已开始')
    }
    
    const optimizeDatabase = async () => {
      // TODO: 调用 API 优化数据库
      ElMessage.success('数据库优化已完成')
    }
    
    const clearCache = async () => {
      // TODO: 调用 API 清理缓存
      ElMessage.success('缓存清理已完成')
    }
    
    onMounted(() => {
      loadCollectors()
      loadSystemInfo()
      loadDbInfo()
    })
    
    return {
      collectors,
      systemInfo,
      dbInfo,
      showConfigDialog,
      selectedCollector,
      collectorConfig,
      toggleCollector,
      configureCollector,
      saveCollectorConfig,
      backupDatabase,
      optimizeDatabase,
      clearCache
    }
  }
}
</script>

<style scoped>
.tools {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tool-content {
  padding: 10px 0;
}

.monitor-item {
  margin-bottom: 20px;
}

.monitor-item span {
  display: inline-block;
  width: 100px;
  margin-bottom: 10px;
}
</style> 