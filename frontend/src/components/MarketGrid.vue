<template>
  <div class="market-grid-container">

    
    <!-- AG Grid 表格 -->
    <div class="grid-container">
      <ag-grid-vue
        ref="agGrid"
        class="ag-theme-alpine financial-theme"
        :columnDefs="columnDefs"
        :rowData="rowData"
        :defaultColDef="defaultColDef"
        :gridOptions="gridOptions"
        @grid-ready="onGridReady"
        @cell-value-changed="onCellValueChanged"
        @row-clicked="onRowClicked"
        style="height: 100%; width: 100%;"
      >
      </ag-grid-vue>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, onUnmounted } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import type { ColDef, GridOptions, GridReadyEvent, CellValueChangedEvent } from 'ag-grid-community'

// Props
interface Props {
  marketType: string
}

const props = withDefaults(defineProps<Props>(), {
  marketType: 'domestic-futures'
})

// Emits
const emit = defineEmits<{
  symbolSelected: [symbol: string]
}>()

// 响应式数据
const agGrid = ref()

// AG Grid 配置
const columnDefs = ref<ColDef[]>([
  {
    headerName: '代码',
    field: 'symbol',
    width: 100,
    pinned: 'left',
    cellClass: 'financial-cell'
  },
  {
    headerName: '名称',
    field: 'name',
    width: 120,
    pinned: 'left'
  },
  {
    headerName: '最新价',
    field: 'lastPrice',
    width: 100,
    type: 'numericColumn',
    cellClass: 'price-cell',
    valueFormatter: (params) => {
      if (params.value == null) return '-'
      return Number(params.value).toFixed(2)
    }
  },
  {
    headerName: '涨跌',
    field: 'change',
    width: 80,
    type: 'numericColumn',
    cellClass: (params) => {
      if (params.value > 0) return 'price-up'
      if (params.value < 0) return 'price-down'
      return 'price-neutral'
    },
    valueFormatter: (params) => {
      if (params.value == null) return '-'
      const value = Number(params.value)
      return value > 0 ? `+${value.toFixed(2)}` : value.toFixed(2)
    }
  },
  {
    headerName: '涨跌幅',
    field: 'changePercent',
    width: 90,
    type: 'numericColumn',
    cellClass: (params) => {
      if (params.value > 0) return 'price-up'
      if (params.value < 0) return 'price-down'
      return 'price-neutral'
    },
    valueFormatter: (params) => {
      if (params.value == null) return '-'
      const value = Number(params.value)
      return value > 0 ? `+${value.toFixed(2)}%` : `${value.toFixed(2)}%`
    }
  },
  {
    headerName: '开盘',
    field: 'openPrice',
    width: 90,
    type: 'numericColumn',
    valueFormatter: (params) => {
      if (params.value == null) return '-'
      return Number(params.value).toFixed(2)
    }
  },
  {
    headerName: '最高',
    field: 'highPrice',
    width: 90,
    type: 'numericColumn',
    cellClass: 'price-up',
    valueFormatter: (params) => {
      if (params.value == null) return '-'
      return Number(params.value).toFixed(2)
    }
  },
  {
    headerName: '最低',
    field: 'lowPrice',
    width: 90,
    type: 'numericColumn',
    cellClass: 'price-down',
    valueFormatter: (params) => {
      if (params.value == null) return '-'
      return Number(params.value).toFixed(2)
    }
  },
  {
    headerName: '成交量',
    field: 'volume',
    width: 100,
    type: 'numericColumn',
    valueFormatter: (params) => {
      if (params.value == null) return '-'
      const value = Number(params.value)
      if (value >= 10000) {
        return `${(value / 10000).toFixed(1)}万`
      }
      return value.toString()
    }
  },
  {
    headerName: '成交额',
    field: 'turnover',
    width: 120,
    type: 'numericColumn',
    valueFormatter: (params) => {
      if (params.value == null) return '-'
      const value = Number(params.value)
      if (value >= 100000000) {
        return `${(value / 100000000).toFixed(2)}亿`
      } else if (value >= 10000) {
        return `${(value / 10000).toFixed(1)}万`
      }
      return value.toString()
    }
  },
  {
    headerName: '更新时间',
    field: 'updateTime',
    width: 120,
    valueFormatter: (params) => {
      if (!params.value) return '-'
      return new Date(params.value).toLocaleTimeString()
    }
  }
])

const defaultColDef = ref<ColDef>({
  sortable: true,
  filter: true,
  resizable: true,
  cellClass: 'financial-cell'
})

const gridOptions = ref<GridOptions>({
  animateRows: true,
  enableCellChangeFlash: true,
  suppressRowClickSelection: true,
  rowSelection: 'single',
  headerHeight: 35,
  rowHeight: 28
})

// 行情数据
const rowData = ref<any[]>([])

// WebSocket连接
let ws: WebSocket | null = null

// 连接WebSocket（仅用于模拟市场）
const connectWebSocket = () => {
  if (props.marketType !== 'simulation') return
  
  try {
    ws = new WebSocket('ws://localhost:8000/ws')
    
    ws.onopen = () => {
      console.log('MarketGrid WebSocket连接已建立')
      // 发送品种订阅消息
      const config = marketConfigs[props.marketType]
      if (config && config.symbols) {
        const subscribeMessage = {
          type: 'subscribe',
          symbols: config.symbols
        }
        console.log('发送订阅消息:', subscribeMessage)
        ws?.send(JSON.stringify(subscribeMessage))
      }
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('收到WebSocket数据:', data)
        if (data.type === 'tick') {
          updateMarketDataFromTick(data.data)
        } else if (data.type === 'bar') {
          updateMarketDataFromBar(data.data)
        }
      } catch (error) {
        console.error('解析WebSocket数据失败:', error)
      }
    }
    
    ws.onclose = () => {
      console.log('MarketGrid WebSocket连接已关闭')
    }
    
    ws.onerror = (error) => {
      console.error('MarketGrid WebSocket错误:', error)
    }
  } catch (error) {
    console.error('创建WebSocket连接失败:', error)
  }
}

// 断开WebSocket连接
const disconnectWebSocket = () => {
  if (ws) {
    ws.close()
    ws = null
  }
}

// 从WebSocket tick数据更新市场数据
const updateMarketDataFromTick = (tickData: any) => {
  if (props.marketType !== 'simulation') return
  
  console.log('处理tick数据:', tickData)
  
  // 查找是否已存在该symbol的数据
  const existingIndex = rowData.value.findIndex(item => item.symbol === tickData.symbol)
  
  if (existingIndex >= 0) {
    // 更新现有数据
    const item = rowData.value[existingIndex]
    const prevPrice = item.lastPrice || tickData.pre_close || tickData.last_price
    const change = tickData.last_price - prevPrice
    const changePercent = prevPrice > 0 ? (change / prevPrice) * 100 : 0
    
    rowData.value[existingIndex] = {
      ...item,
      lastPrice: tickData.last_price,
      change: change,
      changePercent: changePercent,
      openPrice: tickData.open_price || item.openPrice,
      highPrice: tickData.high_price || item.highPrice,
      lowPrice: tickData.low_price || item.lowPrice,
      volume: tickData.volume || item.volume,
      turnover: tickData.volume * tickData.last_price || item.turnover,
      updateTime: new Date().toISOString()
    }
  } else {
    // 添加新数据
    const change = tickData.last_price - (tickData.pre_close || tickData.last_price)
    const changePercent = tickData.pre_close > 0 ? (change / tickData.pre_close) * 100 : 0
    
    rowData.value.push({
      symbol: tickData.symbol,
      name: tickData.name || tickData.symbol,
      lastPrice: tickData.last_price,
      change: change,
      changePercent: changePercent,
      openPrice: tickData.open_price || tickData.last_price,
      highPrice: tickData.high_price || tickData.last_price,
      lowPrice: tickData.low_price || tickData.last_price,
      volume: tickData.volume || 0,
      turnover: (tickData.volume || 0) * tickData.last_price,
      updateTime: new Date().toISOString()
    })
  }
  
  // 触发AG Grid更新
  if (agGrid.value?.api) {
    agGrid.value.api.setRowData([...rowData.value])
  }
}

// 从WebSocket bar数据更新市场数据（保留兼容性）
const updateMarketDataFromBar = (barData: any) => {
  if (props.marketType !== 'simulation') return
  
  console.log('处理bar数据:', barData)
  
  // 查找是否已存在该symbol的数据
  const existingIndex = rowData.value.findIndex(item => item.symbol === barData.symbol)
  
  if (existingIndex >= 0) {
    // 更新现有数据
    const item = rowData.value[existingIndex]
    const prevPrice = item.lastPrice || barData.close_price
    const change = barData.close_price - prevPrice
    const changePercent = prevPrice > 0 ? (change / prevPrice) * 100 : 0
    
    rowData.value[existingIndex] = {
      ...item,
      lastPrice: barData.close_price,
      change: change,
      changePercent: changePercent,
      openPrice: barData.open_price,
      highPrice: barData.high_price,
      lowPrice: barData.low_price,
      volume: barData.volume || item.volume,
      turnover: (barData.volume || item.volume) * barData.close_price,
      updateTime: new Date().toISOString()
    }
  } else {
    // 添加新数据
    rowData.value.push({
      symbol: barData.symbol || 'SIM001',
      name: barData.name || '模拟品种',
      lastPrice: barData.close_price,
      change: 0,
      changePercent: 0,
      openPrice: barData.open_price,
      highPrice: barData.high_price,
      lowPrice: barData.low_price,
      volume: barData.volume || 0,
      turnover: (barData.volume || 0) * barData.close_price,
      updateTime: new Date().toISOString()
    })
  }
  
  // 触发AG Grid更新
  if (agGrid.value?.api) {
    agGrid.value.api.setRowData([...rowData.value])
  }
}

// 市场配置信息（用于后端数据生成参考）
const marketConfigs = {
  'domestic-futures': {
    symbols: ['IF2312', 'IC2312', 'IH2312', 'IM2312', 'T2312', 'TF2312', 'TS2312'],
    names: ['沪深300', '中证500', '上证50', '中证1000', '10年国债', '5年国债', '2年国债']
  },
  'international-futures': {
    symbols: ['ES', 'NQ', 'YM', 'RTY', 'CL', 'GC', 'SI'],
    names: ['标普500', '纳斯达克', '道琼斯', '罗素2000', '原油', '黄金', '白银']
  },
  'a-shares': {
    symbols: ['000001', '000002', '600000', '600036', '000858', '002415', '300059'],
    names: ['平安银行', '万科A', '浦发银行', '招商银行', '五粮液', '海康威视', '东方财富']
  },
  'h-shares': {
    symbols: ['00700', '00941', '03690', '09988', '01024', '02318', '01398'],
    names: ['腾讯控股', '中国移动', '美团', '阿里巴巴', '快手', '中国平安', '工商银行']
  },
  'us-stocks': {
    symbols: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA'],
    names: ['苹果', '微软', '谷歌', '亚马逊', '特斯拉', 'Meta', '英伟达']
  },
  'forex': {
    symbols: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD'],
    names: ['欧元美元', '英镑美元', '美元日元', '美元瑞郎', '澳元美元', '美元加元', '纽元美元']
  },
  'crypto': {
    symbols: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT', 'DOTUSDT'],
    names: ['比特币', '以太坊', 'BNB', '艾达币', 'Solana', '瑞波币', 'Polkadot']
  },
  'simulation': {
    symbols: ['SIM001', 'SIM002', 'SIM003', 'SIM004'],
    names: ['模拟品种A', '模拟品种B', '模拟品种C', '模拟品种D']
  }
}

// 加载市场数据
const loadMarketData = (marketType: string) => {
  console.log('Loading market data for:', marketType)
  console.log('Before loading - rowData length:', rowData.value.length)
  
  // 先断开之前的WebSocket连接
  disconnectWebSocket()
  
  // 清空当前数据
  rowData.value = []
  console.log('清空数据，等待WebSocket实时数据')
  
  // 发送市场类型切换消息给后端
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'market_change',
      market_type: marketType
    }))
  }
  
  // 建立WebSocket连接接收实时数据
  connectWebSocket()
  
  // 强制触发AG Grid更新
  setTimeout(() => {
    if (agGrid.value?.api) {
      console.log('Forcing AG Grid refresh')
      agGrid.value.api.setRowData([...rowData.value])
    }
  }, 100)
}

// 监听市场类型变化
watch(() => props.marketType, (newMarketType) => {
  loadMarketData(newMarketType)
}, { immediate: true })

// Grid 事件处理
const onGridReady = (params: GridReadyEvent) => {
  console.log('Market Grid Ready:', params)
  console.log('Current rowData length:', rowData.value.length)
  console.log('Current rowData:', rowData.value)
  console.log('Grid API available:', !!params.api)
  
  // 确保数据被正确设置
  if (rowData.value.length > 0) {
    console.log('Setting initial data to grid')
    params.api.setRowData([...rowData.value])
  }
}

// 组件挂载时的调试
onMounted(() => {
  console.log('MarketGrid mounted with marketType:', props.marketType)
  console.log('Current rowData:', rowData.value)
  
  // 延迟检查AG Grid状态并建立WebSocket连接
  setTimeout(() => {
    console.log('Checking AG Grid after mount:')
    console.log('agGrid.value:', agGrid.value)
    console.log('agGrid.value?.api:', agGrid.value?.api)
    console.log('rowData.value.length:', rowData.value.length)
    
    // 建立WebSocket连接等待实时数据
    connectWebSocket()
  }, 500)
})

// 组件卸载时清理WebSocket连接
onUnmounted(() => {
  disconnectWebSocket()
})

const onCellValueChanged = (params: CellValueChangedEvent) => {
  console.log('Cell Value Changed:', params)
}

// 处理行点击事件
const onRowClicked = (params: any) => {
  const symbol = params.data?.symbol
  if (symbol) {
    console.log('Row clicked, symbol:', symbol)
    emit('symbolSelected', symbol)
  }
}
</script>

<style scoped>
.market-grid-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--tv-bg-primary, #1e222d);
}



.grid-container {
  flex: 1;
  overflow: hidden;
  height: 100%;
  min-height: 400px;
}

.grid-container .ag-grid-vue {
  height: 100%;
  width: 100%;
}

/* AG Grid 主题样式 */
:deep(.ag-theme-alpine) {
  --ag-background-color: var(--tv-bg-primary, #1e222d);
  --ag-header-background-color: var(--tv-bg-secondary, #2a2e39);
  --ag-odd-row-background-color: var(--tv-bg-primary, #1e222d);
  --ag-row-hover-color: var(--tv-bg-overlay, #2a2e39);
  --ag-border-color: var(--tv-border-primary, #363a45);
  --ag-header-foreground-color: var(--tv-text-primary, #d1d4dc);
  --ag-foreground-color: var(--tv-text-primary, #d1d4dc);
  --ag-secondary-foreground-color: var(--tv-text-secondary, #868993);
  font-size: 12px;
}

:deep(.financial-cell) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
}

:deep(.price-cell) {
  font-weight: bold;
  font-family: 'Consolas', 'Monaco', monospace;
}

:deep(.price-up) {
  color: #4caf50 !important;
}

:deep(.price-down) {
  color: #f44336 !important;
}

:deep(.price-neutral) {
  color: var(--tv-text-secondary, #868993) !important;
}
</style>