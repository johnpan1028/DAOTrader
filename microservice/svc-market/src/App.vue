<template>
  <div id="app" class="market-app">
    <!-- 顶部工具栏 -->
    <div class="market-toolbar">
      <div class="toolbar-left">
        <h2 class="app-title">
          📈 DAOTrader 行情中台
        </h2>
        <div class="status-indicator">
          <div class="status-dot" :class="{ disconnected: !isConnected }"></div>
          <span>{{ isConnected ? '实时连接' : '连接断开' }}</span>
        </div>
      </div>
      
      <div class="toolbar-right">
        <select v-model="selectedMarket" class="market-select">
          <option value="domestic-futures">国内期货</option>
          <option value="international-futures">国际期货</option>
          <option value="a-stock">A股</option>
          <option value="h-stock">H股</option>
          <option value="us-stock">美股</option>
          <option value="forex">外汇</option>
          <option value="crypto">数字币</option>
        </select>
        
        <div class="button-group">
          <button 
            :class="['btn', { active: viewMode === 'grid' }]" 
            @click="viewMode = 'grid'"
          >
            📊 表格
          </button>
          <button 
            :class="['btn', { active: viewMode === 'chart' }]" 
            @click="viewMode = 'chart'"
          >
            📈 图表
          </button>
        </div>
        
        <button class="btn refresh-btn" @click="refreshData">
          🔄 刷新
        </button>
      </div>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- AG Grid 表格视图 -->
      <div v-show="viewMode === 'grid'" class="grid-container">
        <ag-grid-vue
          ref="agGrid"
          class="ag-theme-alpine financial-theme"
          :columnDefs="columnDefs"
          :rowData="rowData"
          :defaultColDef="defaultColDef"
          :gridOptions="gridOptions"
          @grid-ready="onGridReady"
          @cell-value-changed="onCellValueChanged"
        >
        </ag-grid-vue>
      </div>
      
      <!-- 图表视图 -->
      <div v-show="viewMode === 'chart'" class="chart-container">
        <div class="chart-placeholder">
          <div class="chart-icon">📈</div>
          <p>图表视图开发中...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import type { ColDef, GridOptions, GridReadyEvent, CellValueChangedEvent } from 'ag-grid-community'

// 响应式数据
const isConnected = ref(true)
const selectedMarket = ref('domestic-futures')
const viewMode = ref('grid')
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
    field: 'price',
    width: 100,
    type: 'numericColumn',
    cellClass: 'financial-cell',
    cellRenderer: (params: any) => {
      const value = params.value
      const change = params.data.change
      let className = 'price-neutral'
      if (change > 0) className = 'price-up'
      else if (change < 0) className = 'price-down'
      return `<span class="${className}">${value?.toFixed(2) || '--'}</span>`
    }
  },
  {
    headerName: '涨跌',
    field: 'change',
    width: 80,
    type: 'numericColumn',
    cellClass: 'financial-cell',
    cellRenderer: (params: any) => {
      const value = params.value
      if (value === undefined || value === null) return '--'
      const className = value > 0 ? 'change-positive' : value < 0 ? 'change-negative' : 'change-zero'
      const prefix = value > 0 ? '+' : ''
      return `<span class="${className}">${prefix}${value.toFixed(2)}</span>`
    }
  },
  {
    headerName: '涨跌幅',
    field: 'changePercent',
    width: 90,
    type: 'numericColumn',
    cellClass: 'financial-cell',
    cellRenderer: (params: any) => {
      const value = params.value
      if (value === undefined || value === null) return '--'
      const className = value > 0 ? 'change-positive' : value < 0 ? 'change-negative' : 'change-zero'
      const prefix = value > 0 ? '+' : ''
      return `<span class="${className}">${prefix}${value.toFixed(2)}%</span>`
    }
  },
  {
    headerName: '成交量',
    field: 'volume',
    width: 100,
    type: 'numericColumn',
    cellClass: 'volume-cell',
    valueFormatter: (params: any) => {
      const value = params.value
      if (!value) return '--'
      if (value >= 100000000) return (value / 100000000).toFixed(1) + '亿'
      if (value >= 10000) return (value / 10000).toFixed(1) + '万'
      return value.toString()
    }
  },
  {
    headerName: '开盘价',
    field: 'open',
    width: 90,
    type: 'numericColumn',
    cellClass: 'financial-cell',
    valueFormatter: (params: any) => params.value?.toFixed(2) || '--'
  },
  {
    headerName: '最高价',
    field: 'high',
    width: 90,
    type: 'numericColumn',
    cellClass: 'financial-cell',
    valueFormatter: (params: any) => params.value?.toFixed(2) || '--'
  },
  {
    headerName: '最低价',
    field: 'low',
    width: 90,
    type: 'numericColumn',
    cellClass: 'financial-cell',
    valueFormatter: (params: any) => params.value?.toFixed(2) || '--'
  },
  {
    headerName: '昨收价',
    field: 'prevClose',
    width: 90,
    type: 'numericColumn',
    cellClass: 'financial-cell',
    valueFormatter: (params: any) => params.value?.toFixed(2) || '--'
  }
])

const defaultColDef = ref<ColDef>({
  sortable: true,
  filter: true,
  resizable: true,
  menuTabs: ['filterMenuTab', 'generalMenuTab']
})

const gridOptions = ref<GridOptions>({
  animateRows: true,
  enableRangeSelection: true,
  enableCharts: true,
  suppressMenuHide: true,
  getRowId: (params) => params.data.symbol
})

// 模拟行情数据
const rowData = ref([
  {
    symbol: 'CU2401',
    name: '沪铜2401',
    price: 68450,
    change: 320,
    changePercent: 0.47,
    volume: 125680,
    open: 68200,
    high: 68580,
    low: 68100,
    prevClose: 68130
  },
  {
    symbol: 'AU2312',
    name: '沪金2312',
    price: 456.8,
    change: -2.4,
    changePercent: -0.52,
    volume: 89456,
    open: 458.5,
    high: 459.2,
    low: 456.1,
    prevClose: 459.2
  },
  {
    symbol: 'RB2401',
    name: '螺纹钢2401',
    price: 3845,
    change: 15,
    changePercent: 0.39,
    volume: 234567,
    open: 3835,
    high: 3850,
    low: 3820,
    prevClose: 3830
  },
  {
    symbol: 'I2401',
    name: '铁矿石2401',
    price: 785.5,
    change: -8.5,
    changePercent: -1.07,
    volume: 156789,
    open: 792,
    high: 795,
    low: 783,
    prevClose: 794
  },
  {
    symbol: 'ZC401',
    name: '动力煤2401',
    price: 892.4,
    change: 12.6,
    changePercent: 1.43,
    volume: 98765,
    open: 885,
    high: 895,
    low: 882,
    prevClose: 879.8
  }
])

// 方法
const onGridReady = (params: GridReadyEvent) => {
  console.log('AG Grid 已准备就绪', params)
  // 自动调整列宽
  params.api.sizeColumnsToFit()
}

const onCellValueChanged = (event: CellValueChangedEvent) => {
  console.log('单元格值已更改', event)
}

const refreshData = () => {
  console.log('刷新数据')
  // 这里可以调用API刷新数据
  // 模拟数据更新
  rowData.value.forEach(item => {
    const randomChange = (Math.random() - 0.5) * 10
    item.change = randomChange
    item.changePercent = (randomChange / item.prevClose) * 100
    item.price = item.prevClose + randomChange
  })
  
  // 刷新网格
  if (agGrid.value) {
    agGrid.value.api.setRowData(rowData.value)
  }
}

// 模拟实时数据更新
const startRealTimeUpdates = () => {
  setInterval(() => {
    if (viewMode.value === 'grid' && rowData.value.length > 0) {
      // 随机更新一行数据
      const randomIndex = Math.floor(Math.random() * rowData.value.length)
      const item = rowData.value[randomIndex]
      const randomChange = (Math.random() - 0.5) * 5
      
      item.change = randomChange
      item.changePercent = (randomChange / item.prevClose) * 100
      item.price = item.prevClose + randomChange
      item.volume += Math.floor(Math.random() * 1000)
      
      // 更新网格中的特定行
      if (agGrid.value) {
        agGrid.value.api.applyTransaction({ update: [item] })
      }
    }
  }, 2000) // 每2秒更新一次
}

// 生命周期
onMounted(() => {
  console.log('行情服务中台已启动')
  startRealTimeUpdates()
})
</script>

<style scoped>
.market-app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.market-toolbar {
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.market-select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 12px;
  min-width: 120px;
}

.button-group {
  display: flex;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #d1d5db;
}

.btn {
  padding: 6px 12px;
  border: none;
  background: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border-right: 1px solid #d1d5db;
}

.btn:last-child {
  border-right: none;
}

.btn:hover {
  background: #f3f4f6;
}

.btn.active {
  background: #3b82f6;
  color: white;
}

.refresh-btn {
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

.chart-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.main-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.grid-container {
  height: 100%;
  width: 100%;
}

.chart-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
}

.chart-placeholder {
  text-align: center;
  color: #a0aec0;
}

.chart-placeholder p {
  margin-top: 16px;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .market-toolbar {
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }
  
  .app-title {
    font-size: 16px;
  }
}
</style>