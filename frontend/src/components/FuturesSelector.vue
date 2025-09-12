<template>
  <el-card shadow="hover">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <h3 style="margin:0;font-weight:600;">期货合约选择器</h3>
        <el-button :loading="loading" size="small" @click="refreshData" type="primary" plain>
          刷新
        </el-button>
      </div>
    </template>

    <el-form inline label-position="left" style="margin-bottom: 8px;">
      <el-form-item>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索合约代码或名称..."
          clearable
          @input="handleSearch"
          style="width: 320px;"
        />
      </el-form-item>
      <el-form-item label="交易所">
        <el-select v-model="selectedExchange" placeholder="全部交易所" clearable @change="handleFilterChange" style="min-width:160px;">
          <el-option 
            v-for="exchange in exchanges" 
            :key="exchange.code" 
            :label="exchange.name" 
            :value="exchange.name"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="品种分类">
        <el-select v-model="selectedCategory" placeholder="全部分类" clearable @change="handleFilterChange" style="min-width:160px;">
          <el-option 
            v-for="category in categories" 
            :key="category.code" 
            :label="category.name" 
            :value="category.name"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="夜盘交易">
        <el-select v-model="nightTradingFilter" placeholder="全部" clearable @change="handleFilterChange" style="min-width:140px;">
          <el-option label="有夜盘" value="true" />
          <el-option label="无夜盘" value="false" />
        </el-select>
      </el-form-item>
    </el-form>

    <el-alert v-if="error" :title="error" type="error" show-icon style="margin-bottom:12px;" />

    <el-skeleton v-if="loading" animated :rows="4" style="margin: 12px 0;" />

    <div v-if="statistics && !loading" style="display:flex;gap:16px;margin:12px 0;flex-wrap:wrap;">
      <el-tag type="info">总合约数: {{ statistics.total_contracts }}</el-tag>
      <el-tag type="warning">夜盘合约: {{ statistics.night_trading_count }}</el-tag>
      <el-tag>当前显示: {{ filteredContracts.length }}</el-tag>
    </div>

    <el-row :gutter="12" v-if="!loading && !error">
      <el-col v-for="contract in paginatedContracts" :key="contract.symbol" :xs="24" :sm="12" :md="8" :lg="6">
        <el-card @click="toggleContract(contract)" shadow="hover" style="margin-bottom:12px;cursor: pointer;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <div style="font-weight:700;">{{ contract.symbol }}</div>
            <div style="display:flex;gap:6px;">
              <el-tag v-if="contract.has_night_trading" type="warning" size="small">夜盘</el-tag>
              <el-tag type="info" size="small">{{ getExchangeShortName(contract.exchange) }}</el-tag>
            </div>
          </div>
          <div style="color: var(--el-text-color-secondary);margin-bottom:8px;">{{ contract.name }}</div>
          <el-descriptions :column="2" size="small" border>
            <el-descriptions-item label="分类">{{ contract.category }}</el-descriptions-item>
            <el-descriptions-item label="单位">{{ contract.unit }}</el-descriptions-item>
            <el-descriptions-item label="最小变动">{{ contract.tick_size }}</el-descriptions-item>
          </el-descriptions>
          <div v-if="contract.description" style="margin-top:8px;color: var(--el-text-color-secondary);">{{ contract.description }}</div>
          <div style="display:flex;gap:8px;margin-top:12px;">
            <el-button size="small" type="success" @click.stop="viewData(contract)">数据</el-button>
            <el-button size="small" type="info" @click.stop="viewInfo(contract)">详情</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="!loading && !error && filteredContracts.length === 0" style="margin:24px 0;">
      <el-empty description="暂无匹配的合约"></el-empty>
    </div>

    <div v-if="totalPages > 1 && !loading" style="display:flex;justify-content:center;margin-top:8px;">
      <el-pagination
        background
        layout="prev, pager, next, jumper"
        :current-page="currentPage"
        :page-size="pageSize"
        :total="filteredContracts.length"
        @current-change="(p)=> currentPage = p"
      />
    </div>

    <div v-if="selectedContracts.length > 0" style="margin-top:16px;">
      <h4 style="margin: 12px 0;">已选合约 ({{ selectedContracts.length }})</h4>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
        <el-tag
          v-for="symbol in selectedContracts"
          :key="symbol"
          closable
          @close="removeContract(symbol)"
          type="primary"
          effect="light"
        >
          {{ symbol }} - {{ getContractName(symbol) }}
        </el-tag>
      </div>
      <div style="display:flex;gap:8px;">
        <el-button type="primary" @click="confirmSelection">确认选择 ({{ selectedContracts.length }})</el-button>
        <el-button @click="clearSelection">清空选择</el-button>
      </div>
    </div>

  </el-card>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { futuresApi } from '../api/futures'

export default {
  name: 'FuturesSelector',
  emits: ['contract-selected', 'contracts-confirmed'],
  setup(props, { emit }) {
    // 响应式数据
    const loading = ref(false)
    const error = ref('')
    const searchKeyword = ref('')
    const selectedExchange = ref('')
    const selectedCategory = ref('')
    const nightTradingFilter = ref('')
    const currentPage = ref(1)
    const pageSize = ref(12)
    
    // 数据存储
    const contracts = ref([])
    const exchanges = ref([])
    const categories = ref([])
    const statistics = ref(null)
    const selectedContracts = ref([])
    
    // 计算属性
    const filteredContracts = computed(() => {
      let filtered = contracts.value
      
      // 搜索过滤
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        filtered = filtered.filter(contract => 
          contract.symbol.toLowerCase().includes(keyword) ||
          contract.name.toLowerCase().includes(keyword) ||
          contract.underlying.toLowerCase().includes(keyword)
        )
      }
      
      // 交易所过滤
      if (selectedExchange.value) {
        filtered = filtered.filter(contract => 
          contract.exchange === selectedExchange.value
        )
      }
      
      // 品种分类过滤
      if (selectedCategory.value) {
        filtered = filtered.filter(contract => 
          contract.category === selectedCategory.value
        )
      }
      
      // 夜盘交易过滤
      if (nightTradingFilter.value !== '') {
        const hasNightTrading = nightTradingFilter.value === 'true'
        filtered = filtered.filter(contract => 
          contract.has_night_trading === hasNightTrading
        )
      }
      
      return filtered
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredContracts.value.length / pageSize.value)
    })
    
    const paginatedContracts = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredContracts.value.slice(start, end)
    })
    
    // 方法
    const loadData = async () => {
      loading.value = true
      error.value = ''
      
      try {
        // 并行加载数据
        const [contractsRes, exchangesRes, categoriesRes, statsRes] = await Promise.all([
          futuresApi.getContracts(),
          futuresApi.getExchanges(),
          futuresApi.getCategories(),
          futuresApi.getStatistics()
        ])
        
        if (contractsRes.success) {
          contracts.value = Object.values(contractsRes.data)
        }
        
        if (exchangesRes.success) {
          exchanges.value = exchangesRes.data
        }
        
        if (categoriesRes.success) {
          categories.value = categoriesRes.data
        }
        
        if (statsRes.success) {
          statistics.value = statsRes.data
        }
        
      } catch (err) {
        error.value = '加载数据失败: ' + (err.message || '未知错误')
      } finally {
        loading.value = false
      }
    }
    
    const refreshData = () => {
      loadData()
    }
    
    const handleSearch = () => {
      currentPage.value = 1
    }
    
    const clearSearch = () => {
      searchKeyword.value = ''
      currentPage.value = 1
    }
    
    const handleFilterChange = () => {
      currentPage.value = 1
    }
    
    const toggleContract = (contract) => {
      const index = selectedContracts.value.indexOf(contract.symbol)
      if (index > -1) {
        selectedContracts.value.splice(index, 1)
      } else {
        selectedContracts.value.push(contract.symbol)
      }
      
      emit('contract-selected', {
        contract,
        selected: index === -1,
        selectedContracts: [...selectedContracts.value]
      })
    }
    
    const removeContract = (symbol) => {
      const index = selectedContracts.value.indexOf(symbol)
      if (index > -1) {
        selectedContracts.value.splice(index, 1)
      }
    }
    
    const clearSelection = () => {
      selectedContracts.value = []
    }
    
    const confirmSelection = () => {
      const selectedContractData = selectedContracts.value.map(symbol => {
        return contracts.value.find(c => c.symbol === symbol)
      }).filter(Boolean)
      
      emit('contracts-confirmed', {
        symbols: [...selectedContracts.value],
        contracts: selectedContractData
      })
    }
    
    const viewData = (contract) => {
      // 触发查看数据事件
      emit('view-data', contract)
    }
    
    const viewInfo = (contract) => {
      // 触发查看详情事件
      emit('view-info', contract)
    }
    
    const getContractName = (symbol) => {
      const contract = contracts.value.find(c => c.symbol === symbol)
      return contract ? contract.name : symbol
    }
    
    const getExchangeShortName = (exchangeName) => {
      const exchangeMap = {
        '上海期货交易所': 'SHFE',
        '上海国际能源交易中心': 'INE',
        '大连商品交易所': 'DCE',
        '郑州商品交易所': 'CZCE',
        '中国金融期货交易所': 'CFFEX',
        '广州期货交易所': 'GFEX'
      }
      return exchangeMap[exchangeName] || exchangeName
    }
    
    // 监听过滤条件变化，重置页码
    watch([selectedExchange, selectedCategory, nightTradingFilter], () => {
      currentPage.value = 1
    })
    
    // 组件挂载时加载数据
    onMounted(() => {
      loadData()
    })
    
    return {
      // 响应式数据
      loading,
      error,
      searchKeyword,
      selectedExchange,
      selectedCategory,
      nightTradingFilter,
      currentPage,
      pageSize,
      contracts,
      exchanges,
      categories,
      statistics,
      selectedContracts,
      
      // 计算属性
      filteredContracts,
      totalPages,
      paginatedContracts,
      
      // 方法
      loadData,
      refreshData,
      handleSearch,
      clearSearch,
      handleFilterChange,
      toggleContract,
      removeContract,
      clearSelection,
      confirmSelection,
      viewData,
      viewInfo,
      getContractName,
      getExchangeShortName
    }
  }
}
</script>