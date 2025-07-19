<template>
  <div class="cursor-updates">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="header">
          <h2>Cursor 更新日志</h2>
          <div class="actions">
            <el-button type="primary" @click="collectUpdates" :loading="collecting">
              <el-icon><Refresh /></el-icon>
              采集更新
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 采集过程显示区域 -->
    <el-row :gutter="20" v-if="collectionInfo || collecting || realTimeProgress.isActive" style="margin-bottom: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📊 采集过程</span>
              <el-button size="small" @click="clearCollectionInfo" v-if="!collecting && !realTimeProgress.isActive">
                <el-icon><Close /></el-icon>
                清除
              </el-button>
            </div>
          </template>
          
          <!-- 实时进度显示 -->
          <div v-if="realTimeProgress.isActive" class="real-time-progress">
            <div class="progress-header">
              <h4>🔄 实时采集进度</h4>
              <div class="status-badge" :class="realTimeProgress.status">
                {{ getStatusText(realTimeProgress.status) }}
              </div>
            </div>
            
            <!-- 当前状态 -->
            <div class="current-status">
              <el-icon class="status-icon" :class="{ 'is-loading': realTimeProgress.status === 'processing' }">
                <Loading v-if="realTimeProgress.status === 'processing'" />
                <SuccessFilled v-else-if="realTimeProgress.status === 'completed'" />
                <WarningFilled v-else-if="realTimeProgress.status === 'error'" />
                <InfoFilled v-else />
              </el-icon>
              <span class="status-message">{{ realTimeProgress.currentMessage }}</span>
            </div>
            
            <!-- 进度条 -->
            <div v-if="realTimeProgress.progress.total > 0" class="progress-section">
              <el-progress 
                :percentage="realTimeProgress.progress.percentage" 
                :status="realTimeProgress.status === 'error' ? 'exception' : 'primary'"
                :stroke-width="12"
              >
                <template #default="{ percentage }">
                  <span class="progress-text">
                    {{ realTimeProgress.progress.current }}/{{ realTimeProgress.progress.total }} ({{ percentage }}%)
                  </span>
                </template>
              </el-progress>
              <div class="progress-message">{{ realTimeProgress.progress.message }}</div>
            </div>
            
            <!-- 实时统计 -->
            <div v-if="realTimeProgress.stats" class="real-time-stats">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-icon">📊</div>
                  <div class="stat-info">
                    <div class="stat-number">{{ realTimeProgress.stats.total_versions || 0 }}</div>
                    <div class="stat-label">总版本数</div>
                  </div>
                </div>
                
                <div class="stat-item">
                  <div class="stat-icon">🆕</div>
                  <div class="stat-info">
                    <div class="stat-number">{{ realTimeProgress.stats.new_versions || 0 }}</div>
                    <div class="stat-label">新版本数</div>
                  </div>
                </div>
                
                <div class="stat-item">
                  <div class="stat-icon">📋</div>
                  <div class="stat-info">
                    <div class="stat-number">{{ realTimeProgress.stats.existing_versions || 0 }}</div>
                    <div class="stat-label">已存在版本</div>
                  </div>
                </div>
                
                <div class="stat-item">
                  <div class="stat-icon">💰</div>
                  <div class="stat-info">
                    <div class="stat-number">{{ realTimeProgress.stats.api_calls_made || 0 }}</div>
                    <div class="stat-label">API调用次数</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 版本处理详情 -->
            <div v-if="realTimeProgress.versionDetails.length > 0" class="version-details">
              <h4>🔍 版本处理详情</h4>
              <div class="details-list" style="max-height: 300px; overflow-y: auto;">
                <div 
                  v-for="detail in realTimeProgress.versionDetails" 
                  :key="detail.version"
                  class="detail-item"
                  :class="detail.status"
                >
                  <div class="detail-header">
                    <span class="version">v{{ detail.version }}</span>
                    <el-tag 
                      :type="getVersionTagType(detail.status)" 
                      size="small"
                    >
                      {{ getVersionStatusText(detail.status) }}
                    </el-tag>
                    <span class="api-calls" :class="detail.api_calls > 0 ? 'cost' : 'free'">
                      {{ detail.api_calls > 0 ? `💰 ${detail.api_calls} 次API调用` : '🆓 免费' }}
                    </span>
                    <span v-if="detail.processing_time" class="processing-time">
                      ⏱️ {{ detail.processing_time.toFixed(1) }}s
                    </span>
                  </div>
                  <div class="detail-message">{{ detail.message }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 传统采集信息显示（如果没有实时进度） -->
          <div v-else-if="collectionInfo" class="collection-stats">
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-icon">📊</div>
                <div class="stat-info">
                  <div class="stat-number">{{ collectionInfo.total_versions }}</div>
                  <div class="stat-label">总版本数</div>
                </div>
              </div>
              
              <div class="stat-item">
                <div class="stat-icon">🆕</div>
                <div class="stat-info">
                  <div class="stat-number">{{ collectionInfo.new_versions }}</div>
                  <div class="stat-label">新版本数</div>
                </div>
              </div>
              
              <div class="stat-item">
                <div class="stat-icon">📋</div>
                <div class="stat-info">
                  <div class="stat-number">{{ collectionInfo.existing_versions }}</div>
                  <div class="stat-label">已存在版本</div>
                </div>
              </div>
              
              <div class="stat-item">
                <div class="stat-icon">💰</div>
                <div class="stat-info">
                  <div class="stat-number">{{ collectionInfo.api_calls_made }}</div>
                  <div class="stat-label">API调用次数</div>
                </div>
              </div>
            </div>
            
            <!-- 费用提示 -->
            <div v-if="collectionInfo.api_calls_made === 0" class="cost-tip success">
              <el-icon><SuccessFilled /></el-icon>
              太棒了！本次采集没有产生任何费用，所有版本都已存在于数据库中。
            </div>
            <div v-else class="cost-tip info">
              <el-icon><InfoFilled /></el-icon>
              本次采集调用了 {{ collectionInfo.api_calls_made }} 次API，用于翻译和分析新版本。
            </div>
          </div>
          
          <div v-if="collecting" class="collecting-status">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在从 Cursor 官网采集最新更新...</span>
          </div>
          
          <!-- 处理详情 -->
          <div v-if="collectionInfo && collectionInfo.processing_details" class="processing-details">
            <h4>🔍 处理详情</h4>
            <div class="details-list">
              <div 
                v-for="detail in collectionInfo.processing_details" 
                :key="detail.version"
                class="detail-item"
                :class="detail.status"
              >
                <div class="detail-header">
                  <span class="version">v{{ detail.version }}</span>
                  <el-tag 
                    :type="detail.status === 'new' ? 'success' : 'info'" 
                    size="small"
                  >
                    {{ detail.status === 'new' ? '🆕 新版本' : '📋 已存在' }}
                  </el-tag>
                  <span class="api-calls" :class="detail.api_calls > 0 ? 'cost' : 'free'">
                    {{ detail.api_calls > 0 ? `💰 ${detail.api_calls} 次API调用` : '🆓 免费' }}
                  </span>
                </div>
                <div class="detail-message">{{ detail.message }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计信息 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.total_updates }}</div>
            <div class="stat-label">总更新数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.major_updates }}</div>
            <div class="stat-label">重大更新</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.latest_version || 'N/A' }}</div>
            <div class="stat-label">最新版本</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ formatDate(stats.latest_release_date) }}</div>
            <div class="stat-label">最新发布</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 更新列表 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>更新列表</span>
              <el-button @click="loadUpdates" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <div class="updates-container">
            <div v-if="loading" class="loading">
              <el-skeleton :rows="5" animated />
            </div>
            
            <div v-else-if="updates.length === 0" class="empty">
              <el-empty description="暂无更新数据" />
            </div>
            
            <div v-else class="updates-list">
              <div v-for="update in updates" :key="update.id" class="update-item">
                <div class="update-header">
                  <div class="version-info">
                    <span class="version">v{{ update.version }}</span>
                    <el-tag v-if="update.is_major" type="success" size="small">重大更新</el-tag>
                    <span class="release-date">{{ formatDate(update.release_date) }}</span>
                  </div>
                  <div class="actions">
                    <el-button size="small" @click="showDetail(update)">查看详情</el-button>
                  </div>
                </div>
                
                <div class="update-content">
                  <h3>{{ update.title }}</h3>
                  <div class="tabs">
                    <el-tabs v-model="activeTab[update.id]" @tab-click="handleTabClick">
                      <el-tab-pane label="中文翻译" :name="`translated_${update.id}`">
                        <div class="content-section">
                          <div v-if="update.translated_content" v-html="formatContent(update.translated_content)"></div>
                          <div v-else class="no-content">暂无中文翻译</div>
                        </div>
                      </el-tab-pane>
                      
                      <el-tab-pane label="原文" :name="`original_${update.id}`">
                        <div class="content-section">
                          <div v-if="update.original_content" v-html="formatContent(update.original_content)"></div>
                          <div v-else class="no-content">暂无原文内容</div>
                        </div>
                      </el-tab-pane>
                      
                      <el-tab-pane label="AI 分析" :name="`analysis_${update.id}`">
                        <div class="content-section">
                          <div v-if="update.analysis" v-html="formatContent(update.analysis)"></div>
                          <div v-else class="no-content">暂无分析内容</div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="Cursor 更新详情" width="80%">
      <div v-if="selectedUpdate" class="detail-content">
        <div class="detail-header">
          <h2>{{ selectedUpdate.title }}</h2>
          <div class="meta-info">
            <el-tag size="large">v{{ selectedUpdate.version }}</el-tag>
            <span class="release-date">发布时间: {{ formatDateTime(selectedUpdate.release_date) }}</span>
          </div>
        </div>
        
        <el-tabs v-model="detailActiveTab" class="detail-tabs">
          <el-tab-pane label="中文翻译" name="translated">
            <div class="detail-section">
              <div v-if="selectedUpdate.translated_content" v-html="formatContent(selectedUpdate.translated_content)"></div>
              <div v-else class="no-content">暂无中文翻译</div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="原文" name="original">
            <div class="detail-section">
              <div v-if="selectedUpdate.original_content" v-html="formatContent(selectedUpdate.original_content)"></div>
              <div v-else class="no-content">暂无原文内容</div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="AI 分析" name="analysis">
            <div class="detail-section">
              <div v-if="selectedUpdate.analysis" v-html="formatContent(selectedUpdate.analysis)"></div>
              <div v-else class="no-content">暂无分析内容</div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button type="primary" @click="openOriginalLink">访问原文</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { Refresh, Close, Loading, SuccessFilled, InfoFilled, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 创建axios实例，配置baseURL
const api = axios.create({
  baseURL: '', // 使用相对路径，通过nginx代理
  timeout: 10000, // 默认10秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 添加请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 添加响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API请求失败:', error)
    return Promise.reject(error)
  }
)

export default {
  name: 'CursorUpdates',
  components: {
    Refresh, Close, Loading, SuccessFilled, InfoFilled, WarningFilled
  },
  setup() {
    const updates = ref([])
    const loading = ref(false)
    const collecting = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const activeTab = reactive({})
    const showDetailDialog = ref(false)
    const selectedUpdate = ref(null)
    const detailActiveTab = ref('translated')
    
    const stats = ref({
      total_updates: 0,
      major_updates: 0,
      latest_version: null,
      latest_release_date: null
    })
    
    const collectionInfo = ref(null)

    const realTimeProgress = reactive({
      isActive: false,
      status: 'idle', // 'idle', 'processing', 'completed', 'error'
      currentMessage: '',
      progress: {
        total: 0,
        current: 0,
        percentage: 0,
        message: ''
      },
      stats: {
        total_versions: 0,
        new_versions: 0,
        existing_versions: 0,
        api_calls_made: 0
      },
      versionDetails: []
    })

    // WebSocket 管理
    let websocket = null
    let reconnectInterval = null
    const isConnected = ref(false)

    const connectWebSocket = () => {
      try {
        // 建立WebSocket连接 - 通过nginx代理
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        const wsUrl = `${protocol}//${host}/ws/cursor_collection`
        
        console.log('尝试连接WebSocket:', wsUrl)
        websocket = new WebSocket(wsUrl)
        
        websocket.onopen = () => {
          console.log('WebSocket连接已建立')
          isConnected.value = true
          
          // 清除重连定时器
          if (reconnectInterval) {
            clearInterval(reconnectInterval)
            reconnectInterval = null
          }
        }
        
        websocket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            handleWebSocketMessage(message)
          } catch (error) {
            console.error('解析WebSocket消息失败:', error)
          }
        }
        
        websocket.onclose = () => {
          console.log('WebSocket连接已关闭')
          isConnected.value = false
          websocket = null
          
          // 如果进度正在进行中，尝试重连
          if (realTimeProgress.isActive && realTimeProgress.status === 'processing') {
            startReconnect()
          }
        }
        
        websocket.onerror = (error) => {
          console.error('WebSocket连接错误:', error)
          isConnected.value = false
        }
        
      } catch (error) {
        console.error('WebSocket连接失败:', error)
      }
    }

    const startReconnect = () => {
      if (!reconnectInterval) {
        reconnectInterval = setInterval(() => {
          console.log('尝试重连WebSocket...')
          connectWebSocket()
        }, 3000) // 每3秒重连一次
      }
    }

    const disconnectWebSocket = () => {
      if (reconnectInterval) {
        clearInterval(reconnectInterval)
        reconnectInterval = null
      }
      
      if (websocket) {
        websocket.close()
        websocket = null
      }
      
      isConnected.value = false
    }

    const handleWebSocketMessage = (message) => {
      console.log('收到WebSocket消息:', message)
      
      switch (message.type) {
        case 'connection_established':
          console.log('WebSocket连接确认:', message.connection_id)
          break
          
        case 'status_update':
          realTimeProgress.isActive = true
          realTimeProgress.status = message.status
          realTimeProgress.currentMessage = message.message
          
          // 如果采集完成，延迟关闭实时进度
          if (message.status === 'completed') {
            setTimeout(() => {
              realTimeProgress.isActive = false
              collecting.value = false
              loadUpdates() // 重新加载更新列表
              loadStats() // 重新加载统计信息
            }, 3000) // 3秒后关闭
          } else if (message.status === 'error') {
            setTimeout(() => {
              realTimeProgress.isActive = false
              collecting.value = false
            }, 5000) // 错误状态5秒后关闭
          }
          break
          
        case 'progress_update':
          realTimeProgress.progress = {
            total: message.total,
            current: message.current,
            percentage: message.percentage,
            message: message.message
          }
          break
          
        case 'version_update':
          // 更新或添加版本详情
          const existingIndex = realTimeProgress.versionDetails.findIndex(
            v => v.version === message.version
          )
          
          const versionDetail = {
            version: message.version,
            status: message.status,
            message: message.message,
            api_calls: message.api_calls,
            processing_time: message.processing_time
          }
          
          if (existingIndex >= 0) {
            realTimeProgress.versionDetails[existingIndex] = versionDetail
          } else {
            realTimeProgress.versionDetails.push(versionDetail)
          }
          break
          
        case 'stats_update':
          realTimeProgress.stats = message.stats
          break
          
        case 'heartbeat':
          // 心跳响应，无需处理
          break
          
        default:
          console.log('未知消息类型:', message.type)
      }
    }

    const sendHeartbeat = () => {
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({ type: 'ping' }))
      }
    }
    
    const loadUpdates = async () => {
      loading.value = true
      try {
        const response = await api.get('/api/v1/cursor/updates', {
          params: {
            skip: (currentPage.value - 1) * pageSize.value,
            limit: pageSize.value
          },
          timeout: 5000 // 5秒超时
        })
        
        updates.value = response.data.updates || []
        total.value = response.data.total || 0
        
        // 初始化选项卡状态
        updates.value.forEach(update => {
          activeTab[update.id] = `translated_${update.id}`
        })
        
      } catch (error) {
        console.error('加载更新失败:', error)
        ElMessage.error('加载更新失败，请检查网络连接')
        // 设置默认值
        updates.value = []
        total.value = 0
      } finally {
        loading.value = false
      }
    }
    
    const loadStats = async () => {
      try {
        const response = await api.get('/api/v1/cursor/stats', {
          timeout: 5000 // 5秒超时
        })
        stats.value = response.data
      } catch (error) {
        console.error('加载统计信息失败:', error)
        ElMessage.error('加载统计信息失败，请检查网络连接')
        // 设置默认值
        stats.value = {
          total_updates: 0,
          major_updates: 0,
          latest_version: null,
          latest_release_date: null
        }
      }
    }
    
    const collectUpdates = async () => {
      collecting.value = true
      collectionInfo.value = null
      
      // 重置实时进度
      realTimeProgress.isActive = true
      realTimeProgress.status = 'processing'
      realTimeProgress.currentMessage = '准备开始采集...'
      realTimeProgress.progress = { total: 0, current: 0, percentage: 0, message: '' }
      realTimeProgress.stats = { total_versions: 0, new_versions: 0, existing_versions: 0, api_calls_made: 0 }
      realTimeProgress.versionDetails = []
      
      // 确保WebSocket连接
      if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        connectWebSocket()
      }
      
      try {
        ElMessage.info('开始采集Cursor更新，您可以在上方看到实时进度...')
        
        const response = await api.post('/api/v1/cursor/collect', {}, {
          timeout: 180000, // 3分钟超时
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        ElMessage.success(response.data.message)
        
        // 更新传统的采集信息（作为备份）
        collectionInfo.value = response.data.collection_info
        
      } catch (error) {
        console.error('采集失败:', error)
        
        // 更新实时进度状态
        realTimeProgress.status = 'error'
        realTimeProgress.currentMessage = `采集失败: ${error.response?.data?.detail || error.message}`
        
        if (error.code === 'ECONNABORTED') {
          ElMessage.error('采集超时，请稍后重试。如果持续出现问题，可能是网络较慢或Cursor网站访问困难。')
        } else if (error.response?.status === 504) {
          ElMessage.error('网关超时，采集过程可能较长，请稍后查看结果')
        } else {
          ElMessage.error(`采集失败: ${error.response?.data?.detail || error.message}`)
        }
      } finally {
        // 如果WebSocket没有处理完成状态，则手动设置
        if (realTimeProgress.status === 'processing') {
          setTimeout(() => {
            collecting.value = false
            realTimeProgress.isActive = false
          }, 2000)
        }
      }
    }

    const clearCollectionInfo = () => {
      collectionInfo.value = null
      
      // 清理实时进度
      realTimeProgress.isActive = false
      realTimeProgress.status = 'idle'
      realTimeProgress.currentMessage = ''
      realTimeProgress.progress = { total: 0, current: 0, percentage: 0, message: '' }
      realTimeProgress.stats = { total_versions: 0, new_versions: 0, existing_versions: 0, api_calls_made: 0 }
      realTimeProgress.versionDetails = []
    }
    
    const showDetail = (update) => {
      selectedUpdate.value = update
      showDetailDialog.value = true
      detailActiveTab.value = 'translated'
    }
    
    const openOriginalLink = () => {
      if (selectedUpdate.value && selectedUpdate.value.url) {
        window.open(selectedUpdate.value.url, '_blank')
      }
    }
    
    const formatContent = (content) => {
      if (!content) return ''
      
      let formattedContent = content
      
      // 先移除所有的### 和 *** 标记符号
      formattedContent = formattedContent.replace(/#{1,6}\s*/g, '')
      formattedContent = formattedContent.replace(/\*{3,}/g, '')
      
      // 清理多余的空白字符
      formattedContent = formattedContent.replace(/\s+/g, ' ').trim()
      
      // 处理数字列表 (1. 2. 3.)
      formattedContent = formattedContent.replace(/^\d+\.\s+(.*)$/gm, '<li style="margin: 8px 0; line-height: 1.6;">$1</li>')
      
      // 处理无序列表 (- * +)
      formattedContent = formattedContent.replace(/^[-*+]\s+(.*)$/gm, '<li style="margin: 8px 0; line-height: 1.6;">$1</li>')
      
      // 包装连续的li为ul
      formattedContent = formattedContent.replace(/(<li[^>]*>.*?<\/li>\s*)+/g, '<ul style="margin: 15px 0; padding-left: 25px;">$&</ul>')
      
      // 处理粗体文本
      formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: bold; color: #333;">$1</strong>')
      
      // 处理斜体文本
      formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em style="font-style: italic;">$1</em>')
      
      // 处理代码块
      formattedContent = formattedContent.replace(/`([^`]+)`/g, '<code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; color: #e83e8c;">$1</code>')
      
      // 处理功能标签 (如 **智能体规划系统**: )
      formattedContent = formattedContent.replace(/\*\*([^*]+)\*\*:/g, '<div style="font-weight: bold; color: #409eff; margin: 20px 0 8px 0; padding: 8px 12px; background: #f0f8ff; border-left: 4px solid #409eff; border-radius: 4px;">$1</div>')
      
      // 按句号分段
      formattedContent = formattedContent.replace(/([。！？])\s*(?=\S)/g, '$1<br><br>')
      
      // 处理单个换行
      formattedContent = formattedContent.replace(/\n/g, '<br>')
      
      // 处理双换行为段落分隔
      formattedContent = formattedContent.replace(/(<br>\s*){2,}/g, '</p><p>')
      
      // 包装为段落
      if (!formattedContent.includes('<p>')) {
        formattedContent = '<p style="margin: 15px 0; line-height: 1.8; color: #555;">' + formattedContent + '</p>'
      } else {
        // 为已有的段落添加样式
        formattedContent = formattedContent.replace(/<p>/g, '<p style="margin: 15px 0; line-height: 1.8; color: #555;">')
      }
      
      // 清理空段落
      formattedContent = formattedContent.replace(/<p[^>]*>\s*<\/p>/g, '')
      
      // 处理特殊符号和emoji
      formattedContent = formattedContent.replace(/→/g, '→')
      formattedContent = formattedContent.replace(/✓/g, '✅')
      formattedContent = formattedContent.replace(/×/g, '❌')
      
      return formattedContent
    }
    
    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString()
    }
    
    const formatDateTime = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleString()
    }
    
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      loadUpdates()
    }
    
    const handleCurrentChange = (page) => {
      currentPage.value = page
      loadUpdates()
    }
    
    const handleTabClick = (tab) => {
      // 标签页点击事件处理器
      // 目前无需特殊处理，可在此添加必要的逻辑
    }

    const getStatusText = (status) => {
      switch (status) {
        case 'idle':
          return '待机'
        case 'processing':
          return '采集中'
        case 'completed':
          return '完成'
        case 'error':
          return '错误'
        default:
          return '未知'
      }
    }

    const getVersionTagType = (status) => {
      switch (status) {
        case 'new':
          return 'success'
        case 'existing':
          return 'info'
        default:
          return 'info'
      }
    }

    const getVersionStatusText = (status) => {
      switch (status) {
        case 'new':
          return '🆕 新版本'
        case 'existing':
          return '📋 已存在'
        default:
          return '未知'
      }
    }
    
    onMounted(() => {
      loadUpdates()
      loadStats()
      connectWebSocket() // 启动WebSocket连接
      setInterval(sendHeartbeat, 30000) // 每30秒发送心跳
    })

    onUnmounted(() => {
      disconnectWebSocket() // 组件卸载时断开WebSocket
    })
    
    return {
      updates,
      loading,
      collecting,
      currentPage,
      pageSize,
      total,
      activeTab,
      showDetailDialog,
      selectedUpdate,
      detailActiveTab,
      stats,
      collectionInfo,
      realTimeProgress,
      isConnected,
      loadUpdates,
      collectUpdates,
      showDetail,
      openOriginalLink,
      formatContent,
      formatDate,
      formatDateTime,
      handleSizeChange,
      handleCurrentChange,
      handleTabClick,
      clearCollectionInfo,
      getStatusText,
      getVersionTagType,
      getVersionStatusText,
      connectWebSocket,
      disconnectWebSocket
    }
  }
}
</script>

<style scoped>
.cursor-updates {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 20px;
}

.stat-number {
  font-size: 2em;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  color: #666;
  margin-top: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.updates-container {
  min-height: 400px;
}

.update-item {
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 20px;
  padding: 20px;
  background: #fafafa;
}

.update-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.version {
  font-size: 1.2em;
  font-weight: bold;
  color: #409eff;
}

.release-date {
  color: #666;
  font-size: 0.9em;
}

.update-content h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.content-section {
  max-height: 400px;
  overflow-y: auto;
  padding: 20px;
  background: white;
  border-radius: 6px;
  line-height: 1.8;
}

/* 内容格式化样式 */
.content-section ::v-deep(h1) {
  color: #333;
  margin: 25px 0 20px 0;
  font-size: 1.5em;
  font-weight: bold;
  border-bottom: 2px solid #409eff;
  padding-bottom: 10px;
}

.content-section ::v-deep(h2) {
  color: #333;
  margin: 20px 0 15px 0;
  font-size: 1.3em;
  font-weight: bold;
  border-left: 4px solid #409eff;
  padding-left: 12px;
}

.content-section ::v-deep(h3) {
  color: #333;
  margin: 15px 0 10px 0;
  font-size: 1.1em;
  font-weight: bold;
  color: #606266;
}

.content-section ::v-deep(p) {
  margin: 12px 0;
  line-height: 1.8;
  color: #555;
  text-align: justify;
}

.content-section ::v-deep(ul) {
  margin: 15px 0;
  padding-left: 25px;
}

.content-section ::v-deep(li) {
  margin: 8px 0;
  line-height: 1.6;
  color: #555;
}

.content-section ::v-deep(strong) {
  font-weight: bold;
  color: #333;
}

.content-section ::v-deep(em) {
  font-style: italic;
  color: #666;
}

.content-section ::v-deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  color: #e83e8c;
  font-size: 0.9em;
}

.content-section ::v-deep(div[style*="border-left"]) {
  font-weight: bold;
  color: #409eff;
  margin: 15px 0 8px 0;
  padding: 8px 12px;
  background: #f0f8ff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
}

/* 空内容提示样式 */
.no-content {
  text-align: center;
  color: #999;
  font-style: italic;
  padding: 40px 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: center;
}

.detail-content {
  min-height: 600px;
}

.detail-header {
  margin-bottom: 20px;
}

.detail-header h2 {
  margin: 0 0 10px 0;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.detail-section {
  max-height: 500px;
  overflow-y: auto;
  padding: 20px;
  background: #fafafa;
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 内容样式 */
.content-section :deep(h1) {
  font-size: 1.5em;
  margin: 20px 0 10px 0;
  color: #333;
}

.content-section :deep(h2) {
  font-size: 1.3em;
  margin: 15px 0 10px 0;
  color: #333;
}

.content-section :deep(h3) {
  font-size: 1.1em;
  margin: 10px 0 5px 0;
  color: #333;
}

.content-section :deep(ul) {
  margin: 10px 0;
  padding-left: 20px;
}

.content-section :deep(li) {
  margin: 5px 0;
  line-height: 1.5;
}

.collection-info {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.collecting-status {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #606266;
  font-size: 1.1em;
}

.collecting-status .is-loading {
  margin-right: 10px;
  font-size: 1.5em;
}

.collection-summary {
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
}

.number {
  font-size: 1.8em;
  font-weight: bold;
  color: #409eff;
}

.new {
  color: #67c23a; /* 绿色 */
}

.existing {
  color: #909399; /* 灰色 */
}

.api {
  color: #e6a23c; /* 橙色 */
}

.label {
  display: block;
  color: #909399;
  font-size: 0.9em;
  margin-top: 5px;
}

.processing-details h4 {
  margin-bottom: 15px;
  color: #333;
}

.details-list {
  max-height: 300px; /* 控制详情列表的高度 */
  overflow-y: auto;
}

.detail-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
  background: #fff;
}

.detail-item.new {
  border-left: 4px solid #67c23a; /* 绿色边框 */
}

.detail-item.existing {
  border-left: 4px solid #909399; /* 灰色边框 */
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.version {
  font-size: 1em;
  font-weight: bold;
  color: #333;
}

.api-calls {
  font-size: 0.8em;
  color: #909399;
}

.detail-message {
  font-size: 0.9em;
  color: #606266;
  line-height: 1.6;
}

.collection-stats {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 1.8em;
  color: #409eff;
}

.stat-info {
  text-align: left;
}

.stat-number {
  font-size: 1.5em;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 0.9em;
  color: #666;
}

.cost-tip {
  padding: 15px;
  border-radius: 6px;
  margin-top: 15px;
  font-size: 0.9em;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cost-tip.success {
  background-color: #67c23a;
}

.cost-tip.info {
  background-color: #409eff;
}
 
 .processing-details {
   margin-top: 20px;
   padding: 15px;
   background: #f9f9f9;
   border-radius: 6px;
   border: 1px solid #e6e6e6;
 }
 
 .processing-details h4 {
   margin: 0 0 15px 0;
   font-size: 1.1em;
   color: #333;
 }
 
 .details-list {
   display: flex;
   flex-direction: column;
   gap: 10px;
 }
 
 .detail-item {
   padding: 12px;
   background: #fff;
   border-radius: 4px;
   border-left: 4px solid #409eff;
   box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
 }
 
 .detail-item.new {
   border-left-color: #67c23a;
 }
 
 .detail-item.existing {
   border-left-color: #909399;
 }
 
 .detail-header {
   display: flex;
   align-items: center;
   gap: 10px;
   margin-bottom: 8px;
 }
 
 .detail-header .version {
   font-weight: bold;
   color: #409eff;
   font-size: 0.95em;
 }
 
 .detail-header .api-calls {
   margin-left: auto;
   font-size: 0.85em;
   padding: 2px 6px;
   border-radius: 4px;
 }
 
 .detail-header .api-calls.cost {
   background-color: #fdf2ec;
   color: #e6a23c;
 }
 
 .detail-header .api-calls.free {
   background-color: #f0f9ff;
   color: #67c23a;
 }
 
 .detail-message {
   font-size: 0.9em;
   color: #666;
   line-height: 1.4;
 }
 
 .collecting-status {
   display: flex;
   align-items: center;
   gap: 10px;
   padding: 15px;
   background: #f0f9ff;
   border-radius: 6px;
   color: #409eff;
   font-weight: 500;
 }
 
 .collecting-status .is-loading {
   font-size: 1.2em;
 }

 .real-time-progress {
   padding: 20px;
   background: #f5f7fa;
   border-radius: 8px;
   margin-bottom: 20px;
 }

 .progress-header {
   display: flex;
   justify-content: space-between;
   align-items: center;
   margin-bottom: 15px;
 }

 .progress-header h4 {
   margin: 0;
   color: #333;
 }

 .status-badge {
   padding: 5px 10px;
   border-radius: 5px;
   font-weight: bold;
   font-size: 0.9em;
 }

 .status-badge.idle {
   background-color: #e1f3d8;
   color: #67c23a;
 }

 .status-badge.processing {
   background-color: #e1f3d8;
   color: #67c23a;
 }

 .status-badge.completed {
   background-color: #e1f3d8;
   color: #67c23a;
 }

 .status-badge.error {
   background-color: #fde2e2;
   color: #f56c6c;
 }

 .current-status {
   display: flex;
   align-items: center;
   gap: 10px;
   margin-bottom: 15px;
   color: #515a6e;
   font-size: 0.95em;
 }

 .status-icon {
   font-size: 1.2em;
 }

 .status-icon.is-loading {
   animation: spin 1s linear infinite;
 }

 .progress-section {
   margin-bottom: 15px;
 }

 .progress-text {
   font-size: 0.9em;
   color: #606266;
 }

 .progress-message {
   font-size: 0.85em;
   color: #909399;
   margin-top: 5px;
 }

 .real-time-stats {
   padding: 15px;
   background: #f9f9f9;
   border-radius: 6px;
   border: 1px solid #e6e6e6;
   margin-top: 15px;
 }

 .version-details {
   margin-top: 15px;
 }

 .version-details h4 {
   margin-bottom: 10px;
   color: #333;
 }

 .version-details .details-list {
   max-height: 300px;
   overflow-y: auto;
 }

 .version-details .detail-item {
   padding: 12px;
   background: #fff;
   border-radius: 4px;
   border-left: 4px solid #409eff;
   box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
 }

 .version-details .detail-item.new {
   border-left-color: #67c23a;
 }

 .version-details .detail-item.existing {
   border-left-color: #909399;
 }

 .version-details .detail-header {
   display: flex;
   align-items: center;
   gap: 10px;
   margin-bottom: 8px;
 }

 .version-details .version {
   font-weight: bold;
   color: #409eff;
   font-size: 0.95em;
 }

 .version-details .api-calls {
   margin-left: auto;
   font-size: 0.85em;
   padding: 2px 6px;
   border-radius: 4px;
 }

 .version-details .api-calls.cost {
   background-color: #fdf2ec;
   color: #e6a23c;
 }

 .version-details .api-calls.free {
   background-color: #f0f9ff;
   color: #67c23a;
 }

 .version-details .processing-time {
   font-size: 0.8em;
   color: #909399;
   margin-left: 10px;
 }

 @keyframes spin {
   from {
     transform: rotate(0deg);
   }
   to {
     transform: rotate(360deg);
   }
 }
</style> 