<template>
  <div class="news-list">
    <div class="news-list-header">
      <div class="news-count">
        <el-icon><TrendCharts /></el-icon>
        共 {{ filteredNewsList.length }} 条新闻
      </div>
      <div class="list-actions">
        <el-button size="small" @click="refreshList" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>
    
    <div v-else-if="filteredNewsList.length === 0" class="empty-container">
      <el-empty description="暂无新闻数据" />
    </div>
    
    <div v-else class="news-cards-container">
      <transition-group name="news-card" tag="div" class="news-cards">
        <div 
          v-for="(news, index) in paginatedNews" 
          :key="news.id" 
          class="news-card"
          @click="$emit('view', news)"
        >
          <div class="news-card-header">
            <div class="news-number">{{ getNewsIndex(index) }}</div>
            <div class="card-actions">
              <el-button 
                size="small" 
                type="danger" 
                text
                @click.stop="$emit('delete', news)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          
          <div class="news-content">
            <h3 class="news-title" v-html="formatTitle(news.title)"></h3>
            
            <!-- 新闻摘要 -->
            <div v-if="news.summary" class="news-summary">
              <div 
                v-for="(paragraph, pIndex) in formatSummary(news.summary)" 
                :key="pIndex"
                class="summary-paragraph"
              >
                {{ paragraph }}
              </div>
            </div>
            
            <div class="news-meta">
              <el-tag 
                v-if="news.source && news.source !== 'AI新闻助手'"
                size="small" 
                :type="getSourceTagType(news.source)"
                class="source-tag"
              >
                {{ news.source }}
              </el-tag>
              <el-tag 
                v-if="news.model"
                type="warning"
                size="small"
                class="model-tag"
              >
                🤖 {{ news.model }}
              </el-tag>
              <span class="publish-time">{{ formatTime(news.published_at) }}</span>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
    
    <div class="pagination-container" v-if="filteredNewsList.length > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 60]"
        :total="filteredNewsList.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        background
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { Refresh, Delete, TrendCharts } from '@element-plus/icons-vue'

export default {
  name: 'NewsList',
  components: {
    Refresh,
    Delete,
    TrendCharts
  },
  props: {
    newsList: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['view', 'delete', 'refresh'],
  setup(props, { emit }) {
    const currentPage = ref(1)
    const pageSize = ref(12)
    
    // 过滤有效新闻（排除只有日期的条目）
    const filteredNewsList = computed(() => {
      return props.newsList.filter(news => {
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
      }).map(news => {
        // 不再清理标题，保持原始标题用于格式化处理
        return {
          ...news,
          title: news.title.trim()
        }
      })
    })
    
    // 计算分页后的新闻
    const paginatedNews = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredNewsList.value.slice(start, end)
    })
    
    // 获取新闻序号
    const getNewsIndex = (pageIndex) => {
      return (currentPage.value - 1) * pageSize.value + pageIndex + 1
    }
    
    // 监听新闻列表变化，重置到第一页
    watch(() => props.newsList, () => {
      currentPage.value = 1
    }, { deep: true })
    
    // 处理分页大小变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
    }
    
    // 处理当前页变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
    }
    
    // 刷新列表
    const refreshList = () => {
      emit('refresh')
    }
    
    // 格式化时间
    const formatTime = (time) => {
      if (!time) return '未知'
      const date = new Date(time)
      const now = new Date()
      const diff = now - date
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
        return date.toLocaleDateString()
      }
    }
    
    // 获取来源标签类型
    const getSourceTagType = (source) => {
      if (!source) return ''
      
      const sourceTypes = {
        'Hacker News': 'warning',
        'Product Hunt': 'info',
        'Dev.to': 'success',
        'GitHub': 'primary',
        'Vue.js官方': 'success',
        'React团队': 'primary',
        'TypeScript官方': 'info',
        'AI新闻助手': 'success'
      }
      
      return sourceTypes[source] || 'default'
    }

    // 格式化标题，突出显示重要关键词
    const formatTitle = (title) => {
      if (!title) return ''
      
      // 首先处理原有的**标记
      let formattedTitle = title
        .replace(/\*\*([^*]+)\*\*/g, '<span class="highlight-text">$1</span>')  // **文本** -> 彩色文本
        .replace(/\*([^*]+)\*/g, '<span class="emphasis-text">$1</span>')       // *文本* -> 强调文本
        .replace(/\*\*/g, '')                                                   // 移除剩余的 **
        .replace(/\*/g, '')                                                     // 移除剩余的 *
      
      // 定义重要关键词，主动添加突出显示
      const importantKeywords = [
        // AI公司和产品
        'OpenAI', 'ChatGPT', 'GPT-4', 'GPT-3', 'Claude', 'Anthropic',
        'Google', 'Gemini', 'Bard', 'Microsoft', 'Copilot', 'Azure',
        'Meta', 'Llama', 'NVIDIA', 'DeepMind', 'AlphaCode', 'Grok',
        'xAI', 'Elon Musk', 'Amazon', 'Bedrock', 'AWS',
        
        // 技术关键词
        'AI', '人工智能', '机器学习', '深度学习', '神经网络',
        '大模型', '生成式AI', '自然语言处理', 'NLP',
        
        // 重要动作词
        '发布', '推出', '宣布', '升级', '更新', '突破', '创新',
        '提升', '优化', '增强', '改进', '扩展'
      ]
      
      // 为关键词添加突出显示
      importantKeywords.forEach(keyword => {
        const regex = new RegExp(`\\b(${keyword})\\b`, 'gi')
        formattedTitle = formattedTitle.replace(regex, '<span class="highlight-text">$1</span>')
      })
      
      // 清理多余空格
      formattedTitle = formattedTitle.replace(/\s+/g, ' ').trim()
      
      return formattedTitle
    }

    // 格式化新闻摘要，使其分段显示
    const formatSummary = (summary) => {
      if (!summary) return []
      // 使用正则表达式将文本按段落分隔
      return summary.split(/[\r\n]+/).filter(paragraph => paragraph.trim() !== '')
    }
    
    return {
      currentPage,
      pageSize,
      filteredNewsList,
      paginatedNews,
      getNewsIndex,
      handleSizeChange,
      handleCurrentChange,
      refreshList,
      formatTime,
      getSourceTagType,
      formatTitle,
      formatSummary
    }
  }
}
</script>

<style scoped>
.news-list {
  width: 100%;
}

.news-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.news-count {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.list-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 20px;
}

.empty-container {
  padding: 40px;
  text-align: center;
}

.news-cards-container {
  width: 100%;
}

.news-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 15px;
  padding: 0;
}

.news-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  cursor: pointer;
  overflow: hidden;
  border: 1px solid #f0f0f0;
}

.news-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.news-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.news-number {
  background: #409eff;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: 6px;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.news-card:hover .card-actions {
  opacity: 1;
}

.news-content {
  padding: 16px;
}

.news-title {
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-summary {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
}

.summary-paragraph {
  margin-bottom: 8px;
  text-align: justify;
}

.summary-paragraph:last-child {
  margin-bottom: 0;
}

/* 突出显示的文本样式 */
.news-title :deep(.highlight-text) {
  color: #409eff;
  font-weight: 700;
  background: linear-gradient(135deg, #409eff 0%, #36cfc9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 8px rgba(64, 158, 255, 0.3);
  position: relative;
}

.news-title :deep(.emphasis-text) {
  color: #f56c6c;
  font-weight: 600;
  text-shadow: 0 0 4px rgba(245, 108, 108, 0.3);
}

/* 添加悬停效果 */
.news-card:hover .news-title :deep(.highlight-text) {
  transform: scale(1.05);
  transition: all 0.3s ease;
}

.news-card:hover .news-title :deep(.emphasis-text) {
  transform: scale(1.03);
  transition: all 0.3s ease;
}

.news-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.source-tag {
  font-size: 11px;
  font-weight: 500;
  border-radius: 4px;
}

.publish-time {
  color: #909399;
  font-size: 11px;
}

.pagination-container {
  margin-top: 25px;
  display: flex;
  justify-content: center;
}

/* 动画效果 */
.news-card-enter-active,
.news-card-leave-active {
  transition: all 0.3s ease;
}

.news-card-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.news-card-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.model-tag {
  margin-right: 8px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  border: none;
  color: #fff;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .news-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .news-list-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
    padding: 12px 16px;
  }
  
  .news-card {
    margin: 0 8px;
  }
  
  .news-title {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .news-cards {
    gap: 10px;
  }
  
  .news-card {
    margin: 0 4px;
  }
  
  .news-card-header,
  .news-content {
    padding: 10px 12px;
  }
}
</style> 