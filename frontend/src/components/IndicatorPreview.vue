<template>
  <div class="indicator-preview">
    <!-- 预览控制栏 -->
    <div class="preview-controls">
      <div class="controls-left">
        <el-button-group>
          <el-button 
            :type="viewMode === 'chart' ? 'primary' : 'default'"
            @click="viewMode = 'chart'"
            :icon="TrendCharts"
          >
            图表预览
          </el-button>
          <el-button 
            :type="viewMode === 'data' ? 'primary' : 'default'"
            @click="viewMode = 'data'"
            :icon="DataBoard"
          >
            数据预览
          </el-button>
          <el-button 
            :type="viewMode === 'validation' ? 'primary' : 'default'"
            @click="viewMode = 'validation'"
            :icon="CircleCheck"
          >
            验证结果
          </el-button>
        </el-button-group>
      </div>
      
      <div class="controls-right">
        <el-select 
          v-model="selectedTimeframe" 
          @change="updateChartData"
          style="width: 120px"
        >
          <el-option label="1分钟" value="1m" />
          <el-option label="5分钟" value="5m" />
          <el-option label="15分钟" value="15m" />
          <el-option label="1小时" value="1h" />
          <el-option label="1天" value="1d" />
        </el-select>
        
        <el-input-number 
          v-model="dataCount" 
          :min="50" 
          :max="1000" 
          :step="50" 
          @change="updateChartData"
          style="width: 120px; margin-left: 8px"
        />
        
        <el-button 
          :icon="Refresh" 
          @click="refreshPreview"
          style="margin-left: 8px"
        >
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 预览内容 -->
    <div class="preview-content">
      <!-- 图表预览 -->
      <div v-show="viewMode === 'chart'" class="chart-view">
        <div class="chart-container" ref="chartContainer">
          <!-- KLineChart 将在这里渲染 -->
        </div>
        
        <!-- 图表信息 -->
        <div class="chart-info" v-if="indicator">
          <div class="info-section">
            <h4>指标信息</h4>
            <el-descriptions :column="3" size="small">
              <el-descriptions-item label="名称">
                {{ indicator.name }}
              </el-descriptions-item>
              <el-descriptions-item label="简称">
                {{ indicator.shortName || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="精度">
                {{ indicator.precision || 2 }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <div class="info-section" v-if="indicator.params && indicator.params.length > 0">
            <h4>参数设置</h4>
            <el-table :data="indicator.params" size="small">
              <el-table-column prop="name" label="参数名" width="100" />
              <el-table-column prop="default" label="默认值" width="80" />
              <el-table-column prop="min" label="最小值" width="80" />
              <el-table-column prop="max" label="最大值" width="80" />
              <el-table-column prop="step" label="步长" width="60" />
              <el-table-column label="当前值" width="120">
                <template #default="{ row, $index }">
                  <el-input-number 
                    v-model="paramValues[$index]" 
                    :min="row.min" 
                    :max="row.max" 
                    :step="row.step || 1"
                    size="small"
                    @change="updateIndicatorParams"
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <div class="info-section" v-if="indicator.plots && indicator.plots.length > 0">
            <h4>输出线条</h4>
            <el-table :data="indicator.plots" size="small">
              <el-table-column prop="key" label="键名" width="80" />
              <el-table-column prop="title" label="显示名" width="100" />
              <el-table-column prop="type" label="类型" width="80" />
              <el-table-column label="颜色" width="100">
                <template #default="{ row }">
                  <div class="color-display">
                    <div 
                      class="color-box" 
                      :style="{ backgroundColor: row.color }"
                    ></div>
                    <span>{{ row.color }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="可见性" width="80">
                <template #default="{ row, $index }">
                  <el-switch 
                    v-model="plotVisibility[$index]" 
                    @change="updatePlotVisibility"
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
      
      <!-- 数据预览 -->
      <div v-show="viewMode === 'data'" class="data-view">
        <div class="data-controls">
          <el-input 
            v-model="dataFilter" 
            placeholder="搜索数据..." 
            :prefix-icon="Search"
            style="width: 200px"
          />
          
          <el-button 
            :icon="Download" 
            @click="exportData"
            style="margin-left: 8px"
          >
            导出数据
          </el-button>
        </div>
        
        <div class="data-table">
          <el-table 
            :data="filteredCalculationData" 
            height="400" 
            size="small"
            stripe
          >
            <el-table-column 
              prop="index" 
              label="序号" 
              width="60" 
              fixed="left"
            />
            <el-table-column 
              prop="timestamp" 
              label="时间" 
              width="180" 
              :formatter="formatTimestamp"
            />
            <el-table-column 
              prop="open" 
              label="开盘" 
              width="80" 
              :formatter="formatNumber"
            />
            <el-table-column 
              prop="high" 
              label="最高" 
              width="80" 
              :formatter="formatNumber"
            />
            <el-table-column 
              prop="low" 
              label="最低" 
              width="80" 
              :formatter="formatNumber"
            />
            <el-table-column 
              prop="close" 
              label="收盘" 
              width="80" 
              :formatter="formatNumber"
            />
            <el-table-column 
              prop="volume" 
              label="成交量" 
              width="100" 
              :formatter="formatVolume"
            />
            
            <!-- 动态生成指标列 -->
            <el-table-column 
              v-for="plot in indicator?.plots || []" 
              :key="plot.key"
              :prop="`indicator.${plot.key}`"
              :label="plot.title || plot.key"
              width="100"
              :formatter="(row) => formatIndicatorValue(row, plot.key)"
            />
          </el-table>
        </div>
        
        <!-- 数据统计 -->
        <div class="data-statistics" v-if="calculationData.length > 0">
          <h4>数据统计</h4>
          <el-row :gutter="16">
            <el-col :span="6">
              <el-statistic title="数据条数" :value="calculationData.length" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="有效指标值" :value="validIndicatorCount" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="空值数量" :value="nullIndicatorCount" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="计算耗时" :value="calculationTime" suffix="ms" />
            </el-col>
          </el-row>
        </div>
      </div>
      
      <!-- 验证结果 -->
      <div v-show="viewMode === 'validation'" class="validation-view">
        <div class="validation-summary">
          <el-alert 
            :type="validationResult?.valid ? 'success' : 'error'"
            :title="validationResult?.valid ? '验证通过' : '验证失败'"
            :description="getValidationSummary()"
            show-icon
            :closable="false"
          />
        </div>
        
        <div class="validation-details" v-if="validationResult">
          <!-- 错误信息 -->
          <div v-if="validationResult.errors.length > 0" class="validation-section">
            <h4 class="error-title">
              <el-icon><CircleClose /></el-icon>
              错误信息 ({{ validationResult.errors.length }})
            </h4>
            <el-alert 
              v-for="(error, index) in validationResult.errors" 
              :key="index"
              type="error"
              :title="error"
              :closable="false"
              style="margin-bottom: 8px"
            />
          </div>
          
          <!-- 警告信息 -->
          <div v-if="validationResult.warnings.length > 0" class="validation-section">
            <h4 class="warning-title">
              <el-icon><Warning /></el-icon>
              警告信息 ({{ validationResult.warnings.length }})
            </h4>
            <el-alert 
              v-for="(warning, index) in validationResult.warnings" 
              :key="index"
              type="warning"
              :title="warning"
              :closable="false"
              style="margin-bottom: 8px"
            />
          </div>
          
          <!-- VNPY验证结果 -->
          <div v-if="validationResult.vnpyValidation" class="validation-section">
            <h4>
              <el-icon><Check v-if="validationResult.vnpyValidation.valid" /><Close v-else /></el-icon>
              VNPY格式验证
            </h4>
            <el-descriptions :column="2" size="small">
              <el-descriptions-item label="验证状态">
                <el-tag :type="validationResult.vnpyValidation.valid ? 'success' : 'danger'">
                  {{ validationResult.vnpyValidation.valid ? '通过' : '失败' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="错误数量">
                {{ validationResult.vnpyValidation.errors.length }}
              </el-descriptions-item>
              <el-descriptions-item label="警告数量">
                {{ validationResult.vnpyValidation.warnings.length }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <!-- KLineChart验证结果 -->
          <div v-if="validationResult.klineValidation" class="validation-section">
            <h4>
              <el-icon><Check v-if="validationResult.klineValidation.valid" /><Close v-else /></el-icon>
              KLineChart格式验证
            </h4>
            <el-descriptions :column="2" size="small">
              <el-descriptions-item label="验证状态">
                <el-tag :type="validationResult.klineValidation.valid ? 'success' : 'danger'">
                  {{ validationResult.klineValidation.valid ? '通过' : '失败' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="错误数量">
                {{ validationResult.klineValidation.errors.length }}
              </el-descriptions-item>
              <el-descriptions-item label="警告数量">
                {{ validationResult.klineValidation.warnings.length }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <!-- 计算测试结果 -->
          <div v-if="validationResult.calculationTest" class="validation-section">
            <h4>
              <el-icon><Check v-if="validationResult.calculationTest.success" /><Close v-else /></el-icon>
              计算测试结果
            </h4>
            <el-descriptions :column="2" size="small">
              <el-descriptions-item label="测试状态">
                <el-tag :type="validationResult.calculationTest.success ? 'success' : 'danger'">
                  {{ validationResult.calculationTest.success ? '通过' : '失败' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="结果类型">
                {{ getResultType(validationResult.calculationTest.result) }}
              </el-descriptions-item>
              <el-descriptions-item label="结果长度">
                {{ Array.isArray(validationResult.calculationTest.result) ? validationResult.calculationTest.result.length : '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  DataBoard,
  CircleCheck,
  Refresh,
  Download,
  Search,
  CircleClose,
  Warning,
  Check,
  Close
} from '@element-plus/icons-vue'
import { init as initKLineChart, dispose as disposeKLineChart } from 'klinecharts'
import IndicatorValidator from '@/utils/indicatorValidator'

// Props
const props = defineProps({
  indicator: {
    type: Object,
    default: null
  },
  compiledResult: {
    type: Object,
    default: null
  }
})

// 响应式数据
const chartContainer = ref(null)
const viewMode = ref('chart')
const selectedTimeframe = ref('1d')
const dataCount = ref(200)
const dataFilter = ref('')

// 图表和数据
let chart = null
const chartData = ref([])
const calculationData = ref([])
const calculationTime = ref(0)

// 参数控制
const paramValues = ref([])
const plotVisibility = ref([])

// 验证结果
const validationResult = ref(null)

// 计算属性
const filteredCalculationData = computed(() => {
  if (!dataFilter.value) return calculationData.value
  
  const filter = dataFilter.value.toLowerCase()
  return calculationData.value.filter(item => {
    return Object.values(item).some(value => 
      String(value).toLowerCase().includes(filter)
    )
  })
})

const validIndicatorCount = computed(() => {
  if (!calculationData.value.length || !props.indicator?.plots) return 0
  
  return calculationData.value.reduce((count, item) => {
    const hasValidValue = props.indicator.plots.some(plot => {
      const value = item.indicator?.[plot.key]
      return value !== null && value !== undefined && !isNaN(value)
    })
    return count + (hasValidValue ? 1 : 0)
  }, 0)
})

const nullIndicatorCount = computed(() => {
  return calculationData.value.length - validIndicatorCount.value
})

// 监听器
watch(() => props.indicator, (newIndicator) => {
  if (newIndicator) {
    initializeParams()
    updatePreview()
  }
}, { immediate: true })

watch(() => props.compiledResult, (newResult) => {
  if (newResult) {
    validateIndicator()
  }
}, { immediate: true })

// 组件挂载
onMounted(() => {
  updateChartData()
})

// 组件卸载
onUnmounted(() => {
  if (chart) {
    disposeKLineChart(chart)
  }
})

// 初始化参数
function initializeParams() {
  if (props.indicator?.params) {
    paramValues.value = props.indicator.params.map(param => param.default)
  }
  
  if (props.indicator?.plots) {
    plotVisibility.value = props.indicator.plots.map(() => true)
  }
}

// 更新图表数据
function updateChartData() {
  chartData.value = IndicatorValidator.generateTestData(dataCount.value)
  updatePreview()
}

// 更新预览
function updatePreview() {
  if (!props.indicator) return
  
  calculateIndicatorData()
  
  if (viewMode.value === 'chart') {
    nextTick(() => {
      initChart()
    })
  }
}

// 计算指标数据
function calculateIndicatorData() {
  if (!props.indicator || !chartData.value.length) return
  
  const startTime = performance.now()
  
  try {
    let indicatorResult = []
    
    if (props.indicator.calc) {
      // KLineChart格式计算
      indicatorResult = props.indicator.calc(chartData.value, ...paramValues.value)
    }
    
    // 合并K线数据和指标数据
    calculationData.value = chartData.value.map((kline, index) => {
      const item = {
        index: index + 1,
        ...kline,
        indicator: {}
      }
      
      if (indicatorResult && indicatorResult[index]) {
        if (typeof indicatorResult[index] === 'object') {
          item.indicator = indicatorResult[index]
        } else {
          // 单值结果，使用第一个plot的key
          const firstPlotKey = props.indicator.plots?.[0]?.key || 'value'
          item.indicator[firstPlotKey] = indicatorResult[index]
        }
      }
      
      return item
    })
    
    calculationTime.value = Math.round(performance.now() - startTime)
    
  } catch (error) {
    ElMessage.error(`指标计算失败: ${error.message}`)
    calculationData.value = []
    calculationTime.value = 0
  }
}

// 初始化图表
function initChart() {
  if (!chartContainer.value || !chartData.value.length) return
  
  // 销毁现有图表
  if (chart) {
    disposeKLineChart(chart)
  }
  
  // 创建新图表
  chart = initKLineChart(chartContainer.value)
  
  // 应用K线数据
  chart.applyNewData(chartData.value)
  
  // 添加自定义指标
  if (props.indicator) {
    try {
      // 创建指标副本，应用当前参数
      const indicatorCopy = {
        ...props.indicator,
        params: props.indicator.params?.map((param, index) => ({
          ...param,
          default: paramValues.value[index] ?? param.default
        }))
      }
      
      chart.createIndicator(indicatorCopy, true)
      
      // 应用可见性设置
      updatePlotVisibility()
      
    } catch (error) {
      ElMessage.error(`图表渲染失败: ${error.message}`)
    }
  }
}

// 更新指标参数
function updateIndicatorParams() {
  updatePreview()
}

// 更新线条可见性
function updatePlotVisibility() {
  // KLineChart的可见性控制需要通过样式实现
  // 这里可以根据实际API调整
}

// 刷新预览
function refreshPreview() {
  updateChartData()
  ElMessage.success('预览已刷新')
}

// 验证指标
function validateIndicator() {
  if (!props.compiledResult) {
    validationResult.value = null
    return
  }
  
  validationResult.value = IndicatorValidator.validateIndicator(props.compiledResult)
}

// 导出数据
function exportData() {
  if (!calculationData.value.length) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  try {
    const csvContent = convertToCSV(calculationData.value)
    downloadCSV(csvContent, `indicator_data_${Date.now()}.csv`)
    ElMessage.success('数据导出成功')
  } catch (error) {
    ElMessage.error(`导出失败: ${error.message}`)
  }
}

// 转换为CSV格式
function convertToCSV(data) {
  if (!data.length) return ''
  
  const headers = ['序号', '时间', '开盘', '最高', '最低', '收盘', '成交量']
  
  // 添加指标列标题
  if (props.indicator?.plots) {
    headers.push(...props.indicator.plots.map(plot => plot.title || plot.key))
  }
  
  const rows = [headers.join(',')]
  
  data.forEach(item => {
    const row = [
      item.index,
      formatTimestamp(null, null, item.timestamp),
      item.open,
      item.high,
      item.low,
      item.close,
      item.volume
    ]
    
    // 添加指标值
    if (props.indicator?.plots) {
      props.indicator.plots.forEach(plot => {
        const value = item.indicator?.[plot.key]
        row.push(value ?? '')
      })
    }
    
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

// 下载CSV文件
function downloadCSV(content, filename) {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// 格式化函数
function formatTimestamp(row, column, value) {
  return new Date(value).toLocaleString()
}

function formatNumber(row, column, value) {
  return typeof value === 'number' ? value.toFixed(2) : value
}

function formatVolume(row, column, value) {
  if (typeof value !== 'number') return value
  
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return value.toString()
}

function formatIndicatorValue(row, key) {
  const value = row.indicator?.[key]
  return typeof value === 'number' ? value.toFixed(4) : (value ?? '-')
}

function getValidationSummary() {
  if (!validationResult.value) return ''
  
  const { errors, warnings } = validationResult.value
  return `错误: ${errors.length}个, 警告: ${warnings.length}个`
}

function getResultType(result) {
  if (result === null || result === undefined) return '无结果'
  if (Array.isArray(result)) {
    if (result.length === 0) return '空数组'
    const firstItem = result[0]
    if (typeof firstItem === 'object') return '对象数组'
    if (typeof firstItem === 'number') return '数值数组'
    return '混合数组'
  }
  return typeof result
}
</script>

<style scoped>
.indicator-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--tv-bg-secondary);
}

.preview-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-primary);
}

.controls-right {
  display: flex;
  align-items: center;
}

.preview-content {
  flex: 1;
  overflow: hidden;
}

.chart-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex: 1;
  min-height: 300px;
}

.chart-info {
  border-top: 1px solid var(--tv-border-primary);
  max-height: 300px;
  overflow-y: auto;
  padding: 16px;
}

.info-section {
  margin-bottom: 24px;
}

.info-section h4 {
  margin: 0 0 12px 0;
  color: var(--tv-text-primary);
  font-size: 14px;
}

.color-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-box {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  border: 1px solid var(--tv-border-primary);
}

.data-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.data-controls {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.data-table {
  flex: 1;
  margin-bottom: 16px;
}

.data-statistics {
  border-top: 1px solid var(--tv-border-primary);
  padding-top: 16px;
}

.data-statistics h4 {
  margin: 0 0 16px 0;
  color: var(--tv-text-primary);
}

.validation-view {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}

.validation-summary {
  margin-bottom: 24px;
}

.validation-section {
  margin-bottom: 24px;
  padding: 16px;
  border: 1px solid var(--tv-border-primary);
  border-radius: 4px;
}

.validation-section h4 {
  margin: 0 0 12px 0;
  color: var(--tv-text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-title {
  color: var(--tv-danger);
}

.warning-title {
  color: var(--tv-warning);
}
</style>