<template>
  <div class="news">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="news-header">
          <h2>📰 新闻收集中心</h2>
          <div class="header-actions">
            <el-button type="success" @click="refreshNews">
              <el-icon><Refresh /></el-icon>
              刷新全部
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- AI新闻收集区域 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="24">
        <el-card class="ai-news-card">
          <template #header>
            <div class="card-header">
              <span>🤖 AI新闻收集</span>
              <div>
                <el-button 
                  type="primary" 
                  @click="collectAINews"
                  :loading="aiCollecting"
                  :disabled="aiCollecting || !canCollect"
                >
                  <el-icon><Star /></el-icon>
                  {{ aiCollecting ? '正在收集...' : '收集AI新闻' }}
                </el-button>
                <el-button 
                  type="success" 
                  size="small"
                  @click="loadApiStatus"
                  style="margin-left: 10px;"
                >
                  🔄 刷新状态
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="ai-news-info">
            <div class="ai-stats">
              <el-statistic title="AI新闻总数" :value="aiNewsCount" />
              <el-statistic title="最近收集时间" :value="lastCollectTime" />
              <el-statistic title="今日已用次数" :value="currentCalls" />
              <el-statistic title="剩余次数" :value="remainingCalls" />
            </div>
            
            <div class="ai-description">
              <p>🎯 AI新闻收集功能使用 <strong>{{ currentModel }}</strong> 模型自动收集最新的AI行业新闻</p>
              <p>📈 重点关注：OpenAI、Claude、Google、Grok 等大厂的最新动态</p>
              <p v-if="!canCollect" style="color: #E6A23C;">⚠️ 今日收集次数已用完，每日限制{{ maxCalls }}次调用以控制费用</p>
              <p v-else style="color: #67C23A;">✅ 今日还可收集 {{ remainingCalls }} 次</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 新闻分类标签页 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <el-tabs v-model="activeTab" @tab-click="handleTabClick">
            <el-tab-pane label="📅 今日新闻" name="today">
              <news-list 
                :news-list="todayNewsList"
                :loading="todayNewsLoading"
                @view="viewNews"
                @delete="deleteNews"
              />
            </el-tab-pane>
            
            <el-tab-pane label="📰 全部新闻" name="all">
              <news-list 
                :news-list="newsList"
                :loading="loading"
                @view="viewNews"
                @delete="deleteNews"
              />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 新闻详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="新闻详情" width="800px">
      <div v-if="selectedNews" class="news-detail">
        <h3>{{ selectedNews.title }}</h3>
        <div class="news-meta">
          <el-tag size="small">{{ selectedNews.source }}</el-tag>
          <span class="news-author" v-if="selectedNews.author">作者: {{ selectedNews.author }}</span>
          <span class="news-time">{{ formatTime(selectedNews.published_at) }}</span>
        </div>
        
        <div v-if="selectedNews.tags && selectedNews.tags.length" class="news-tags">
          <strong>标签:</strong>
          <el-tag v-for="tag in selectedNews.tags" :key="tag" size="small" class="tag-item">
            {{ tag }}
          </el-tag>
        </div>
        
        <div v-if="selectedNews.summary" class="news-summary">
          <h4>摘要</h4>
          <p>{{ selectedNews.summary }}</p>
        </div>
        
        <div v-if="selectedNews.content" class="news-content">
          <h4>内容</h4>
          <div v-html="formatContent(selectedNews.content)"></div>
        </div>
        
        <div v-if="selectedNews.url" class="news-link">
          <el-button type="primary" size="small" @click="openLink(selectedNews.url)">
            <el-icon><Link /></el-icon>
            查看原文
          </el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { Refresh, Star, Link } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import NewsListComponent from '../components/NewsList.vue'

export default {
  name: 'News',
  components: {
    Refresh,
    Star,
    Link,
    'news-list': NewsListComponent
  },
  setup() {
    const newsList = ref([])
    const todayNewsList = ref([])
    const loading = ref(false)
    const todayNewsLoading = ref(false)
    const aiCollecting = ref(false)
    const activeTab = ref('today')
    const showDetailDialog = ref(false)
    const selectedNews = ref(null)
    const lastCollectTime = ref('暂无')
    
    // 🔒 API调用限制相关
    const remainingCalls = ref(3)
    const currentCalls = ref(0)
    const canCollect = ref(true)
    const maxCalls = ref(3)  // 每日最大调用次数，从后端获取
    const currentModel = ref('加载中...')  // 当前使用的AI模型，从后端获取
    
    // 过滤有效新闻的函数（与NewsList组件保持一致）
    const filterValidNews = (newsList) => {
      return newsList.filter(news => {
        // 过滤掉标题为空或只是日期格式的新闻
        if (!news.title || news.title.trim() === '') return false
        
        const title = news.title.trim()
        
        // 过滤掉各种日期格式的标题
        const datePatterns = [
          /^\d{4}年\d{1,2}月\d{1,2}日$/,           // 2025年7月14日
          /^\d{4}年\d{1,2}\.\d{1,2}日$/,          // 2025年7.14日
          /^\d{4}年\d{1,2}月\d{1,2}日\*+$/,       // 2025年7月14日**
          /^\*+\d{4}年\d{1,2}月\d{1,2}日\*+$/,    // **2025年7月14日**
          /^\d{4}-\d{1,2}-\d{1,2}$/,              // 2025-7-14
          /^\d{4}\/\d{1,2}\/\d{1,2}$/,            // 2025/7/14
          /^\d{1,2}月\d{1,2}日$/,                 // 7月14日
          /^\d{1,2}\.\d{1,2}$/,                   // 7.14
          /^今日$/,                               // 今日
          /^昨日$/,                               // 昨日
          /^明日$/,                               // 明日
          /^\d{4}年\d{1,2}月$/,                   // 2025年7月
          /^\d{1,2}月份$/,                        // 7月份
          /^第\d+周$/,                            // 第28周
          /^星期[一二三四五六日]$/,                // 星期一
          /^周[一二三四五六日]$/,                  // 周一
        ]
        
        // 检查是否匹配任何日期格式
        if (datePatterns.some(pattern => pattern.test(title))) {
          return false
        }
        
        // 过滤掉过短的标题（可能是无效数据）
        if (title.length < 5) return false
        
        // 过滤掉只包含特殊字符的标题
        if (/^[*\-_=\s]+$/.test(title)) return false
        
        return true
      })
    }
    
    // 计算AI新闻数量（使用过滤后的有效新闻）
    const aiNewsCount = computed(() => {
      const validNews = filterValidNews(newsList.value)
      return validNews.filter(news => 
        news.source === 'AI新闻助手' || news.title.includes('AI') || news.title.includes('人工智能')
      ).length
    })
    
    // 加载所有新闻
    const loadNews = async () => {
      loading.value = true
      try {
        const response = await fetch('/api/v1/news/')
        const data = await response.json()
        
        if (data.success) {
          newsList.value = data.data
        } else {
          ElMessage.error('加载新闻失败')
        }
      } catch (error) {
        console.error('加载新闻失败:', error)
        ElMessage.error('加载新闻失败')
      } finally {
        loading.value = false
      }
    }
    
    // 加载今日新闻
    const loadTodayNews = async () => {
      todayNewsLoading.value = true
      try {
        const response = await fetch('/api/v1/news/')
        const data = await response.json()
        
        if (data.success) {
          // 过滤今日新闻（24小时内）
          const today = new Date()
          const yesterday = new Date(today)
          yesterday.setDate(yesterday.getDate() - 1)
          
          todayNewsList.value = data.data.filter(news => {
            const newsDate = new Date(news.created_at || news.published_at)
            return newsDate >= yesterday
          })
          
          if (todayNewsList.value.length > 0) {
            lastCollectTime.value = formatTime(todayNewsList.value[0].created_at)
          }
        } else {
          ElMessage.error('加载今日新闻失败')
        }
      } catch (error) {
        console.error('加载今日新闻失败:', error)
        ElMessage.error('加载今日新闻失败')
      } finally {
        todayNewsLoading.value = false
      }
    }
    

    
    // 🔒 获取API调用状态
    const loadApiStatus = async () => {
      try {
        const response = await fetch('/api/v1/news/ai/status')
        const data = await response.json()
        
        if (data.success) {
          remainingCalls.value = data.data.remaining_calls
          currentCalls.value = data.data.current_calls
          canCollect.value = data.data.can_collect
          maxCalls.value = data.data.max_calls  // 从后端获取最大调用次数
          currentModel.value = data.data.current_model  // 从后端获取当前模型
        }
      } catch (error) {
        console.error('获取API状态失败:', error)
      }
    }
    
    // 收集AI新闻
    const collectAINews = async () => {
      // 🔒 检查是否可以收集
      if (!canCollect.value) {
        ElMessage.warning(`今日AI新闻收集次数已用完(${maxCalls.value}次)，请明天再试`)
        return
      }
      
      aiCollecting.value = true
      try {
        const response = await fetch('/api/v1/news/ai/collect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        
        const data = await response.json()
        
        if (data.success) {
          ElMessage.success(`${data.message} (耗时: ${data.execution_time.toFixed(2)}秒)`)
          
          // 🔒 更新剩余次数
          if (data.remaining_calls !== undefined) {
            remainingCalls.value = data.remaining_calls
            currentCalls.value = maxCalls.value - data.remaining_calls
            canCollect.value = data.remaining_calls > 0
          }
          
          // 重新加载新闻
          await loadNews()
          await loadTodayNews()
          
          // 如果当前在今日新闻标签页，也重新加载
          if (activeTab.value === 'today') {
            await loadTodayNews()
          }
        } else {
          ElMessage.error(`收集失败: ${data.error || '未知错误'}`)
        }
      } catch (error) {
        console.error('收集AI新闻失败:', error)
        if (error.message && error.message.includes('429')) {
          ElMessage.error('今日AI新闻收集次数已达限制，请明天再试')
          canCollect.value = false
          remainingCalls.value = 0
        } else {
          ElMessage.error('收集AI新闻失败')
        }
      } finally {
        aiCollecting.value = false
      }
    }
    
    // 刷新所有新闻
    const refreshNews = async () => {
      await Promise.all([
        loadNews(),
        loadTodayNews()
      ])
      ElMessage.success('新闻刷新成功')
    }
    
    // 处理标签页切换
    const handleTabClick = (tab) => {
      if (tab.name === 'today' && todayNewsList.value.length === 0) {
        loadTodayNews()
      }
    }
    
    // 查看新闻详情
    const viewNews = (news) => {
      selectedNews.value = news
      showDetailDialog.value = true
    }
    
    // 删除新闻
    const deleteNews = (news) => {
      ElMessageBox.confirm(
        '确定要删除这条新闻吗？',
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(() => {
        // TODO: 调用删除API
        // 临时从列表中移除
        const removeFromList = (list) => {
          const index = list.findIndex(n => n.id === news.id)
          if (index > -1) {
            list.splice(index, 1)
          }
        }
        
        removeFromList(newsList.value)
        removeFromList(todayNewsList.value)
        
        ElMessage.success('新闻删除成功')
      }).catch(() => {
        // 取消删除
      })
    }
    
    // 格式化时间
    const formatTime = (time) => {
      if (!time) return '未知'
      const date = new Date(time)
      return date.toLocaleString()
    }
    
    // 格式化内容
    const formatContent = (content) => {
      if (!content) return ''
      // 简单的换行处理
      return content.replace(/\n/g, '<br>')
    }
    
    // 打开链接
    const openLink = (url) => {
      if (url) {
        window.open(url, '_blank')
      }
    }
    
    onMounted(() => {
      loadNews()
      loadTodayNews()
      loadApiStatus()  // 🔒 加载API调用状态
    })
    
    return {
      newsList,
      todayNewsList,
      loading,
      todayNewsLoading,
      aiCollecting,
      activeTab,
      showDetailDialog,
      selectedNews,
      lastCollectTime,
      aiNewsCount,
      collectAINews,
      refreshNews,
      handleTabClick,
      viewNews,
      deleteNews,
      formatTime,
      formatContent,
      openLink,
      // 🔒 API调用限制相关
      remainingCalls,
      currentCalls,
      canCollect,
      maxCalls,
      currentModel,
      loadApiStatus
    }
  }
}
</script>

<style scoped>
.news {
  padding: 20px;
  background-color: #f8f9fa;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.news-header h2 {
  margin: 0;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.ai-news-card {
  border: 2px solid #409eff;
  border-radius: 8px;
}

.ai-news-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #409eff;
}

.ai-news-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.ai-stats {
  display: flex;
  gap: 40px;
}

.ai-description {
  flex: 1;
  color: #6c757d;
}

.ai-description p {
  margin: 5px 0;
  line-height: 1.6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-detail {
  max-height: 600px;
  overflow-y: auto;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 15px 0;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.news-author {
  color: #6c757d;
  font-size: 14px;
}

.news-time {
  color: #999;
  font-size: 12px;
}

.news-tags {
  margin: 15px 0;
}

.tag-item {
  margin-left: 5px;
}

.news-summary {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.news-content {
  margin: 20px 0;
  line-height: 1.6;
}

.news-link {
  margin-top: 20px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-news-info {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .ai-stats {
    flex-direction: column;
    gap: 20px;
  }
  
  .news-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style> 