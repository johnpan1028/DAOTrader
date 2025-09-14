<template>
  <div class="ai-chat">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-left">
        <el-icon class="ai-icon"><Robot /></el-icon>
        <span class="ai-title">指标AI助手</span>
        <el-tag size="small" type="success" v-if="isConnected">在线</el-tag>
        <el-tag size="small" type="danger" v-else>离线</el-tag>
      </div>
      
      <div class="header-right">
        <el-button-group size="small">
          <el-button :icon="Setting" @click="showSettings = true">设置</el-button>
          <el-button :icon="Delete" @click="clearChat">清空</el-button>
          <el-button :icon="Close" @click="$emit('close')">关闭</el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 聊天内容 -->
    <div class="chat-content" ref="chatContent">
      <div class="chat-messages">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-card">
            <el-icon class="welcome-icon"><MagicStick /></el-icon>
            <h3>欢迎使用指标AI助手</h3>
            <p>我可以帮助您：</p>
            <ul>
              <li>用自然语言描述需求，生成麦语言指标代码</li>
              <li>解释和优化现有指标代码</li>
              <li>提供技术指标的使用建议</li>
              <li>修复代码错误和语法问题</li>
            </ul>
            
            <div class="quick-actions">
              <h4>快速开始：</h4>
              <div class="action-buttons">
                <el-button 
                  v-for="template in quickTemplates" 
                  :key="template.id"
                  size="small" 
                  @click="sendQuickMessage(template.message)"
                >
                  {{ template.label }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 聊天消息 -->
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.type]"
        >
          <div class="message-avatar">
            <el-avatar 
              v-if="message.type === 'user'" 
              :icon="UserFilled" 
              :size="32"
            />
            <el-avatar 
              v-else 
              :icon="Robot" 
              :size="32" 
              style="background-color: var(--tv-primary)"
            />
          </div>
          
          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">
                {{ message.type === 'user' ? '您' : 'AI助手' }}
              </span>
              <span class="message-time">
                {{ formatTime(message.timestamp) }}
              </span>
            </div>
            
            <div class="message-body">
              <!-- 文本消息 -->
              <div v-if="message.contentType === 'text'" class="text-content">
                <div v-html="formatMessageContent(message.content)"></div>
              </div>
              
              <!-- 代码消息 -->
              <div v-else-if="message.contentType === 'code'" class="code-content">
                <div class="code-header">
                  <span class="code-title">生成的麦语言代码</span>
                  <div class="code-actions">
                    <el-button 
                      size="small" 
                      :icon="DocumentCopy" 
                      @click="copyCode(message.content.code)"
                    >
                      复制
                    </el-button>
                    <el-button 
                      size="small" 
                      type="primary" 
                      :icon="Position" 
                      @click="insertCode(message.content.code)"
                    >
                      插入编辑器
                    </el-button>
                  </div>
                </div>
                
                <div class="code-block">
                  <pre><code>{{ message.content.code }}</code></pre>
                </div>
                
                <div v-if="message.content.explanation" class="code-explanation">
                  <h4>代码说明：</h4>
                  <div v-html="formatMessageContent(message.content.explanation)"></div>
                </div>
                
                <div v-if="message.content.parameters" class="code-parameters">
                  <h4>参数说明：</h4>
                  <el-table :data="message.content.parameters" size="small">
                    <el-table-column prop="name" label="参数名" width="100" />
                    <el-table-column prop="description" label="说明" />
                    <el-table-column prop="default" label="默认值" width="80" />
                  </el-table>
                </div>
              </div>
              
              <!-- 错误消息 -->
              <div v-else-if="message.contentType === 'error'" class="error-content">
                <el-alert 
                  type="error" 
                  :title="message.content.title || '处理错误'"
                  :description="message.content.message"
                  show-icon
                  :closable="false"
                />
              </div>
              
              <!-- 加载消息 -->
              <div v-else-if="message.contentType === 'loading'" class="loading-content">
                <el-icon class="loading-icon"><Loading /></el-icon>
                <span>{{ message.content || 'AI正在思考中...' }}</span>
              </div>
            </div>
            
            <!-- 消息操作 -->
            <div class="message-actions" v-if="message.type === 'assistant' && message.contentType !== 'loading'">
              <el-button 
                size="small" 
                :icon="Like" 
                @click="rateMessage(index, 'like')"
                :type="message.rating === 'like' ? 'primary' : 'default'"
              >
                有用
              </el-button>
              <el-button 
                size="small" 
                :icon="DisLike" 
                @click="rateMessage(index, 'dislike')"
                :type="message.rating === 'dislike' ? 'danger' : 'default'"
              >
                无用
              </el-button>
              <el-button 
                size="small" 
                :icon="Refresh" 
                @click="regenerateResponse(index)"
              >
                重新生成
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="chat-input">
      <div class="input-toolbar">
        <el-button-group size="small">
          <el-button :icon="Microphone" @click="startVoiceInput" :disabled="isRecording">
            {{ isRecording ? '录音中...' : '语音输入' }}
          </el-button>
          <el-button :icon="Picture" @click="uploadImage">上传图片</el-button>
          <el-button :icon="Document" @click="showTemplates = true">模板</el-button>
        </el-button-group>
        
        <div class="input-status">
          <span v-if="isTyping" class="typing-indicator">
            <el-icon><Loading /></el-icon>
            AI正在输入...
          </span>
        </div>
      </div>
      
      <div class="input-area">
        <el-input 
          v-model="inputMessage" 
          type="textarea" 
          :rows="3"
          placeholder="请描述您想要的指标功能，例如：'创建一个双均线交叉指标'、'生成MACD背离提醒'等..."
          @keydown.ctrl.enter="sendMessage"
          @keydown.meta.enter="sendMessage"
          :disabled="isTyping"
          resize="none"
        />
        
        <div class="input-actions">
          <div class="input-hint">
            <el-icon><InfoFilled /></el-icon>
            <span>Ctrl+Enter 发送消息</span>
          </div>
          
          <el-button 
            type="primary" 
            :icon="Promotion" 
            @click="sendMessage"
            :loading="isTyping"
            :disabled="!inputMessage.trim()"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="AI助手设置" width="500px">
      <el-form :model="settings" label-width="120px">
        <el-form-item label="AI模型">
          <el-select v-model="settings.model" style="width: 100%">
            <el-option label="GPT-4" value="gpt-4" />
            <el-option label="GPT-3.5 Turbo" value="gpt-3.5-turbo" />
            <el-option label="Claude-3" value="claude-3" />
            <el-option label="本地模型" value="local" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="创造性">
          <el-slider 
            v-model="settings.temperature" 
            :min="0" 
            :max="1" 
            :step="0.1" 
            show-stops
            show-tooltip
          />
          <div class="slider-labels">
            <span>保守</span>
            <span>创新</span>
          </div>
        </el-form-item>
        
        <el-form-item label="响应长度">
          <el-radio-group v-model="settings.responseLength">
            <el-radio label="short">简洁</el-radio>
            <el-radio label="medium">适中</el-radio>
            <el-radio label="long">详细</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="代码风格">
          <el-checkbox-group v-model="settings.codeStyle">
            <el-checkbox label="comments">添加注释</el-checkbox>
            <el-checkbox label="optimization">性能优化</el-checkbox>
            <el-checkbox label="validation">参数验证</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="自动插入">
          <el-switch 
            v-model="settings.autoInsert" 
            active-text="生成代码后自动插入编辑器"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showSettings = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 模板对话框 -->
    <el-dialog v-model="showTemplates" title="常用模板" width="600px">
      <div class="template-grid">
        <div 
          v-for="template in messageTemplates" 
          :key="template.id" 
          class="template-card"
          @click="useTemplate(template)"
        >
          <div class="template-header">
            <el-icon>{{ template.icon }}</el-icon>
            <h4>{{ template.title }}</h4>
          </div>
          <p class="template-description">{{ template.description }}</p>
          <div class="template-example">{{ template.example }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Robot,
  UserFilled,
  Setting,
  Delete,
  Close,
  MagicStick,
  DocumentCopy,
  Position,
  Like,
  DisLike,
  Refresh,
  Microphone,
  Picture,
  Document,
  InfoFilled,
  Promotion,
  Loading
} from '@element-plus/icons-vue'

// Props & Emits
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'insert-code'])

// 响应式数据
const chatContent = ref(null)
const inputMessage = ref('')
const messages = ref([])
const isTyping = ref(false)
const isRecording = ref(false)
const isConnected = ref(true)

// 对话框状态
const showSettings = ref(false)
const showTemplates = ref(false)

// 设置
const settings = ref({
  model: 'gpt-4',
  temperature: 0.7,
  responseLength: 'medium',
  codeStyle: ['comments'],
  autoInsert: false
})

// 快速模板
const quickTemplates = ref([
  { id: 1, label: '双均线指标', message: '帮我创建一个双均线交叉指标，5日线和20日线' },
  { id: 2, label: 'MACD指标', message: '生成一个标准的MACD指标代码' },
  { id: 3, label: 'RSI指标', message: '创建RSI相对强弱指标，周期14' },
  { id: 4, label: '布林带指标', message: '生成布林带指标，周期20，标准差2' }
])

// 消息模板
const messageTemplates = ref([
  {
    id: 1,
    title: '趋势指标',
    description: '创建各种趋势跟踪指标',
    example: '帮我创建一个[指标名称]，参数为[具体参数]',
    icon: 'TrendCharts'
  },
  {
    id: 2,
    title: '震荡指标',
    description: '生成RSI、KDJ等震荡类指标',
    example: '生成一个RSI指标，周期为14，超买线70，超卖线30',
    icon: 'DataAnalysis'
  },
  {
    id: 3,
    title: '成交量指标',
    description: '基于成交量的技术指标',
    example: '创建一个成交量移动平均线，周期20',
    icon: 'DataBoard'
  },
  {
    id: 4,
    title: '自定义策略',
    description: '复合条件的交易策略指标',
    example: '当5日均线上穿20日均线且RSI小于30时发出买入信号',
    icon: 'Lightning'
  }
])

// 监听器
watch(() => props.visible, (visible) => {
  if (visible) {
    nextTick(() => {
      scrollToBottom()
    })
  }
})

watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

// 组件挂载
onMounted(() => {
  loadSettings()
  loadChatHistory()
})

// 组件卸载
onUnmounted(() => {
  saveChatHistory()
})

// 发送消息
function sendMessage() {
  const message = inputMessage.value.trim()
  if (!message || isTyping.value) return
  
  // 添加用户消息
  addMessage({
    type: 'user',
    contentType: 'text',
    content: message,
    timestamp: Date.now()
  })
  
  inputMessage.value = ''
  
  // 发送到AI处理
  processAIRequest(message)
}

// 快速发送消息
function sendQuickMessage(message) {
  inputMessage.value = message
  sendMessage()
}

// 处理AI请求
async function processAIRequest(userMessage) {
  isTyping.value = true
  
  // 添加加载消息
  const loadingMessageIndex = addMessage({
    type: 'assistant',
    contentType: 'loading',
    content: 'AI正在分析您的需求...',
    timestamp: Date.now()
  })
  
  try {
    // 调用AI API
    const response = await callAIAPI(userMessage)
    
    // 移除加载消息
    messages.value.splice(loadingMessageIndex, 1)
    
    // 添加AI响应
    addMessage({
      type: 'assistant',
      contentType: response.type || 'text',
      content: response.content,
      timestamp: Date.now()
    })
    
    // 自动插入代码
    if (settings.value.autoInsert && response.type === 'code') {
      insertCode(response.content.code)
    }
    
  } catch (error) {
    // 移除加载消息
    messages.value.splice(loadingMessageIndex, 1)
    
    // 添加错误消息
    addMessage({
      type: 'assistant',
      contentType: 'error',
      content: {
        title: 'AI处理失败',
        message: error.message || '网络连接异常，请稍后重试'
      },
      timestamp: Date.now()
    })
  } finally {
    isTyping.value = false
  }
}

// 调用AI API
async function callAIAPI(message) {
  // 构建请求数据
  const requestData = {
    message: message,
    context: getConversationContext(),
    settings: settings.value,
    indicators: getAvailableIndicators()
  }
  
  // 发送请求
  const response = await fetch('/api/ai/indicator-chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestData)
  })
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  
  return await response.json()
}

// 获取对话上下文
function getConversationContext() {
  return messages.value
    .filter(msg => msg.contentType !== 'loading')
    .slice(-10) // 只保留最近10条消息作为上下文
    .map(msg => ({
      role: msg.type === 'user' ? 'user' : 'assistant',
      content: typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)
    }))
}

// 获取可用指标列表
function getAvailableIndicators() {
  // 这里应该从指标管理系统获取
  return [
    'MA', 'EMA', 'SMA', 'WMA', 'DMA',
    'MACD', 'KDJ', 'RSI', 'BOLL', 'ATR',
    'CCI', 'ROC', 'BIAS', 'PSY', 'VR'
  ]
}

// 添加消息
function addMessage(message) {
  messages.value.push(message)
  return messages.value.length - 1
}

// 复制代码
function copyCode(code) {
  navigator.clipboard.writeText(code).then(() => {
    ElMessage.success('代码已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 插入代码到编辑器
function insertCode(code) {
  emit('insert-code', code)
  ElMessage.success('代码已插入到编辑器')
}

// 评价消息
function rateMessage(index, rating) {
  messages.value[index].rating = rating
  
  // 发送反馈到服务器
  sendFeedback(messages.value[index], rating)
  
  ElMessage.success(rating === 'like' ? '感谢您的反馈' : '我们会继续改进')
}

// 重新生成响应
function regenerateResponse(index) {
  const message = messages.value[index]
  if (message.type !== 'assistant') return
  
  // 找到对应的用户消息
  let userMessageIndex = index - 1
  while (userMessageIndex >= 0 && messages.value[userMessageIndex].type !== 'user') {
    userMessageIndex--
  }
  
  if (userMessageIndex >= 0) {
    const userMessage = messages.value[userMessageIndex].content
    
    // 移除当前AI响应
    messages.value.splice(index, 1)
    
    // 重新处理
    processAIRequest(userMessage)
  }
}

// 清空聊天
function clearChat() {
  ElMessageBox.confirm('确定要清空所有聊天记录吗？', '确认清空', {
    type: 'warning'
  }).then(() => {
    messages.value = []
    ElMessage.success('聊天记录已清空')
  }).catch(() => {})
}

// 语音输入
function startVoiceInput() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    ElMessage.error('您的浏览器不支持语音识别')
    return
  }
  
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  const recognition = new SpeechRecognition()
  
  recognition.lang = 'zh-CN'
  recognition.continuous = false
  recognition.interimResults = false
  
  recognition.onstart = () => {
    isRecording.value = true
  }
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript
    inputMessage.value = transcript
  }
  
  recognition.onerror = (event) => {
    ElMessage.error(`语音识别失败: ${event.error}`)
  }
  
  recognition.onend = () => {
    isRecording.value = false
  }
  
  recognition.start()
}

// 上传图片
function uploadImage() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  
  input.onchange = (event) => {
    const file = event.target.files[0]
    if (file) {
      // 处理图片上传逻辑
      ElMessage.info('图片上传功能开发中...')
    }
  }
  
  input.click()
}

// 使用模板
function useTemplate(template) {
  inputMessage.value = template.example
  showTemplates.value = false
}

// 保存设置
function saveSettings() {
  localStorage.setItem('ai-chat-settings', JSON.stringify(settings.value))
  showSettings.value = false
  ElMessage.success('设置已保存')
}

// 加载设置
function loadSettings() {
  const saved = localStorage.getItem('ai-chat-settings')
  if (saved) {
    try {
      settings.value = { ...settings.value, ...JSON.parse(saved) }
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }
}

// 保存聊天历史
function saveChatHistory() {
  const history = messages.value.filter(msg => msg.contentType !== 'loading')
  localStorage.setItem('ai-chat-history', JSON.stringify(history))
}

// 加载聊天历史
function loadChatHistory() {
  const saved = localStorage.getItem('ai-chat-history')
  if (saved) {
    try {
      messages.value = JSON.parse(saved)
    } catch (error) {
      console.error('加载聊天历史失败:', error)
    }
  }
}

// 发送反馈
function sendFeedback(message, rating) {
  // 发送反馈到服务器用于改进AI
  fetch('/api/ai/feedback', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      messageId: message.timestamp,
      rating: rating,
      content: message.content
    })
  }).catch(error => {
    console.error('发送反馈失败:', error)
  })
}

// 滚动到底部
function scrollToBottom() {
  if (chatContent.value) {
    chatContent.value.scrollTop = chatContent.value.scrollHeight
  }
}

// 格式化时间
function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString()
}

// 格式化消息内容
function formatMessageContent(content) {
  if (typeof content !== 'string') return content
  
  // 简单的Markdown渲染
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.ai-chat {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--tv-bg-secondary);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-icon {
  color: var(--tv-primary);
  font-size: 20px;
}

.ai-title {
  font-weight: 500;
  color: var(--tv-text-primary);
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.welcome-card {
  text-align: center;
  max-width: 500px;
  padding: 32px;
  border: 1px solid var(--tv-border-primary);
  border-radius: 8px;
  background: var(--tv-bg-primary);
}

.welcome-icon {
  font-size: 48px;
  color: var(--tv-primary);
  margin-bottom: 16px;
}

.welcome-card h3 {
  margin: 0 0 16px 0;
  color: var(--tv-text-primary);
}

.welcome-card p {
  margin: 0 0 16px 0;
  color: var(--tv-text-secondary);
}

.welcome-card ul {
  text-align: left;
  margin: 0 0 24px 0;
  color: var(--tv-text-secondary);
}

.quick-actions h4 {
  margin: 0 0 12px 0;
  color: var(--tv-text-primary);
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.message {
  display: flex;
  margin-bottom: 24px;
  align-items: flex-start;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message.user .message-content {
  text-align: right;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message.user .message-header {
  flex-direction: row-reverse;
}

.message-sender {
  font-weight: 500;
  color: var(--tv-text-primary);
}

.message-time {
  font-size: 12px;
  color: var(--tv-text-secondary);
}

.message-body {
  background: var(--tv-bg-overlay);
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid var(--tv-border-primary);
}

.message.user .message-body {
  background: var(--tv-primary);
  color: var(--tv-text-inverse);
}

.text-content {
  line-height: 1.6;
}

.code-content {
  background: var(--tv-bg-secondary);
  border: 1px solid var(--tv-border-primary);
  border-radius: 4px;
  overflow: hidden;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--tv-bg-primary);
  border-bottom: 1px solid var(--tv-border-primary);
}

.code-title {
  font-weight: 500;
  color: var(--tv-text-primary);
}

.code-actions {
  display: flex;
  gap: 8px;
}

.code-block {
  padding: 16px;
  background: var(--tv-bg-overlay);
  overflow-x: auto;
}

.code-block pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.4;
}

.code-explanation,
.code-parameters {
  padding: 12px;
  border-top: 1px solid var(--tv-border-primary);
}

.code-explanation h4,
.code-parameters h4 {
  margin: 0 0 8px 0;
  color: var(--tv-text-primary);
  font-size: 14px;
}

.error-content {
  background: var(--tv-bg-secondary);
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--tv-text-secondary);
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.chat-input {
  border-top: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-secondary);
}

.input-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-primary);
}

.input-status {
  color: var(--tv-text-secondary);
  font-size: 12px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.input-area {
  padding: 16px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--tv-text-secondary);
  font-size: 12px;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 12px;
  color: var(--tv-text-secondary);
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.template-card {
  padding: 16px;
  border: 1px solid var(--tv-border-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-card:hover {
  border-color: var(--tv-primary);
  box-shadow: 0 2px 8px var(--tv-shadow-primary);
}

.template-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.template-header h4 {
  margin: 0;
  color: var(--tv-text-primary);
}

.template-description {
  margin: 0 0 8px 0;
  color: var(--tv-text-secondary);
  font-size: 14px;
}

.template-example {
  padding: 8px;
  background: var(--tv-bg-overlay);
  border-radius: 4px;
  font-size: 12px;
  color: var(--tv-text-secondary);
  font-style: italic;
}
</style>