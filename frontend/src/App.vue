<template>
  <el-container class="trading-app">
    <!-- 顶部导航栏 - TradingView风格 -->
    <el-header 
      height="44px" 
      :style="{ 
        background: 'var(--tv-bg-secondary)', 
        borderBottom: '1px solid var(--tv-border-primary)',
        padding: '0 12px',
        boxShadow: 'none'
      }"
    >
      <el-row justify="space-between" align="middle" :style="{ height: '100%' }">
        <!-- 左侧：品牌 + 股票信息 -->
        <el-col :span="8">
          <el-space>
            <el-space :size="8" align="center">
               <el-icon size="20" color="var(--el-color-primary)"><TrendCharts /></el-icon>
               <el-text size="default" tag="b" :style="{ color: 'var(--tv-accent-primary)', fontWeight: 'bold' }">DAOTrader</el-text>
             </el-space>
            <el-divider direction="vertical" :style="{ borderColor: 'var(--el-border-color-light)' }" />
            <el-space direction="vertical" :size="4">
              <el-input 
                v-model="symbolSearch" 
                placeholder="搜索品种" 
                size="small"
                :style="{ width: '140px' }"
                :prefix-icon="Search"
                clearable
              />
              <el-space :size="8" align="center">
                <el-text size="small" :style="{ color: 'var(--tv-text-primary)' }">{{ currentSymbol }}</el-text>
                <el-text size="small" :style="{ color: priceChangeClass === 'positive' ? 'var(--el-color-success)' : 'var(--el-color-danger)' }">{{ currentPrice }}</el-text>
                <el-text size="small" :style="{ color: priceChangeClass === 'positive' ? 'var(--el-color-success)' : 'var(--el-color-danger)' }">{{ priceChange }}</el-text>
              </el-space>
            </el-space>
          </el-space>
        </el-col>
        
        <!-- 中央：时间周期 + 图表类型 -->
        <el-col :span="8" :style="{ textAlign: 'center' }">
          <el-space>
            <el-radio-group 
              v-model="timeframe" 
              size="small" 
              :style="{ 
                background: 'var(--tv-bg-tertiary)', 
                borderRadius: '6px', 
                padding: '2px' 
              }"
            >
              <el-radio-button value="1m">1m</el-radio-button>
              <el-radio-button value="5m">5m</el-radio-button>
              <el-radio-button value="15m">15m</el-radio-button>
              <el-radio-button value="1h">1h</el-radio-button>
              <el-radio-button value="1d">1D</el-radio-button>
            </el-radio-group>
            
            <el-button-group 
              size="small" 
              :style="{ 
                background: 'var(--tv-bg-tertiary)', 
                borderRadius: '6px', 
                padding: '2px' 
              }"
            >
              <el-button 
                :type="chartType === 'candle' ? 'primary' : ''" 
                @click="chartType = 'candle'"
                :icon="Grid"
                :style="{ 
                  background: chartType === 'candle' ? 'var(--tv-accent-primary)' : 'transparent',
                  color: chartType === 'candle' ? 'var(--tv-text-on-accent)' : 'var(--tv-text-secondary)',
                  border: 'none'
                }"
              />
              <el-button 
                :type="chartType === 'line' ? 'primary' : ''" 
                @click="chartType = 'line'"
                :icon="Connection"
                :style="{ 
                  background: chartType === 'line' ? 'var(--tv-accent-primary)' : 'transparent',
                  color: chartType === 'line' ? 'var(--tv-text-on-accent)' : 'var(--tv-text-secondary)',
                  border: 'none'
                }"
              />
            </el-button-group>
          </el-space>
        </el-col>
        
        <!-- 右侧：功能按钮 -->
        <el-col :span="8" :style="{ textAlign: 'right' }">
          <el-space>
            <el-button size="small" :icon="DataAnalysis" text>指标</el-button>
            <el-button size="small" :icon="Camera" text>截图</el-button>
            <el-button size="small" :icon="Setting" text />
            <el-button size="small" :icon="FullScreen" text @click="toggleFullscreen" />
          </el-space>
        </el-col>
      </el-row>
    </el-header>

    <!-- 主体内容区 -->
     <el-main :style="{ height: 'calc(100vh - 44px)', padding: '0' }">
      <el-container direction="horizontal" :style="{ height: '100%' }">
        <!-- 左边栏 -->
        <el-aside 
          width="52px" 
          :style="{ 
            background: 'var(--tv-bg-secondary)', 
            borderRight: '4px solid var(--tv-border-primary)',
            height: '100%'
          }"
        >
          <el-scrollbar :style="{ height: '100%' }">
            <div :style="{ padding: '8px 4px', textAlign: 'center', fontSize: '12px', color: 'var(--tv-text-primary)' }">
              左边栏内容
            </div>
          </el-scrollbar>
        </el-aside>
        
        <!-- 中间区域 -->
        <el-main 
          :style="{ 
            background: 'var(--tv-bg-primary)', 
            padding: '0',
            minWidth: '300px',
            height: '100%'
          }"
        >
          <el-scrollbar :style="{ height: '100%' }">
            <div :style="{ padding: '16px', height: '100%', color: 'var(--tv-text-primary)' }">
              中间区域内容
            </div>
          </el-scrollbar>
        </el-main>
        
        <!-- 右侧分割线 -->
        <el-divider 
          direction="vertical" 
          :style="{ 
            width: '4px', 
            height: '100%', 
            background: isDividerHovered ? 'var(--tv-accent-primary)' : 'var(--tv-border-primary)',
            cursor: 'col-resize',
            margin: '0',
            borderColor: 'var(--tv-border-primary)',
            transition: 'background-color 0.2s'
          }"
          @mousedown="startResize('right', $event)"
          @mouseenter="isDividerHovered = true"
          @mouseleave="isDividerHovered = false"
        />
        
        <!-- 右边栏 -->
        <el-aside 
          :width="rightPanelWidth + 'px'" 
          :style="{ 
            background: 'var(--tv-bg-secondary)', 
            borderLeft: '4px solid var(--tv-border-primary)',
            minWidth: '150px',
            maxWidth: '500px',
            height: '100%'
          }"
        >
          <el-scrollbar :style="{ height: '100%' }">
            <div :style="{ padding: '16px', height: '100%', color: 'var(--tv-text-primary)' }">
              右边栏内容
            </div>
          </el-scrollbar>
        </el-aside>
      </el-container>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  TrendCharts,
  Setting,
  FullScreen,
  Search,
  Grid,
  Connection,
  DataAnalysis,
  Camera
} from '@element-plus/icons-vue'

// 基础响应式数据
const symbolSearch = ref('')
const timeframe = ref('15m')
const chartType = ref('candle')
const isDividerHovered = ref(false)

// 股票信息
const currentSymbol = ref('BTCUSDT')
const currentPrice = ref('43,250.50')
const priceChange = ref('+1,250.50 (+2.98%)')
const priceChangeClass = computed(() => {
  return priceChange.value.startsWith('+') ? 'positive' : 'negative'
})

// 响应式布局相关
const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 768)

// 面板宽度控制
const leftPanelWidth = ref(52)
const rightPanelWidth = ref(250)
const isResizing = ref(false)
const resizeType = ref('')
const startX = ref(0)
const startWidth = ref(0)

// 拖拽调整大小方法（仅右边栏）
const startResize = (type: string, event: MouseEvent) => {
  if (type !== 'right') return // 只允许调整右边栏
  
  isResizing.value = true
  resizeType.value = type
  startX.value = event.clientX
  startWidth.value = rightPanelWidth.value
  
  // 添加拖拽状态类名
  document.body.classList.add('resizing')
  
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  event.preventDefault()
}

const handleResize = (event: MouseEvent) => {
  if (!isResizing.value || resizeType.value !== 'right') return
  
  const deltaX = event.clientX - startX.value
  const newWidth = startWidth.value - deltaX
  rightPanelWidth.value = Math.max(150, Math.min(500, newWidth))
}

const stopResize = () => {
  isResizing.value = false
  resizeType.value = ''
  
  // 移除拖拽状态类名
  document.body.classList.remove('resizing')
  
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

// 基础方法
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

onMounted(() => {
  console.log('简化版TradingView界面已加载')
  
  // 监听窗口大小变化
  const handleResize = () => {
    windowWidth.value = window.innerWidth
  }
  
  window.addEventListener('resize', handleResize)
  
  // 清理监听器
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })
})
</script>

<style>
/* 引入TradingView主题样式 */
@import './styles/tradingview-theme.css';

/* 全局样式重置 */
* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}

/* Element Plus 组件样式重置 */
.el-container {
  margin: 0;
  padding: 0;
}

.el-header {
  margin: 0;
  padding: 0;
}

.el-aside {
  margin: 0;
  padding: 0;
}

.el-main {
  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100vw;
  font-family: var(--tv-font-family);
  background-color: var(--tv-bg-primary);
  color: var(--tv-text-primary);
  position: relative;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
}
</style>

<style scoped>

/* Element Plus 暗色主题变量 */
:root {
  --el-bg-color: var(--tv-bg-secondary);
  --el-bg-color-page: var(--tv-bg-primary);
  --el-bg-color-overlay: var(--tv-bg-tertiary);
  --el-text-color-primary: var(--tv-text-primary);
  --el-text-color-regular: var(--tv-text-secondary);
  --el-text-color-secondary: var(--tv-text-tertiary);
  --el-border-color: var(--tv-border-primary);
  --el-border-color-light: var(--tv-border-secondary);
  --el-color-primary: var(--tv-accent-primary);
  --el-color-success: var(--tv-color-success);
  --el-color-danger: var(--tv-color-danger);
  --el-color-warning: var(--tv-color-warning);
  --el-color-info: var(--tv-text-secondary);
}

/* 基础布局样式 - 使用Element组件控制 */
.trading-app {
  height: 100vh;
  width: 100vw;
  background: var(--tv-bg-primary);
  color: var(--tv-text-primary);
  font-family: var(--tv-font-family);
  overflow: hidden;
  margin: 0;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
}

/* 拖拽时的全局样式 */
body.resizing {
  cursor: col-resize;
  user-select: none;
}

body.resizing * {
  pointer-events: none;
}

/* 左侧工具栏 - TradingView风格 */
.left-toolbar {
  flex-shrink: 0;
  background: var(--tv-bg-secondary);
  border-right: 1px solid var(--tv-border-primary);
  overflow: hidden;
  position: fixed;
  left: 0;
  top: 60px;
  bottom: 0;
  width: 48px;
  z-index: 100;
  margin: 0;
  padding: 0;
}

.toolbar-section {
  padding: 0 4px 8px 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.toolbar-section:first-child {
  padding-top: 0;
}

.tool-category {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.tool-category:first-child {
  margin-top: 0;
}

.toolbar-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--tv-text-secondary);
  border-radius: 4px;
  transition: all 0.2s ease;
}

.toolbar-btn:hover {
  background: var(--tv-accent-primary-alpha);
  color: var(--tv-text-primary);
}

.toolbar-btn.el-button--primary {
  background: var(--tv-accent-primary);
  color: var(--tv-text-on-accent);
}

.toolbar-btn.el-button--primary:hover {
  background: var(--tv-accent-primary);
  opacity: 0.8;
}

/* 中央内容区域 - TradingView风格 */
.central-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  background: var(--tv-bg-primary);
}

.chart-main {
  flex: 1;
  padding: 0;
  overflow: hidden;
  background: var(--tv-bg-primary);
}

.chart-container {
  width: 100%;
  height: 100%;
  background: var(--tv-bg-primary);
  border: none;
  border-radius: 0;
}

/* 右侧面板 */
.right-panel {
  flex-shrink: 0;
  overflow-y: auto;
  height: 100%;
}

/* 图表区域 */
.chart-area {
  padding: 0;
  overflow: hidden;
  height: 100%;
}

/* 底部面板 - TradingView风格 */
.bottom-panel {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--tv-bg-secondary);
  border-top: 1px solid var(--tv-border-primary);
}

/* 工具类 - TradingView风格涨跌颜色 */
.positive, .price-up {
  color: var(--el-color-success) !important;
}

.negative, .price-down {
  color: var(--el-color-danger) !important;
}

/* 顶部导航栏样式已通过Element组件控制 */

/* 品牌和股票信息样式已通过Element组件控制 */

/* 价格和时间周期样式已通过Element组件控制 */


/* Element Plus 组件主题覆盖 - 保留必要的深度样式 */
:deep(.el-input) {
  --el-input-bg-color: var(--el-bg-color-overlay);
  --el-input-border-color: var(--el-border-color);
  --el-input-hover-border-color: var(--el-border-color-light);
  --el-input-focus-border-color: var(--el-color-primary);
  --el-input-text-color: var(--el-text-color-primary);
}

:deep(.el-button) {
  --el-button-bg-color: var(--tv-bg-tertiary);
  --el-button-border-color: var(--tv-border-primary);
  --el-button-text-color: var(--tv-text-primary);
  --el-button-hover-bg-color: var(--tv-accent-primary);
  --el-button-hover-text-color: var(--tv-text-on-accent);
}

:deep(.el-button--primary) {
  --el-button-bg-color: var(--tv-accent-primary);
  --el-button-border-color: var(--tv-accent-primary);
  --el-button-text-color: var(--tv-text-on-accent);
}

:deep(.el-radio-button) {
  --el-radio-button-checked-bg-color: var(--el-color-primary);
  --el-radio-button-checked-text-color: #ffffff;
  --el-radio-button-bg-color: var(--el-bg-color-overlay);
  --el-radio-button-text-color: var(--el-text-color-regular);
}

/* 响应式布局 */
@media (max-width: 767px) {
  .hidden-xs-only {
    display: none !important;
  }
  
  .main-content {
    flex-direction: column;
  }
  
  .left-toolbar {
    display: none;
  }
  
  .right-panel {
    display: none;
  }
  
  .central-content {
    width: 100%;
  }
  
  .chart-container {
    height: 250px !important;
  }
  
  .bottom-panel {
    min-height: 200px;
  }
  
  .tab-content {
    padding: 8px;
  }
  
  :deep(.el-header) {
    padding: 0 8px;
    flex-wrap: wrap;
    height: auto !important;
    min-height: 60px;
  }
  
  :deep(.el-col) {
    margin-bottom: 8px;
  }
}

/* 响应式布局通过Element组件的props控制 */
@media (max-width: 767px) {
  /* 移动端特殊样式保留 */
  .trading-app {
    font-size: 14px;
  }
}
</style>



