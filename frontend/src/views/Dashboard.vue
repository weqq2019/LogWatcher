<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="dashboard-header">
          <h2>📊 系统概览</h2>
          <div class="last-update">
            上次更新: {{ formatTime(new Date()) }}
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 主要统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card stat-projects">
          <div class="stat-content">
            <div class="stat-icon">📁</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalProjects }}</div>
              <div class="stat-label">项目总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card stat-collectors">
          <div class="stat-content">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.activeCollectors }}</div>
              <div class="stat-label">活跃收集器</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card stat-news">
          <div class="stat-content">
            <div class="stat-icon">📰</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.todayNews }}</div>
              <div class="stat-label">今日新闻</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card stat-total">
          <div class="stat-content">
            <div class="stat-icon">🗂️</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalNews }}</div>
              <div class="stat-label">新闻总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 次要统计信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card class="mini-stat-card">
          <div class="mini-stat-content">
            <div class="mini-stat-icon">🎯</div>
            <div class="mini-stat-info">
              <div class="mini-stat-number">{{ stats.cursorUpdates }}</div>
              <div class="mini-stat-label">Cursor 更新</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="mini-stat-card">
          <div class="mini-stat-content">
            <div class="mini-stat-icon">📈</div>
            <div class="mini-stat-info">
              <div class="mini-stat-number">{{ stats.weeklyGrowth }}%</div>
              <div class="mini-stat-label">本周增长</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="mini-stat-card">
          <div class="mini-stat-content">
            <div class="mini-stat-icon">⏱️</div>
            <div class="mini-stat-info">
              <div class="mini-stat-number">{{ stats.avgResponseTime }}ms</div>
              <div class="mini-stat-label">平均响应时间</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 主要内容区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📂 最近项目</span>
              <el-button type="primary" size="small" @click="$router.push('/projects')">
                查看全部
              </el-button>
            </div>
          </template>
          <div class="recent-projects">
            <el-empty v-if="!recentProjects.length" description="暂无项目" />
            <div v-for="project in recentProjects" :key="project.id" class="project-item">
              <div class="project-icon">📁</div>
              <div class="project-info">
                <div class="project-name">{{ project.name }}</div>
                <div class="project-desc">{{ project.description }}</div>
              </div>
              <div class="project-actions">
                <el-tag 
                  :type="project.status === 'active' ? 'success' : 'info'" 
                  size="small"
                >
                  {{ project.status === 'active' ? '活跃' : '暂停' }}
                </el-tag>
                <div class="project-time">{{ formatTime(project.updated_at) }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📰 最新新闻</span>
              <el-button type="primary" size="small" @click="$router.push('/news')">
                查看全部
              </el-button>
            </div>
          </template>
          <div class="recent-news">
            <el-empty v-if="!recentNews.length" description="暂无新闻" />
            <div v-for="news in recentNews" :key="news.id" class="news-item">
              <div class="news-icon">📰</div>
              <div class="news-content">
                <div class="news-title">{{ news.title }}</div>
                <div class="news-meta">
                  <span class="news-source">{{ news.source }}</span>
                  <span class="news-time">{{ formatTime(news.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统状态和快捷操作 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🔧 系统状态</span>
            </div>
          </template>
          <div class="system-status">
            <div class="status-item">
              <span class="status-label">数据库连接</span>
              <el-tag type="success" size="small">正常</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">RSS 收集器</span>
              <el-tag type="success" size="small">运行中</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">GitHub 收集器</span>
              <el-tag type="success" size="small">运行中</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">Cursor 收集器</span>
              <el-tag type="success" size="small">运行中</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🚀 快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button 
              type="primary" 
              icon="Plus" 
              @click="$router.push('/projects')"
            >
              添加项目
            </el-button>
            <el-button 
              type="success" 
              icon="Refresh" 
              @click="refreshData"
            >
              刷新数据
            </el-button>
            <el-button 
              type="info" 
              icon="View" 
              @click="$router.push('/news')"
            >
              查看新闻
            </el-button>
            <el-button 
              type="warning" 
              icon="Tools" 
              @click="$router.push('/cursor')"
            >
              Cursor 更新
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Dashboard',
  setup() {
    const stats = ref({
      totalProjects: 0,
      activeCollectors: 0,
      todayNews: 0,
      totalNews: 0,
      cursorUpdates: 0,
      weeklyGrowth: 0,
      avgResponseTime: 0
    })
    
    const recentProjects = ref([])
    const recentNews = ref([])
    
    const loadStats = async () => {
      // 模拟API调用
      stats.value = {
        totalProjects: 5,
        activeCollectors: 3,
        todayNews: 24,
        totalNews: 1580,
        cursorUpdates: 12,
        weeklyGrowth: 15.6,
        avgResponseTime: 245
      }
    }
    
    const loadRecentProjects = async () => {
      // 模拟API调用
      recentProjects.value = [
        { 
          id: 1, 
          name: 'Vue Project', 
          description: '基于Vue 3的前端项目',
          status: 'active',
          updated_at: new Date(Date.now() - 1000 * 60 * 30) // 30分钟前
        },
        { 
          id: 2, 
          name: 'React Project', 
          description: '企业级React应用',
          status: 'inactive',
          updated_at: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2小时前
        },
        { 
          id: 3, 
          name: 'Angular Project', 
          description: '现代化Angular框架',
          status: 'active',
          updated_at: new Date(Date.now() - 1000 * 60 * 60 * 6) // 6小时前
        },
        { 
          id: 4, 
          name: 'Node.js API', 
          description: '后端API服务',
          status: 'active',
          updated_at: new Date(Date.now() - 1000 * 60 * 60 * 12) // 12小时前
        }
      ]
    }
    
    const loadRecentNews = async () => {
      // 模拟API调用
      recentNews.value = [
        { 
          id: 1, 
          title: 'Vue 3.4 发布', 
          source: 'Vue.js官方',
          created_at: new Date(Date.now() - 1000 * 60 * 15) // 15分钟前
        },
        { 
          id: 2, 
          title: 'React 18 新特性', 
          source: 'React团队',
          created_at: new Date(Date.now() - 1000 * 60 * 45) // 45分钟前
        },
        { 
          id: 3, 
          title: 'JavaScript 新标准', 
          source: 'MDN Web Docs',
          created_at: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2小时前
        },
        { 
          id: 4, 
          title: 'TypeScript 5.0 更新', 
          source: 'TypeScript官方',
          created_at: new Date(Date.now() - 1000 * 60 * 60 * 4) // 4小时前
        },
        { 
          id: 5, 
          title: 'Node.js 20 LTS', 
          source: 'Node.js基金会',
          created_at: new Date(Date.now() - 1000 * 60 * 60 * 8) // 8小时前
        }
      ]
    }
    
    const formatTime = (time) => {
      const now = new Date()
      const diff = now - new Date(time)
      const minutes = Math.floor(diff / (1000 * 60))
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      
      if (minutes < 60) {
        return `${minutes}分钟前`
      } else if (hours < 24) {
        return `${hours}小时前`
      } else if (days < 7) {
        return `${days}天前`
      } else {
        return new Date(time).toLocaleDateString()
      }
    }
    
    const refreshData = () => {
      loadStats()
      loadRecentProjects()
      loadRecentNews()
      // 显示刷新成功消息
      // ElMessage.success('数据已刷新')
    }
    
    onMounted(() => {
      loadStats()
      loadRecentProjects()
      loadRecentNews()
    })
    
    return {
      stats,
      recentProjects,
      recentNews,
      formatTime,
      refreshData
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background-color: #f8f9fa;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-header h2 {
  margin: 0;
  color: #2c3e50;
}

.last-update {
  color: #6c757d;
  font-size: 14px;
}

/* 主要统计卡片样式 */
.stat-card {
  text-align: left;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  font-size: 3em;
  margin-right: 20px;
  width: 60px;
  text-align: center;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 2.5em;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
}

/* 不同类型的统计卡片颜色 */
.stat-projects .stat-icon { opacity: 0.8; }
.stat-collectors .stat-icon { opacity: 0.8; }
.stat-news .stat-icon { opacity: 0.8; }
.stat-total .stat-icon { opacity: 0.8; }

/* 迷你统计卡片 */
.mini-stat-card {
  border: none;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
}

.mini-stat-content {
  display: flex;
  align-items: center;
  padding: 15px;
}

.mini-stat-icon {
  font-size: 1.5em;
  margin-right: 12px;
  width: 30px;
  text-align: center;
}

.mini-stat-number {
  font-size: 1.2em;
  font-weight: bold;
  color: #2c3e50;
}

.mini-stat-label {
  color: #6c757d;
  font-size: 12px;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #2c3e50;
}

/* 项目列表样式 */
.recent-projects {
  max-height: 400px;
  overflow-y: auto;
}

.project-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  transition: background-color 0.3s;
}

.project-item:last-child {
  border-bottom: none;
}

.project-item:hover {
  background-color: #f8f9fa;
}

.project-icon {
  font-size: 1.5em;
  margin-right: 15px;
  width: 30px;
  text-align: center;
}

.project-info {
  flex: 1;
}

.project-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.project-desc {
  color: #6c757d;
  font-size: 13px;
}

.project-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.project-time {
  color: #999;
  font-size: 12px;
}

/* 新闻列表样式 */
.recent-news {
  max-height: 400px;
  overflow-y: auto;
}

.news-item {
  display: flex;
  align-items: flex-start;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  transition: background-color 0.3s;
}

.news-item:last-child {
  border-bottom: none;
}

.news-item:hover {
  background-color: #f8f9fa;
}

.news-icon {
  font-size: 1.2em;
  margin-right: 12px;
  margin-top: 2px;
  width: 20px;
  text-align: center;
}

.news-content {
  flex: 1;
}

.news-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 6px;
  line-height: 1.4;
}

.news-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-source {
  color: #007bff;
  font-size: 12px;
  background-color: #e7f3ff;
  padding: 2px 6px;
  border-radius: 3px;
}

.news-time {
  color: #999;
  font-size: 12px;
}

/* 系统状态样式 */
.system-status {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.status-label {
  font-weight: 500;
  color: #2c3e50;
}

/* 快捷操作样式 */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.quick-actions .el-button {
  justify-self: stretch;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
  }
  
  .stat-icon {
    margin-right: 0;
    margin-bottom: 10px;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style> 