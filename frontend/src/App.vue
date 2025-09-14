<template>
  <el-container class="trading-app">
    <!-- 顶部导航栏 - TradingView风格 -->
    <el-header 
      height="44px" 
      :style="{ 
        background: 'var(--tv-bg-secondary)', 
        borderBottom: '4px solid var(--tv-border-primary)',
        padding: '0 12px',
        boxShadow: 'none'
      }"
    >
      <!-- 顶栏：从左到右布局（品牌 | 合约 | 时间粒度 | 图表类型 | 功能按钮） -->
      <div :style="{ display: 'flex', alignItems: 'center', height: '100%', gap: '10px' }">
        <!-- 品牌 -->
        <el-space :size="8" align="center">
          <el-icon size="20" color="var(--el-color-primary)"><TrendCharts /></el-icon>
          <el-text size="default" tag="b" :style="{ color: 'var(--tv-accent-primary)', fontWeight: 'bold' }">DAOTrader |</el-text>
        </el-space>

        <el-divider direction="vertical" :style="{ borderColor: 'var(--el-border-color-light)', margin: '0 6px' }" />

        <!-- 当前合约简称（点击弹出搜索栏） -->
        <el-tag size="small" type="warning" effect="dark" style="cursor: pointer;" @click="symbolSearchDialogVisible = true">{{ currentSymbol }}</el-tag>

        <el-divider direction="vertical" :style="{ borderColor: 'var(--el-border-color-light)', margin: '0 6px' }" />

        <!-- 时间粒度组 -->
        <el-radio-group 
          v-model="timeframe" 
          size="small" 
          :style="{ background: 'var(--tv-bg-overlay)', borderRadius: '6px', padding: '2px' }"
        >
          <el-radio-button value="1m">1m</el-radio-button>
          <el-radio-button value="5m">5m</el-radio-button>
          <el-radio-button value="15m">15m</el-radio-button>
          <el-radio-button value="1H">1H</el-radio-button>
          <el-radio-button value="2H">2H</el-radio-button>
          <el-radio-button value="4H">4H</el-radio-button>
          <el-radio-button value="D">D</el-radio-button>
          <el-radio-button value="W">W</el-radio-button>
          <el-radio-button value="M">M</el-radio-button>
          <el-radio-button value="Y">Y</el-radio-button>
        </el-radio-group>



        <div style="flex: 1 1 auto"></div>

        <!-- 功能按钮：指标 / 时区 / 设置 / 截图 / 全屏 -->
        <el-space>
          <el-button size="small" :icon="DataAnalysis" text @click="indicatorDialogVisible = true">指标</el-button>
          <el-button size="small" :icon="Timer" text>时区</el-button>
          <el-button size="small" :icon="Setting" text>设置</el-button>
          <el-button size="small" :icon="Camera" text>截图</el-button>
          <el-button size="small" :icon="FullScreen" text @click="toggleFullscreen">全屏</el-button>
        </el-space>
      </div>
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
            height: '100%',
            overflow: 'hidden'
          }"
        >
          <el-container direction="vertical" :style="{ height: '100%', overflow: 'hidden', position: 'relative' }">
            <!-- 上方：K线图表区域 -->
            <el-main :style="klineAreaStyle">
              <KLineChart ref="klineChartRef" :chart-type="chartType as any" :indicators="indicatorState" />
            </el-main>
            
            <!-- 拖拽手柄 -->
            <el-divider 
              direction="horizontal"
              class="resize-handle"
              :style="dividerStyle"
              @mousedown="startBottomResize"

            >
              <!-- 拖拽指示器 -->
              <div :style="{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '40px',
                height: '2px',
                background: 'var(--tv-text-secondary)',
                borderRadius: '1px',
                pointerEvents: 'none'
              }"></div>
            </el-divider>
            
            <!-- 底部：标签页容器 -->
            <el-footer 
              :style="bottomFooterStyle"
            >
              <div class="bottom-tabs-container">
                <el-tabs 
                  v-model="activeTab" 
                  :style="{
                    height: '100%',
                    '--el-tabs-header-height': '40px'
                  }"
                  class="bottom-tabs"
                >
                  <div class="bottom-panel-controls">
                    <el-button
                      :icon="isBottomMaximized ? ArrowDown : ArrowUp"
                      size="small"
                      text
                      @click="toggleBottomPanel"
                      :title="isBottomMaximized ? '最小化' : '最大化'"
                      class="panel-toggle-btn"
                    />
                  </div>
                <el-tab-pane label="策略测试" name="strategy">
                  <div :style="{ 
                    height: 'calc(100% - 40px)', 
                    color: 'var(--tv-text-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    overflow: 'hidden',
                    padding: '8px'
                  }">
                    策略测试内容区域
                  </div>
                </el-tab-pane>
                
                <el-tab-pane label="回放交易" name="replay">
                  <div :style="{ 
                    height: 'calc(100% - 40px)', 
                    color: 'var(--tv-text-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    overflow: 'hidden',
                    padding: '8px'
                  }">
                    回放交易内容区域
                  </div>
                </el-tab-pane>
                
                <el-tab-pane label="交易面板" name="trading">
                  <div :style="{ 
                    height: 'calc(100% - 40px)', 
                    color: 'var(--tv-text-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    overflow: 'hidden',
                    padding: '8px'
                  }">
                    交易面板内容区域 (高度: {{ bottomPanelHeight }}px)
                  </div>
                </el-tab-pane>
              </el-tabs>
              </div>
            </el-footer>
          </el-container>
        </el-main>
        
        <!-- 右侧分割线 -->
        <el-divider 
          direction="vertical" 
          :style="{ 
            width: '4px', 
            height: '100%', 
            background: 'var(--tv-border-primary)',
            border: 'none',
            cursor: isRightResizing ? 'grabbing' : 'grab',
            margin: '0',
            transition: 'background 0.2s'
          }"
          @mousedown="startResize('right', $event)"

        />
        
        <!-- 右边栏 -->
        <el-aside 
          :width="rightPanelWidth + 'px'" 
          :style="{ 
            background: 'var(--tv-bg-secondary)', 
            minWidth: '150px',
            maxWidth: '500px',
            height: '100%',
            borderLeft: '1px solid var(--tv-border-primary)'
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

    <!-- 指标弹窗 -->
    <el-dialog v-model="indicatorDialogVisible" title="技术指标" width="420px" append-to-body>
      <div>
        <!-- 主图指标 -->
        <el-divider content-position="left">主图指标</el-divider>
        <div style="margin-bottom: 16px;">
          <div style="margin-bottom: 8px; color: var(--el-text-color-regular); font-size: 12px;">内置指标</div>
          <el-checkbox v-model="indicatorState.ma" style="display: block; margin-bottom: 8px;">MA(移动平均线)</el-checkbox>
          <el-checkbox disabled style="display: block; margin-bottom: 8px;">EMA(未来可扩展)</el-checkbox>
          <el-checkbox disabled style="display: block; margin-bottom: 8px;">BOLL(未来可扩展)</el-checkbox>
        </div>
        <div style="margin-bottom: 16px;">
          <div style="margin-bottom: 8px; color: var(--el-color-primary); font-size: 12px;">自定义指标</div>
          <el-checkbox v-model="indicatorState.custom_ma" style="display: block; margin-bottom: 8px;">
            <span class="custom-indicator-label" :class="{ active: indicatorState.custom_ma }">自定义XMA</span>
            <el-tag size="small" type="info" style="margin-left: 8px;">自定义</el-tag>
          </el-checkbox>
        </div>

        <!-- 副图指标 -->
        <el-divider content-position="left">副图指标</el-divider>
        <div style="margin-bottom: 16px;">
          <div style="margin-bottom: 8px; color: var(--el-text-color-regular); font-size: 12px;">内置指标</div>
          <el-checkbox v-model="indicatorState.vol" style="display: block; margin-bottom: 8px;">VOL(成交量)</el-checkbox>
          <el-checkbox v-model="indicatorState.macd" style="display: block; margin-bottom: 8px;">MACD</el-checkbox>
        </div>
        <div>
          <div style="margin-bottom: 8px; color: var(--el-color-primary); font-size: 12px;">自定义指标</div>
          <el-checkbox v-model="indicatorState.custom_rsi" style="display: block; margin-bottom: 8px;">
            <span class="custom-indicator-label" :class="{ active: indicatorState.custom_rsi }">自定义X RSI</span>
            <el-tag size="small" type="info" style="margin-left: 8px;">自定义</el-tag>
          </el-checkbox>
        </div>
      </div>
    </el-dialog>

    <!-- 金融商品搜索弹窗 -->
    <el-dialog
      v-model="symbolSearchDialogVisible"
      title="商品代码搜索"
      width="800px"
      :modal="true"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      class="symbol-search-dialog"
      :show-close="true"
      append-to-body
    >
      <div class="search-container">
        <!-- 搜索框 -->
        <div class="search-header">
          <el-input
            v-model="searchKeyword"
            placeholder="输入商品代码或名称搜索..."
            :prefix-icon="Search"
            clearable
            class="search-input"
            size="large"
          />
        </div>
        
        <!-- 分类标签 -->
        <div class="category-tabs">
          <el-button
            v-for="category in categories"
            :key="category.key"
            :type="selectedCategory === category.key ? 'primary' : 'default'"
            :plain="selectedCategory !== category.key"
            size="small"
            @click="selectedCategory = category.key"
            class="category-btn"
          >
            {{ category.label }}
          </el-button>
        </div>
        
        <!-- 筛选器 -->
        <div class="filter-section">
          <el-select
            v-model="selectedCountry"
            placeholder="所有国家/地区"
            size="small"
            class="filter-select"
            clearable
          >
            <el-option label="所有国家/地区" value="" />
            <el-option label="美国" value="US" />
            <el-option label="中国" value="CN" />
            <el-option label="日本" value="JP" />
          </el-select>
          
          <el-select
            v-model="selectedType"
            placeholder="所有类型"
            size="small"
            class="filter-select"
            clearable
          >
            <el-option label="所有类型" value="" />
            <el-option label="现货" value="spot" />
            <el-option label="期货" value="futures" />
            <el-option label="期权" value="options" />
          </el-select>
        </div>
        
        <!-- 商品列表 -->
        <div class="symbol-list-container">
          <div class="loading-indicator" v-if="isLoading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          
          <div class="symbol-list" v-else>
            <div
              v-for="symbol in filteredSymbols"
              :key="symbol.code"
              class="symbol-item"
              @click="selectSymbol(symbol.code)"
              :class="{ 'selected': symbol.code === currentSymbol }"
            >
              <div class="symbol-main">
                <div class="symbol-code">{{ symbol.code }}</div>
                <div class="symbol-name">{{ symbol.name }}</div>
              </div>
              <div class="symbol-meta">
                <span class="symbol-type">{{ symbol.type }}</span>
                <span class="symbol-exchange">{{ symbol.exchange }}</span>
              </div>
            </div>
          </div>
          
          <div class="empty-state" v-if="!isLoading && filteredSymbols.length === 0">
            <el-empty description="未找到匹配的商品" :image-size="80" />
          </div>
        </div>
      </div>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  Setting,
  FullScreen,
  Search,
  Grid,
  Connection,
  DataAnalysis,
  Camera,
  ArrowUp,
  ArrowDown,
  Timer,
  Loading
} from '@element-plus/icons-vue'
import KLineChart from './components/KLineChart.vue'

// KLineChart组件引用
const klineChartRef = ref<InstanceType<typeof KLineChart> | null>(null)

// 基础响应式数据
const symbolSearch = ref('')
const timeframe = ref('15m')
const chartType = ref<'candle' | 'line'>('candle')


// 指标状态与弹窗
const indicatorDialogVisible = ref(false)

// 金融商品搜索弹窗
const symbolSearchDialogVisible = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('all')
const selectedCountry = ref('')
const selectedType = ref('')
const isLoading = ref(false)

const categories = ref([
  { key: 'all', label: '全部' },
  { key: 'stocks', label: '股票' },
  { key: 'futures', label: '期货' },
  { key: 'forex', label: '外汇' },
  { key: 'crypto', label: '加密货币' },
  { key: 'indices', label: '指数' },
  { key: 'commodities', label: '商品' },
  { key: 'bonds', label: '债券' }
])

const searchResults = ref([
  { code: 'BTCUSDT', name: '比特币/USDT', type: '现货', exchange: 'Binance', category: 'crypto', country: 'US' },
  { code: 'ETHUSDT', name: '以太坊/USDT', type: '现货', exchange: 'Binance', category: 'crypto', country: 'US' },
  { code: 'BNBUSDT', name: 'BNB/USDT', type: '现货', exchange: 'Binance', category: 'crypto', country: 'US' },
  { code: 'ADAUSDT', name: 'ADA/USDT', type: '现货', exchange: 'Binance', category: 'crypto', country: 'US' },
  { code: 'SOLUSDT', name: 'SOL/USDT', type: '现货', exchange: 'Binance', category: 'crypto', country: 'US' },
  { code: 'DOGEUSDT', name: '狗狗币/USDT', type: '现货', exchange: 'Binance', category: 'crypto', country: 'US' },
  { code: 'XRPUSDT', name: 'XRP/USDT', type: '现货', exchange: 'Binance', category: 'crypto', country: 'US' },
  { code: 'DOTUSDT', name: 'DOT/USDT', type: '现货', exchange: 'Binance', category: 'crypto', country: 'US' },
  { code: 'AAPL', name: '苹果公司', type: '股票', exchange: 'NASDAQ', category: 'stocks', country: 'US' },
  { code: 'TSLA', name: '特斯拉', type: '股票', exchange: 'NASDAQ', category: 'stocks', country: 'US' },
  { code: 'MSFT', name: '微软', type: '股票', exchange: 'NASDAQ', category: 'stocks', country: 'US' },
  { code: 'GOOGL', name: '谷歌', type: '股票', exchange: 'NASDAQ', category: 'stocks', country: 'US' },
  { code: 'CL', name: '原油期货', type: '期货', exchange: 'NYMEX', category: 'commodities', country: 'US' },
  { code: 'GC', name: '黄金期货', type: '期货', exchange: 'COMEX', category: 'commodities', country: 'US' },
  { code: 'EURUSD', name: '欧元/美元', type: '外汇', exchange: 'Forex', category: 'forex', country: 'US' },
  { code: 'GBPUSD', name: '英镑/美元', type: '外汇', exchange: 'Forex', category: 'forex', country: 'US' },
  { code: 'SPX', name: '标普500指数', type: '指数', exchange: 'CBOE', category: 'indices', country: 'US' },
  { code: 'NDX', name: '纳斯达克100指数', type: '指数', exchange: 'NASDAQ', category: 'indices', country: 'US' }
])

const filteredResults = computed(() => {
  let filtered = searchResults.value
  
  // 按分类筛选
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(symbol => symbol.category === selectedCategory.value)
  }
  
  // 按国家筛选
  if (selectedCountry.value) {
    filtered = filtered.filter(symbol => symbol.country === selectedCountry.value)
  }
  
  // 按类型筛选
  if (selectedType.value) {
    filtered = filtered.filter(symbol => symbol.type === selectedType.value)
  }
  
  // 按搜索关键词筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(symbol => 
      symbol.code.toLowerCase().includes(keyword) ||
      symbol.name.toLowerCase().includes(keyword)
    )
  }
  
  return filtered
})

const filteredSymbols = filteredResults
const indicatorState = ref({ 
  ma: false, 
  vol: false, 
  macd: false,
  // 自定义指标
  custom_ma: false,
  custom_rsi: false
})

// 调试：监听指标状态变化
watch(
  indicatorState,
  (newVal, oldVal) => {
    console.log('App.vue - indicatorState changed:', { old: oldVal, new: newVal })
    // 勾选即生效：同步到图表
    if (klineChartRef.value) {
      // 内置指标
      klineChartRef.value.ensureIndicator('MA', !!newVal.ma)
      klineChartRef.value.ensureIndicator('VOL', !!newVal.vol)
      klineChartRef.value.ensureIndicator('MACD', !!newVal.macd)
      // 自定义指标
      klineChartRef.value.ensureIndicator('CUSTOM_MA', !!newVal.custom_ma)
      klineChartRef.value.ensureIndicator('CUSTOM_RSI', !!newVal.custom_rsi)
    }
  },
  { deep: true }
)

// 选择金融商品
const selectSymbol = (symbol: string) => {
  currentSymbol.value = symbol
  symbolSearchDialogVisible.value = false
  searchKeyword.value = ''
  selectedCategory.value = 'all'
  selectedCountry.value = ''
  selectedType.value = ''
  ElMessage.success(`已切换到 ${symbol}`)
}

// 应用指标设置
const applyIndicatorSettings = () => {
  console.log('应用指标设置:', indicatorState.value)
  
  // 通过KLineChart组件的ensureIndicator方法应用指标设置
  if (klineChartRef.value) {
    // 内置指标
    klineChartRef.value.ensureIndicator('MA', indicatorState.value.ma)
    klineChartRef.value.ensureIndicator('VOL', indicatorState.value.vol)
    klineChartRef.value.ensureIndicator('MACD', indicatorState.value.macd)
    
    // 自定义指标
    klineChartRef.value.ensureIndicator('CUSTOM_MA', indicatorState.value.custom_ma)
    klineChartRef.value.ensureIndicator('CUSTOM_RSI', indicatorState.value.custom_rsi)
  }
  
  // 关闭弹窗
  indicatorDialogVisible.value = false
  
  // 提示用户
  ElMessage.success('指标设置已应用')
}

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
const isRightResizing = ref(false)
const resizeType = ref('')
const startX = ref(0)
const startWidth = ref(0)

// 底部面板高度控制
const bottomPanelHeight = ref(40) // 默认为最小化状态
const isBottomResizing = ref(false)

// 新增：视口高度与覆盖/锁定逻辑
const windowHeight = ref(window.innerHeight)
const overlayThreshold = computed(() => Math.floor(windowHeight.value * 0.5)) // 底部高度超过视口50%时进入覆盖模式
const isBottomOverlay = computed(() => bottomPanelHeight.value > overlayThreshold.value)
const lockedKlineHeight = computed(() => {
  const headerHeightConst = 44
  const resizerHeightConst = 4
  const containerHeight = windowHeight.value - headerHeightConst
  // 最小高度保护为100px，避免过小
  return Math.max(100, containerHeight - overlayThreshold.value - resizerHeightConst)
})

// 根据是否覆盖模式，动态计算样式
const klineAreaStyle = computed(() => {
  return isBottomOverlay.value
    ? { padding: '0', overflow: 'hidden', height: lockedKlineHeight.value + 'px', flex: 'none' }
    : { padding: '0', overflow: 'hidden', flex: '1' }
})

const dividerStyle = computed(() => {
  const base = {
    height: '4px',
    background: 'var(--tv-border-primary)',
    border: 'none',
    cursor: isBottomResizing.value ? 'grabbing' : 'grab',
    transition: 'background 0.2s',
    userSelect: 'none',
    margin: '0'
  } as any
  return isBottomOverlay.value
    ? { ...base, zIndex: 30, position: 'absolute', left: 0, right: 0, bottom: bottomPanelHeight.value + 'px' }
    : { ...base, zIndex: 10, position: 'relative', flexShrink: 0 }
})

const bottomFooterStyle = computed(() => {
  const base = {
    background: 'var(--tv-bg-secondary)',
    padding: '0',
    minHeight: '25px',
    overflow: 'hidden',
    borderTop: '1px solid var(--tv-border-primary)',
    height: bottomPanelHeight.value + 'px'
  } as any
  return isBottomOverlay.value
    ? { ...base, position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 20, width: '100%' }
    : { ...base, flexShrink: 0 }
})
const startY = ref(0)
const startHeight = ref(0)
const minBottomHeight = 40 // 调整最小高度为40px
const maxBottomHeight = ref(0) // 将在mounted中计算

// 底部标签页控制
const activeTab = ref('trading') // 默认激活交易面板
const isBottomMaximized = ref(false) // 底部面板最大化状态
const previousBottomHeight = ref(200) // 记录之前的高度

// 底部面板拖拽调整方法
const startBottomResize = (event: MouseEvent) => {
  isBottomResizing.value = true
  startY.value = event.clientY
  startHeight.value = bottomPanelHeight.value
  
  // 计算最大高度（窗口高度 - 顶部栏高度 - 最小图表区域高度）
  const headerHeight = 44
  const minChartHeight = 0 // 允许完全拖拽到顶部
  maxBottomHeight.value = window.innerHeight - headerHeight - minChartHeight
  
  document.body.classList.add('resizing')
  document.addEventListener('mousemove', handleBottomResize)
  document.addEventListener('mouseup', stopBottomResize)
  event.preventDefault()
  event.stopPropagation()
}

const handleBottomResize = (event: MouseEvent) => {
  if (!isBottomResizing.value) return
  
  const deltaY = startY.value - event.clientY // 向上拖拽为正值
  const newHeight = startHeight.value + deltaY
  const clampedHeight = Math.max(minBottomHeight, Math.min(maxBottomHeight.value, newHeight))
  
  bottomPanelHeight.value = clampedHeight
  event.preventDefault()
}

const stopBottomResize = () => {
  isBottomResizing.value = false
  document.body.classList.remove('resizing')
  document.removeEventListener('mousemove', handleBottomResize)
  document.removeEventListener('mouseup', stopBottomResize)
}

// 底部面板最大化/最小化切换
const toggleBottomPanel = () => {
  if (isBottomMaximized.value) {
    // 从最大化状态恢复到之前的高度
    bottomPanelHeight.value = previousBottomHeight.value
    isBottomMaximized.value = false
  } else {
    // 保存当前高度并最大化
    previousBottomHeight.value = bottomPanelHeight.value
    bottomPanelHeight.value = maxBottomHeight.value
    isBottomMaximized.value = true
  }
}

// 拖拽调整大小方法（仅右边栏）
const startResize = (type: string, event: MouseEvent) => {
  if (type !== 'right') return // 只允许调整右边栏
  
  isResizing.value = true
  isRightResizing.value = true
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
  isRightResizing.value = false
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
  
  // 初始化底部面板最大高度
  const headerHeight = 44
  const minChartHeight = 0 // 允许完全拖拽到顶部
  maxBottomHeight.value = window.innerHeight - headerHeight - minChartHeight
  
  // 监听窗口大小变化
  const handleResize = () => {
    windowWidth.value = window.innerWidth
    windowHeight.value = window.innerHeight
    // 更新底部面板最大高度
    maxBottomHeight.value = window.innerHeight - headerHeight - minChartHeight
    // 确保当前高度不超过新的最大值
    if (bottomPanelHeight.value > maxBottomHeight.value) {
      bottomPanelHeight.value = maxBottomHeight.value
    }
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
/* 金融商品搜索弹窗样式 - 使用更强的选择器 */
.symbol-search-dialog :deep(.el-overlay) {
  background: rgba(0, 0, 0, 0.8) !important;
}

.symbol-search-dialog :deep(.el-dialog) {
  background: var(--tv-bg-secondary) !important;
  border: none !important;
  border-radius: 8px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
  margin: 0 !important;
}

.symbol-search-dialog :deep(.el-dialog__wrapper) {
  background: transparent !important;
}

.symbol-search-dialog :deep(.el-dialog__header) {
  background: var(--tv-bg-secondary) !important;
  border-bottom: 1px solid var(--tv-border-primary) !important;
  padding: 16px 20px !important;
}

.symbol-search-dialog :deep(.el-dialog__title) {
  color: var(--tv-text-primary) !important;
  font-size: 16px !important;
  font-weight: 500 !important;
}

.symbol-search-dialog :deep(.el-dialog__headerbtn) {
  background: transparent !important;
  border: none !important;
}

.symbol-search-dialog :deep(.el-dialog__close) {
  color: var(--tv-text-secondary) !important;
  font-size: 18px !important;
}

.symbol-search-dialog :deep(.el-dialog__close:hover) {
  color: var(--tv-text-primary) !important;
}

.symbol-search-dialog :deep(.el-dialog__body) {
  padding: 0 !important;
  background: var(--tv-bg-secondary) !important;
}

.symbol-search-dialog :deep(.search-container .search-header) {
  padding: 16px 20px !important;
  border-bottom: 1px solid var(--tv-border-primary) !important;
}

.symbol-search-dialog :deep(.search-container .category-tabs) {
  padding: 12px 20px !important;
  border-bottom: 1px solid var(--tv-border-primary) !important;
  display: flex !important;
  gap: 8px !important;
  flex-wrap: wrap !important;
}

.symbol-search-dialog :deep(.search-container .filter-section) {
  padding: 12px 20px !important;
  border-bottom: 1px solid var(--tv-border-primary) !important;
  display: flex !important;
  gap: 12px !important;
}
  
.symbol-search-dialog :deep(.search-container .symbol-list-container) {
  height: 400px !important;
}

.symbol-search-dialog :deep(.search-container .loading-indicator) {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  height: 100% !important;
  color: var(--tv-text-secondary) !important;
  gap: 8px !important;
}

.symbol-search-dialog :deep(.search-container .symbol-list) {
  height: 100% !important;
  overflow-y: auto !important;
  padding: 8px 0 !important;
}

.symbol-search-dialog :deep(.search-container .symbol-list::-webkit-scrollbar) {
  width: 6px !important;
}

.symbol-search-dialog :deep(.search-container .symbol-list::-webkit-scrollbar-track) {
  background: var(--tv-bg-overlay) !important;
}

.symbol-search-dialog :deep(.search-container .symbol-list::-webkit-scrollbar-thumb) {
  background: var(--tv-border-secondary) !important;
  border-radius: 3px !important;
}

.symbol-search-dialog :deep(.search-container .symbol-list::-webkit-scrollbar-thumb:hover) {
  background: var(--tv-border-light) !important;
}

.symbol-search-dialog :deep(.search-container .symbol-item) {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  padding: 12px 20px !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  border-left: 3px solid transparent !important;
}

.symbol-search-dialog :deep(.search-container .symbol-item:hover) {
  background: var(--tv-bg-hover) !important;
}

.symbol-search-dialog :deep(.search-container .symbol-item.selected) {
  background: var(--tv-primary-light) !important;
  border-left-color: var(--tv-primary) !important;
}

.symbol-search-dialog :deep(.search-container .symbol-main) {
  flex: 1 !important;
}

.symbol-search-dialog :deep(.search-container .symbol-code) {
  font-weight: 600 !important;
  color: var(--tv-text-primary) !important;
  font-size: 14px !important;
  margin-bottom: 2px !important;
}

.symbol-search-dialog :deep(.search-container .symbol-name) {
  font-size: 12px !important;
  color: var(--tv-text-secondary) !important;
}

.symbol-search-dialog :deep(.search-container .symbol-meta) {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-end !important;
  gap: 2px !important;
}

.symbol-search-dialog :deep(.search-container .symbol-type) {
  font-size: 11px !important;
  color: var(--tv-text-disabled) !important;
  background: var(--tv-bg-overlay) !important;
  padding: 2px 6px !important;
  border-radius: 2px !important;
}

.symbol-search-dialog :deep(.search-container .symbol-exchange) {
  font-size: 10px !important;
  color: var(--tv-text-secondary) !important;
}

.symbol-search-dialog :deep(.search-container .empty-state) {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  height: 100% !important;
  color: var(--tv-text-secondary) !important;
}

.symbol-search-dialog :deep(.search-input) {
  .el-input__wrapper {
    background: var(--tv-bg-overlay) !important;
    border: 1px solid var(--tv-border-primary) !important;
    box-shadow: none !important;
    
    &:hover {
      border-color: var(--tv-border-secondary) !important;
    }
    
    &.is-focus {
      border-color: var(--tv-primary) !important;
    }
  }
  
  .el-input__inner {
    color: var(--tv-text-primary) !important;
    
    &::placeholder {
      color: var(--tv-text-secondary) !important;
    }
  }
  
  .el-input__prefix {
    color: var(--tv-text-secondary) !important;
  }
}

.symbol-search-dialog :deep(.category-btn) {
  height: 28px !important;
  padding: 0 12px !important;
  font-size: 12px !important;
  border-radius: 4px !important;
  
  &.el-button--default {
    background: transparent !important;
    border-color: var(--tv-border-primary) !important;
    color: var(--tv-text-secondary) !important;
    
    &:hover {
      background: var(--tv-bg-hover) !important;
      border-color: var(--tv-border-secondary) !important;
      color: var(--tv-text-primary) !important;
    }
  }
  
  &.el-button--primary {
    background: var(--tv-primary) !important;
    border-color: var(--tv-primary) !important;
    color: var(--tv-text-inverse) !important;
  }
}

.symbol-search-dialog :deep(.filter-select) {
  width: 140px !important;
  
  .el-select__wrapper {
    background: var(--tv-bg-overlay) !important;
    border: 1px solid var(--tv-border-primary) !important;
    box-shadow: none !important;
    
    &:hover {
      border-color: var(--tv-border-secondary) !important;
    }
    
    &.is-focus {
      border-color: var(--tv-primary) !important;
    }
  }
  
  .el-select__placeholder {
    color: var(--tv-text-secondary) !important;
  }
  
  .el-select__selected-item {
    color: var(--tv-text-primary) !important;
  }
}

</style>

<style scoped>

/* Element Plus 暗色主题变量 */
:root {
  --el-bg-color: var(--tv-bg-secondary);
  --el-bg-color-page: var(--tv-bg-primary);
  --el-bg-color-overlay: var(--tv-bg-overlay);
  --el-text-color-primary: var(--tv-text-primary);
  --el-text-color-regular: var(--tv-text-secondary);
  --el-text-color-secondary: var(--tv-text-secondary);
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
  --el-button-bg-color: var(--tv-bg-overlay);
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
  --el-radio-button-checked-text-color: var(--tv-text-inverse);
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

/* 拖拽状态样式 */
.resizing {
  user-select: none !important;
  cursor: row-resize !important;
}

.resizing * {
  user-select: none !important;
  pointer-events: none !important;
}

/* 拖拽手柄悬停效果 */
.resize-handle:hover {
  background: var(--tv-accent-primary) !important;
}

/* 底部标签页样式 */
.bottom-tabs-container {
  height: 100%;
  position: relative;
}

:deep(.bottom-tabs) {
  height: 100%;
}

:deep(.bottom-tabs .el-tabs__header) {
  margin: 0;
  background: var(--tv-bg-secondary);
  border-bottom: 1px solid var(--tv-border-primary);
  height: 40px;
  position: relative;
}

:deep(.bottom-tabs .el-tabs__nav-wrap) {
  height: 40px;
  display: flex;
  align-items: center;
  padding: 0 8px;
}

:deep(.bottom-tabs .el-tabs__nav) {
  border: none;
  height: auto;
}

:deep(.bottom-tabs .el-tabs__item) {
  height: 32px !important;
  padding: 0 10px !important;
  margin: 4px 4px !important; /* 在 40px header 内垂直置中：4+32+4 */
  display: inline-flex !important; /* 确保文字在 pill 内垂直居中 */
  align-items: center !important;
  justify-content: center !important; /* 水平居中 */
  border: none !important;
  border-radius: 6px !important;
  background: transparent !important;
  color: var(--tv-text-secondary) !important;
  font-size: 13px !important;
  line-height: 1 !important; /* 重置行高 */
  vertical-align: middle !important;
  transition: color .2s ease, background .2s ease !important;
}

/* 重置标签内文字节点样式 */
:deep(.bottom-tabs .el-tabs__item span) {
  display: inline-block !important;
  line-height: 1 !important;
  vertical-align: middle !important;
}

:deep(.bottom-tabs .el-tabs__item:hover) {
  background: rgba(255, 255, 255, 0.06); /* 浅色圆角矩形填充 */
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08); /* 轻微内描边增强对比 */
  color: var(--tv-text-primary);
}

:deep(.bottom-tabs .el-tabs__item.is-active) {
  background: transparent !important;
  color: #ffffff !important; /* 激活时文字改为白色 */
  font-weight: 600 !important;
}

/* 线型标签下的活动条（下划线） */
:deep(.bottom-tabs .el-tabs__active-bar) {
  background: var(--tv-accent-primary);
  height: 2px;
  border-radius: 1px;
}

:deep(.bottom-tabs .el-tabs__content) {
  height: calc(100% - 40px);
  padding: 0;
}

:deep(.bottom-tabs .el-tab-pane) {
  height: 100%;
}



.custom-indicator-label {
  color: var(--el-text-color-primary);
  transition: color .15s ease;
}
.custom-indicator-label.active {
  color: var(--el-color-primary);
}
</style>