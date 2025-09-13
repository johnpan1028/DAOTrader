<template>
  <div class="futures-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="icon-futures"></i>
          期货数据中心
        </h1>
        <p class="page-description">
          基于AKShare数据源的标准化期货合约数据查询与分析平台
        </p>
      </div>
      
      <div class="header-actions">
        <el-button type="primary" @click="showSelector = !showSelector" round>
          <i class="icon-select"></i>
          {{ showSelector ? '隐藏选择器' : '选择合约' }}
        </el-button>
        
        <el-button :loading="loading" @click="refreshAllData" round>
          <i class="icon-refresh"></i>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 合约选择器 -->
    <div class="selector-container" v-show="showSelector">
      <FuturesSelector
        @contract-selected="handleContractSelected"
        @contracts-confirmed="handleContractsConfirmed"
        @view-data="handleViewData"
        @view-info="handleViewInfo"
      />
    </div>

    <!-- 已选合约概览 -->
    <div class="selected-overview" v-if="selectedContracts.length > 0">
      <div class="overview-header">
        <h3 class="overview-title">
          <i class="icon-portfolio"></i>
          已选合约 ({{ selectedContracts.length }})
        </h3>
        
        <div class="overview-actions">
          <el-button size="small" type="success" @click="exportData" :disabled="!hasData">
            <i class="icon-export"></i>
            导出数据
          </el-button>
          
          <el-button size="small" type="warning" @click="clearAllContracts">
            <i class="icon-clear"></i>
            清空选择
          </el-button>
        </div>
      </div>
      
      <div class="contracts-tabs">
        <div 
          v-for="(contract, index) in selectedContracts"
          :key="contract.symbol"
          class="contract-tab"
          :class="{ 'active': activeContract === contract.symbol }"
          @click="setActiveContract(contract.symbol)"
        >
          <span class="tab-symbol">{{ contract.symbol }}</span>
          <span class="tab-name">{{ contract.name }}</span>
          <el-button
            size="small"
            text
            @click.stop="removeContract(contract.symbol)"
            title="移除合约"
          >
            <i class="icon-close"></i>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 数据展示区域 -->
    <div class="data-container" v-if="activeContract">
      <!-- 合约信息卡片 -->
      <div class="contract-info-card">
        <div class="info-header">
          <div class="contract-title">
            <h2 class="contract-symbol">{{ activeContractData.symbol }}</h2>
            <h3 class="contract-name">{{ activeContractData.name }}</h3>
          </div>
          
          <div class="contract-badges">
            <span class="badge badge-exchange">{{ activeContractData.exchange }}</span>
            <span class="badge badge-category">{{ activeContractData.category }}</span>
            <span 
              v-if="activeContractData.has_night_trading"
              class="badge badge-night"
            >
              夜盘交易
            </span>
          </div>
        </div>
        
        <div class="info-details">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">交易单位:</span>
              <span class="detail-value">{{ activeContractData.unit }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最小变动价位:</span>
              <span class="detail-value">{{ activeContractData.tick_size }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">标的品种:</span>
              <span class="detail-value">{{ activeContractData.underlying }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">合约类型:</span>
              <span class="detail-value">{{ getContractTypeText(activeContractData.contract_type) }}</span>
            </div>
          </div>
          
          <div class="contract-description" v-if="activeContractData.description">
            <p>{{ activeContractData.description }}</p>
          </div>
        </div>
      </div>

      <!-- 实时数据卡片 -->
      <div class="realtime-data-card" v-if="realtimeData[activeContract]">
        <div class="realtime-header">
          <h3 class="realtime-title">
            <i class="icon-realtime"></i>
            实时行情
          </h3>
          <div class="update-time">
            更新时间: {{ formatDateTime(realtimeData[activeContract].timestamp) }}
          </div>
        </div>
        
        <div class="realtime-grid">
          <div class="price-item main-price">
            <div class="price-label">最新价</div>
            <div class="price-value" :class="getPriceChangeClass(realtimeData[activeContract])">
              {{ formatPrice(realtimeData[activeContract].current_price) }}
            </div>
            <div class="price-change" :class="getPriceChangeClass(realtimeData[activeContract])">
              {{ formatChange(realtimeData[activeContract].change, realtimeData[activeContract].change_percent) }}
            </div>
          </div>
          
          <div class="price-item">
            <div class="price-label">开盘价</div>
            <div class="price-value">{{ formatPrice(realtimeData[activeContract].open) }}</div>
          </div>
          
          <div class="price-item">
            <div class="price-label">最高价</div>
            <div class="price-value">{{ formatPrice(realtimeData[activeContract].high) }}</div>
          </div>
          
          <div class="price-item">
            <div class="price-label">最低价</div>
            <div class="price-value">{{ formatPrice(realtimeData[activeContract].low) }}</div>
          </div>
          
          <div class="price-item">
            <div class="price-label">成交量</div>
            <div class="price-value">{{ formatVolume(realtimeData[activeContract].volume) }}</div>
          </div>
          
          <div class="price-item">
            <div class="price-label">持仓量</div>
            <div class="price-value">{{ formatVolume(realtimeData[activeContract].open_interest) }}</div>
          </div>
        </div>
      </div>

      <!-- 数据查询控制 -->
      <div class="data-controls">
        <el-card>
          <template #header>
            <span><i class="icon-chart"></i> 历史数据查询</span>
          </template>
          <el-form :inline="true" label-width="80px">
            <el-form-item label="数据周期">
              <el-select v-model="queryParams.period" style="width: 140px">
                <el-option label="日线" value="daily" />
                <el-option label="周线" value="weekly" />
                <el-option label="月线" value="monthly" />
              </el-select>
            </el-form-item>
            <el-form-item label="开始日期">
              <el-date-picker v-model="queryParams.startDate" type="date" value-format="YYYY-MM-DD" placeholder="开始日期" style="width: 160px" :disabled-date="(d) => d.getTime() > new Date(queryParams.endDate).getTime()" />
            </el-form-item>
            <el-form-item label="结束日期">
              <el-date-picker v-model="queryParams.endDate" type="date" value-format="YYYY-MM-DD" placeholder="结束日期" style="width: 160px" :disabled-date="(d) => d.getTime() < new Date(queryParams.startDate).getTime() || d.getTime() > new Date(today).getTime()" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loadingHistorical" @click="loadHistoricalData">
                <i class="icon-search"></i>
                查询数据
              </el-button>
              <el-button @click="resetQueryParams">
                <i class="icon-reset"></i>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 历史数据表格 -->
      <div class="historical-data-card" v-if="historicalData[activeContract]">
        <div class="data-header">
          <h3 class="data-title">
            <i class="icon-table"></i>
            历史数据 ({{ historicalData[activeContract].length }} 条记录)
          </h3>
          
          <div class="data-actions">
            <el-button size="small" type="primary" plain @click="showChart = !showChart">
              <i class="icon-chart"></i>
              {{ showChart ? '隐藏图表' : '显示图表' }}
            </el-button>
          </div>
        </div>
        
        <!-- K线图表 -->
        <div class="chart-container" v-if="showChart" :style="{ height: '520px' }">
          <KLineChart />
        </div>
        
        <!-- 数据表格 -->
        <div class="data-table-container">
          <el-table :data="paginatedHistoricalData" size="small" stripe border>
            <el-table-column prop="date" label="日期" width="120">
              <template #default="{ row }">{{ formatDate(row.date) }}</template>
            </el-table-column>
            <el-table-column prop="open" label="开盘价" align="right">
              <template #default="{ row }">{{ formatPrice(row.open) }}</template>
            </el-table-column>
            <el-table-column prop="high" label="最高价" align="right">
              <template #default="{ row }">{{ formatPrice(row.high) }}</template>
            </el-table-column>
            <el-table-column prop="low" label="最低价" align="right">
              <template #default="{ row }">{{ formatPrice(row.low) }}</template>
            </el-table-column>
            <el-table-column prop="close" label="收盘价" align="right">
              <template #default="{ row }">{{ formatPrice(row.close) }}</template>
            </el-table-column>
            <el-table-column prop="volume" label="成交量" align="right">
              <template #default="{ row }">{{ formatVolume(row.volume) }}</template>
            </el-table-column>
            <el-table-column prop="open_interest" label="持仓量" align="right">
              <template #default="{ row }">{{ formatVolume(row.open_interest) }}</template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌额" align="right">
              <template #default="{ row }">{{ formatPrice(row.change) }}</template>
            </el-table-column>
            <el-table-column prop="change_percent" label="涨跌幅" align="right">
              <template #default="{ row }">{{ formatPrice(row.change_percent) }}%</template>
            </el-table-column>
          </el-table>
          <div style="padding: 12px; display: flex; justify-content: center;">
            <el-pagination
              background
              layout="prev, pager, next, jumper"
              :current-page="currentDataPage"
              :page-size="dataPageSize"
              :total="(historicalData[activeContract] && historicalData[activeContract].length) || 0"
              @current-change="(p) => currentDataPage = p"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-if="selectedContracts.length === 0">
      <el-empty description="暂无选择的合约">
        <template #image>
          <i class="icon-empty" style="font-size: 48px;"></i>
        </template>
        <el-button type="primary" @click="showSelector = true">
          <i class="icon-select"></i>
          开始选择合约
        </el-button>
      </el-empty>
    </div>

    <!-- 加载遮罩 -->
    <div class="loading-overlay" v-if="loading">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p class="loading-text">{{ loadingText }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import FuturesSelector from '../components/FuturesSelector.vue'
import KLineChart from '../components/KLineChart.vue'
import { futuresApi, dataFormatter } from '../api/futures'

export default {
  name: 'FuturesView',
  components: {
    FuturesSelector,
    KLineChart
  },
  setup() {
    // 响应式数据
    const showSelector = ref(false)
    const loading = ref(false)
    const loadingHistorical = ref(false)
    const loadingText = ref('')
    const showChart = ref(true)
    
    // 合约相关
    const selectedContracts = ref([])
    const activeContract = ref('')
    
    // 数据存储
    const realtimeData = ref({})
    const historicalData = ref({})
    
    // 查询参数
    const queryParams = reactive({
      period: 'daily',
      startDate: '',
      endDate: ''
    })
    
    // 分页
    const currentDataPage = ref(1)
    const dataPageSize = ref(20)
    
    // 计算属性
    const today = computed(() => {
      return new Date().toISOString().split('T')[0]
    })
    
    const activeContractData = computed(() => {
      return selectedContracts.value.find(c => c.symbol === activeContract.value) || {}
    })
    
    const hasData = computed(() => {
      return Object.keys(historicalData.value).length > 0
    })
    
    const paginatedHistoricalData = computed(() => {
      const data = historicalData.value[activeContract.value] || []
      const start = (currentDataPage.value - 1) * dataPageSize.value
      const end = start + dataPageSize.value
      return data.slice(start, end)
    })
    
    const totalDataPages = computed(() => {
      const data = historicalData.value[activeContract.value] || []
      return Math.ceil(data.length / dataPageSize.value)
    })
    
    // 初始化查询参数
    const initQueryParams = () => {
      const endDate = new Date()
      const startDate = new Date()
      startDate.setMonth(startDate.getMonth() - 3) // 默认3个月
      
      queryParams.endDate = endDate.toISOString().split('T')[0]
      queryParams.startDate = startDate.toISOString().split('T')[0]
    }
    
    // 事件处理
    const handleContractSelected = (event) => {
      console.log('合约选择事件:', event)
    }
    
    const handleContractsConfirmed = (event) => {
      selectedContracts.value = event.contracts
      showSelector.value = false
      
      if (selectedContracts.value.length > 0) {
        setActiveContract(selectedContracts.value[0].symbol)
      }
      
      // 加载实时数据
      loadRealtimeData()
    }
    
    const handleViewData = (contract) => {
      // 直接查看合约数据
      selectedContracts.value = [contract]
      setActiveContract(contract.symbol)
      showSelector.value = false
      loadRealtimeData()
      loadHistoricalData()
    }
    
    const handleViewInfo = (contract) => {
      console.log('查看合约详情:', contract)
      // 可以打开详情弹窗
    }
    
    const setActiveContract = (symbol) => {
      activeContract.value = symbol
      currentDataPage.value = 1
      
      // 如果没有历史数据，自动加载
      if (!historicalData.value[symbol]) {
        loadHistoricalData()
      }
    }
    
    const removeContract = (symbol) => {
      const index = selectedContracts.value.findIndex(c => c.symbol === symbol)
      if (index > -1) {
        selectedContracts.value.splice(index, 1)
        
        // 删除相关数据
        delete realtimeData.value[symbol]
        delete historicalData.value[symbol]
        
        // 如果删除的是当前活跃合约，切换到下一个
        if (activeContract.value === symbol) {
          if (selectedContracts.value.length > 0) {
            setActiveContract(selectedContracts.value[0].symbol)
          } else {
            activeContract.value = ''
          }
        }
      }
    }
    
    const clearAllContracts = () => {
      selectedContracts.value = []
      activeContract.value = ''
      realtimeData.value = {}
      historicalData.value = {}
    }
    
    // 数据加载
    const loadRealtimeData = async () => {
      if (selectedContracts.value.length === 0) return
      
      loading.value = true
      loadingText.value = '加载实时数据...'
      
      try {
        const symbols = selectedContracts.value.map(c => c.symbol)
        const result = await futuresApi.getRealTimeData(symbols)
        
        if (result.success) {
          // 更新实时数据
          symbols.forEach(symbol => {
            if (result.data[symbol]) {
              realtimeData.value[symbol] = {
                ...result.data[symbol],
                timestamp: new Date()
              }
            }
          })
        } else {
          console.error('加载实时数据失败:', result.error)
        }
      } catch (error) {
        console.error('加载实时数据异常:', error)
      } finally {
        loading.value = false
      }
    }
    
    const loadHistoricalData = async () => {
      if (!activeContract.value) return
      
      loadingHistorical.value = true
      
      try {
        const result = await futuresApi.getDailyData(
          activeContract.value,
          queryParams.startDate,
          queryParams.endDate,
          queryParams.period
        )
        
        if (result.success) {
          historicalData.value[activeContract.value] = result.data
          currentDataPage.value = 1
        } else {
          console.error('加载历史数据失败:', result.error)
        }
      } catch (error) {
        console.error('加载历史数据异常:', error)
      } finally {
        loadingHistorical.value = false
      }
    }
    
    const refreshAllData = () => {
      loadRealtimeData()
      if (activeContract.value) {
        loadHistoricalData()
      }
    }
    
    const resetQueryParams = () => {
      initQueryParams()
    }
    
    const exportData = () => {
      // 导出数据功能
      console.log('导出数据功能开发中...')
    }
    
    // 格式化方法
    const formatPrice = (price) => {
      return dataFormatter.formatPrice(price)
    }
    
    const formatVolume = (volume) => {
      return dataFormatter.formatVolume(volume)
    }
    
    const formatDateTime = (datetime) => {
      return dataFormatter.formatDateTime(datetime)
    }
    
    const formatDate = (date) => {
      return dataFormatter.formatDateTime(date, 'date')
    }
    
    const formatChange = (change, changePercent) => {
      const formatted = dataFormatter.formatChange(change, changePercent)
      return `${formatted.change} (${formatted.percent})`
    }
    
    // 样式类方法
    const getPriceChangeClass = (data) => {
      if (!data || !data.change) return 'neutral'
      return data.change > 0 ? 'positive' : data.change < 0 ? 'negative' : 'neutral'
    }
    
    const getPriceClass = (close, open) => {
      if (!close || !open) return 'neutral'
      return close > open ? 'positive' : close < open ? 'negative' : 'neutral'
    }
    
    const getChangeClass = (change) => {
      if (!change) return 'neutral'
      return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
    }
    
    const getContractTypeText = (type) => {
      const typeMap = {
        'main': '主力合约',
        'continuous': '连续合约',
        'index': '指数合约',
        'specific': '具体合约'
      }
      return typeMap[type] || type
    }
    
    // 组件挂载
    onMounted(() => {
      initQueryParams()
    })
    
    // 监听活跃合约变化
    watch(activeContract, (newSymbol) => {
      if (newSymbol && !realtimeData.value[newSymbol]) {
        loadRealtimeData()
      }
    })
    
    return {
      // 响应式数据
      showSelector,
      loading,
      loadingHistorical,
      loadingText,
      showChart,
      selectedContracts,
      activeContract,
      realtimeData,
      historicalData,
      queryParams,
      currentDataPage,
      dataPageSize,
      
      // 计算属性
      today,
      activeContractData,
      hasData,
      paginatedHistoricalData,
      totalDataPages,
      
      // 方法
      handleContractSelected,
      handleContractsConfirmed,
      handleViewData,
      handleViewInfo,
      setActiveContract,
      removeContract,
      clearAllContracts,
      loadRealtimeData,
      loadHistoricalData,
      refreshAllData,
      resetQueryParams,
      exportData,
      formatPrice,
      formatVolume,
      formatDateTime,
      formatDate,
      formatChange,
      getPriceChangeClass,
      getPriceClass,
      getChangeClass,
      getContractTypeText
    }
  }
}
</script>