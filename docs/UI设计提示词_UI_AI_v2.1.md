# DAOTrader v2.1 UI设计提示词 (UI AI)

## 执行指令概述

你是DAOTrader v2.1的专业UI设计AI，负责设计AKShare数据接入与VNPY回测功能的用户界面。严格按照本提示词执行，零自由度，确保界面美观、易用、符合量化交易平台的专业标准。

## 设计原则

### 核心设计理念
- **专业性**: 体现量化交易平台的专业性和可信度
- **效率性**: 界面操作高效，减少用户操作步骤
- **清晰性**: 信息层次清晰，重要数据突出显示
- **一致性**: 与现有DAOTrader界面风格保持一致
- **响应式**: 支持不同屏幕尺寸的设备

### 色彩规范
```css
/* 主色调 */
--primary-color: #1890ff;        /* 主蓝色 */
--primary-light: #40a9ff;        /* 浅蓝色 */
--primary-dark: #096dd9;         /* 深蓝色 */

/* 辅助色 */
--success-color: #52c41a;        /* 成功绿 */
--warning-color: #faad14;        /* 警告橙 */
--error-color: #ff4d4f;          /* 错误红 */
--info-color: #13c2c2;           /* 信息青 */

/* 中性色 */
--text-primary: #262626;         /* 主文本 */
--text-secondary: #595959;       /* 次要文本 */
--text-disabled: #bfbfbf;        /* 禁用文本 */
--border-color: #d9d9d9;         /* 边框色 */
--background-color: #fafafa;     /* 背景色 */
--card-background: #ffffff;      /* 卡片背景 */

/* 数据色彩 */
--profit-color: #f6ffed;         /* 盈利背景 */
--loss-color: #fff2f0;           /* 亏损背景 */
--profit-text: #389e0d;          /* 盈利文本 */
--loss-text: #cf1322;            /* 亏损文本 */
```

### 字体规范
```css
/* 字体家族 */
--font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
--font-family-code: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;

/* 字体大小 */
--font-size-xs: 12px;            /* 辅助信息 */
--font-size-sm: 14px;            /* 正文 */
--font-size-base: 16px;          /* 基础 */
--font-size-lg: 18px;            /* 小标题 */
--font-size-xl: 20px;            /* 标题 */
--font-size-xxl: 24px;           /* 大标题 */

/* 字重 */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

## 页面布局设计

### 1. 回测主页面布局

#### 整体结构
```
┌─────────────────────────────────────────────────────────────┐
│                        顶部导航栏                            │
├─────────────────────────────────────────────────────────────┤
│  侧边栏  │                   主内容区                        │
│         │  ┌─────────────────────────────────────────────┐  │
│  数据    │  │              回测配置面板                    │  │
│  管理    │  └─────────────────────────────────────────────┘  │
│         │  ┌─────────────────────────────────────────────┐  │
│  策略    │  │              回测结果展示                    │  │
│  管理    │  │                                           │  │
│         │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐    │  │
│  历史    │  │  │ 收益图表 │  │ 指标卡片 │  │ 交易记录 │    │  │
│  记录    │  │  └─────────┘  └─────────┘  └─────────┘    │  │
│         │  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### 响应式布局
```css
/* 桌面端 (≥1200px) */
.backtest-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  grid-template-rows: 64px 1fr;
  height: 100vh;
}

/* 平板端 (768px-1199px) */
@media (max-width: 1199px) {
  .backtest-layout {
    grid-template-columns: 240px 1fr;
  }
}

/* 移动端 (<768px) */
@media (max-width: 767px) {
  .backtest-layout {
    grid-template-columns: 1fr;
    grid-template-rows: 64px 1fr;
  }
  
  .sidebar {
    position: fixed;
    left: -280px;
    transition: left 0.3s ease;
  }
  
  .sidebar.open {
    left: 0;
  }
}
```

### 2. 数据管理界面

#### 数据下载面板
```html
<div class="data-download-panel">
  <div class="panel-header">
    <h3>历史数据下载</h3>
    <div class="header-actions">
      <el-button type="text" @click="showBatchDownload">批量下载</el-button>
    </div>
  </div>
  
  <div class="download-form">
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="股票代码">
          <el-input 
            v-model="form.symbol" 
            placeholder="如：000001"
            class="symbol-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-col>
      
      <el-col :span="8">
        <el-form-item label="交易所">
          <el-select v-model="form.exchange" placeholder="选择交易所">
            <el-option label="上海证券交易所" value="SSE" />
            <el-option label="深圳证券交易所" value="SZSE" />
          </el-select>
        </el-form-item>
      </el-col>
      
      <el-col :span="8">
        <el-form-item label="数据频率">
          <el-select v-model="form.interval" placeholder="选择频率">
            <el-option label="日线" value="daily" />
            <el-option label="60分钟" value="60min" />
            <el-option label="30分钟" value="30min" />
            <el-option label="15分钟" value="15min" />
            <el-option label="5分钟" value="5min" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
    
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="form.startDate"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="8">
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="form.endDate"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="8">
        <el-form-item>
          <el-button 
            type="primary" 
            @click="downloadData"
            :loading="downloading"
            style="width: 100%"
          >
            <el-icon><Download /></el-icon>
            下载数据
          </el-button>
        </el-form-item>
      </el-col>
    </el-row>
  </div>
  
  <!-- 下载进度 -->
  <div v-if="downloadProgress.show" class="download-progress">
    <div class="progress-header">
      <span>{{ downloadProgress.message }}</span>
      <el-button type="text" @click="cancelDownload">取消</el-button>
    </div>
    <el-progress 
      :percentage="downloadProgress.percent" 
      :status="downloadProgress.status"
    />
  </div>
</div>
```

#### 数据状态展示
```html
<div class="data-status-panel">
  <div class="panel-header">
    <h3>数据状态</h3>
    <div class="header-actions">
      <el-button type="text" @click="refreshDataStatus">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>
  </div>
  
  <div class="data-status-grid">
    <div 
      v-for="item in dataStatusList" 
      :key="item.symbol"
      class="data-status-card"
    >
      <div class="card-header">
        <div class="symbol-info">
          <span class="symbol">{{ item.symbol }}</span>
          <span class="name">{{ item.name }}</span>
        </div>
        <el-tag 
          :type="getStatusType(item.status)"
          size="small"
        >
          {{ getStatusText(item.status) }}
        </el-tag>
      </div>
      
      <div class="card-content">
        <div class="data-info">
          <div class="info-item">
            <span class="label">数据量:</span>
            <span class="value">{{ item.count.toLocaleString() }}</span>
          </div>
          <div class="info-item">
            <span class="label">时间范围:</span>
            <span class="value">{{ formatDateRange(item.startDate, item.endDate) }}</span>
          </div>
          <div class="info-item">
            <span class="label">最后更新:</span>
            <span class="value">{{ formatTime(item.lastUpdate) }}</span>
          </div>
        </div>
        
        <div class="card-actions">
          <el-button type="text" size="small" @click="updateData(item)">
            更新
          </el-button>
          <el-button type="text" size="small" @click="deleteData(item)">
            删除
          </el-button>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 3. 回测配置界面

#### 策略配置面板
```html
<div class="strategy-config-panel">
  <div class="panel-header">
    <h3>回测配置</h3>
    <div class="header-actions">
      <el-button type="text" @click="saveTemplate">保存模板</el-button>
      <el-button type="text" @click="loadTemplate">加载模板</el-button>
    </div>
  </div>
  
  <el-form :model="backtestForm" label-width="120px" class="backtest-form">
    <!-- 基础配置 -->
    <div class="form-section">
      <h4 class="section-title">基础配置</h4>
      
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="交易品种">
            <el-select 
              v-model="backtestForm.symbol" 
              placeholder="选择或输入品种代码"
              filterable
              allow-create
            >
              <el-option-group label="热门股票">
                <el-option 
                  v-for="stock in popularStocks"
                  :key="stock.symbol"
                  :label="`${stock.symbol} - ${stock.name}`"
                  :value="stock.symbol"
                />
              </el-option-group>
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="数据频率">
            <el-select v-model="backtestForm.interval">
              <el-option label="日线" value="daily" />
              <el-option label="60分钟" value="60min" />
              <el-option label="30分钟" value="30min" />
              <el-option label="15分钟" value="15min" />
              <el-option label="5分钟" value="5min" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="回测开始">
            <el-date-picker
              v-model="backtestForm.startDate"
              type="date"
              placeholder="选择开始日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="回测结束">
            <el-date-picker
              v-model="backtestForm.endDate"
              type="date"
              placeholder="选择结束日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </div>
    
    <!-- 策略选择 -->
    <div class="form-section">
      <h4 class="section-title">策略选择</h4>
      
      <el-form-item label="策略类型">
        <el-select 
          v-model="backtestForm.strategyName" 
          @change="onStrategyChange"
          placeholder="选择策略"
        >
          <el-option 
            v-for="strategy in strategies"
            :key="strategy.name"
            :label="strategy.label"
            :value="strategy.name"
          >
            <div class="strategy-option">
              <span class="strategy-name">{{ strategy.label }}</span>
              <span class="strategy-desc">{{ strategy.description }}</span>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      
      <!-- 策略参数 -->
      <div v-if="selectedStrategy" class="strategy-params">
        <h5>策略参数</h5>
        <el-row :gutter="16">
          <el-col 
            v-for="param in selectedStrategy.params"
            :key="param.name"
            :span="param.span || 12"
          >
            <el-form-item :label="param.label">
              <el-input-number
                v-if="param.type === 'number'"
                v-model="backtestForm.setting[param.name]"
                :min="param.min"
                :max="param.max"
                :step="param.step"
                :precision="param.precision"
                style="width: 100%"
              />
              <el-select
                v-else-if="param.type === 'select'"
                v-model="backtestForm.setting[param.name]"
                style="width: 100%"
              >
                <el-option 
                  v-for="option in param.options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
    </div>
    
    <!-- 交易设置 -->
    <div class="form-section">
      <h4 class="section-title">交易设置</h4>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="初始资金">
            <el-input-number
              v-model="backtestForm.capital"
              :min="10000"
              :max="10000000"
              :step="10000"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="8">
          <el-form-item label="手续费率">
            <el-input-number
              v-model="backtestForm.rate"
              :min="0"
              :max="0.01"
              :step="0.0001"
              :precision="4"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="8">
          <el-form-item label="滑点">
            <el-input-number
              v-model="backtestForm.slippage"
              :min="0"
              :max="0.1"
              :step="0.001"
              :precision="3"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </div>
    
    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="resetForm">重置</el-button>
      <el-button type="primary" @click="runBacktest" :loading="running">
        <el-icon><CaretRight /></el-icon>
        开始回测
      </el-button>
    </div>
  </el-form>
</div>
```

### 4. 回测结果展示

#### 结果概览卡片
```html
<div class="backtest-results">
  <!-- 核心指标卡片 -->
  <div class="metrics-grid">
    <div class="metric-card profit-card">
      <div class="card-icon">
        <el-icon><TrendCharts /></el-icon>
      </div>
      <div class="card-content">
        <div class="metric-value" :class="getReturnClass(result.totalReturn)">
          {{ formatPercent(result.totalReturn) }}
        </div>
        <div class="metric-label">总收益率</div>
        <div class="metric-change">
          <span class="change-label">年化收益:</span>
          <span :class="getReturnClass(result.annualReturn)">
            {{ formatPercent(result.annualReturn) }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="metric-card risk-card">
      <div class="card-icon">
        <el-icon><Warning /></el-icon>
      </div>
      <div class="card-content">
        <div class="metric-value">
          {{ formatPercent(result.maxDrawdown) }}
        </div>
        <div class="metric-label">最大回撤</div>
        <div class="metric-change">
          <span class="change-label">回撤期间:</span>
          <span class="change-value">
            {{ formatDateRange(result.drawdownStart, result.drawdownEnd) }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="metric-card sharpe-card">
      <div class="card-icon">
        <el-icon><DataAnalysis /></el-icon>
      </div>
      <div class="card-content">
        <div class="metric-value">
          {{ formatNumber(result.sharpeRatio, 2) }}
        </div>
        <div class="metric-label">夏普比率</div>
        <div class="metric-change">
          <span class="change-label">信息比率:</span>
          <span class="change-value">
            {{ formatNumber(result.informationRatio, 2) }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="metric-card trade-card">
      <div class="card-icon">
        <el-icon><List /></el-icon>
      </div>
      <div class="card-content">
        <div class="metric-value">
          {{ result.totalTrades }}
        </div>
        <div class="metric-label">总交易次数</div>
        <div class="metric-change">
          <span class="change-label">胜率:</span>
          <span :class="getWinRateClass(result.winRate)">
            {{ formatPercent(result.winRate) }}
          </span>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 收益曲线图表 -->
  <div class="chart-container">
    <div class="chart-header">
      <h4>收益曲线</h4>
      <div class="chart-controls">
        <el-radio-group v-model="chartType" size="small">
          <el-radio-button label="cumulative">累计收益</el-radio-button>
          <el-radio-button label="daily">日收益</el-radio-button>
          <el-radio-button label="drawdown">回撤</el-radio-button>
        </el-radio-group>
      </div>
    </div>
    
    <div class="chart-content">
      <div id="returns-chart" class="chart"></div>
    </div>
  </div>
  
  <!-- 详细统计表格 -->
  <div class="statistics-table">
    <div class="table-header">
      <h4>详细统计</h4>
      <div class="table-actions">
        <el-button type="text" size="small" @click="exportStatistics">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>
    
    <el-table :data="statisticsData" stripe>
      <el-table-column prop="category" label="类别" width="120" />
      <el-table-column prop="metric" label="指标" width="150" />
      <el-table-column prop="value" label="数值" align="right">
        <template #default="{ row }">
          <span :class="getValueClass(row.type, row.value)">
            {{ formatValue(row.type, row.value) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="说明" show-overflow-tooltip />
    </el-table>
  </div>
  
  <!-- 交易记录 -->
  <div class="trades-table">
    <div class="table-header">
      <h4>交易记录</h4>
      <div class="table-actions">
        <el-input
          v-model="tradeFilter"
          placeholder="搜索交易记录"
          size="small"
          style="width: 200px; margin-right: 8px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="text" size="small" @click="exportTrades">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>
    
    <el-table :data="filteredTrades" stripe max-height="400">
      <el-table-column prop="datetime" label="时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.datetime) }}
        </template>
      </el-table-column>
      <el-table-column prop="direction" label="方向" width="80">
        <template #default="{ row }">
          <el-tag :type="row.direction === 'LONG' ? 'success' : 'danger'" size="small">
            {{ row.direction === 'LONG' ? '买入' : '卖出' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格" align="right" width="100">
        <template #default="{ row }">
          {{ formatPrice(row.price) }}
        </template>
      </el-table-column>
      <el-table-column prop="volume" label="数量" align="right" width="100" />
      <el-table-column prop="pnl" label="盈亏" align="right" width="120">
        <template #default="{ row }">
          <span :class="getPnlClass(row.pnl)">
            {{ formatMoney(row.pnl) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="commission" label="手续费" align="right" width="100">
        <template #default="{ row }">
          {{ formatMoney(row.commission) }}
        </template>
      </el-table-column>
      <el-table-column prop="slippage" label="滑点" align="right" width="100">
        <template #default="{ row }">
          {{ formatMoney(row.slippage) }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</div>
```

## 组件样式设计

### 1. 卡片组件样式
```css
/* 指标卡片 */
.metric-card {
  background: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
}

.profit-card::before {
  background: linear-gradient(90deg, var(--success-color), #73d13d);
}

.risk-card::before {
  background: linear-gradient(90deg, var(--error-color), #ff7875);
}

.sharpe-card::before {
  background: linear-gradient(90deg, var(--info-color), #36cfc9);
}

.trade-card::before {
  background: linear-gradient(90deg, var(--warning-color), #ffd666);
}

.card-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 24px;
  color: var(--text-disabled);
  opacity: 0.3;
}

.card-content {
  position: relative;
  z-index: 1;
}

.metric-value {
  font-size: 32px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 8px;
}

.metric-value.positive {
  color: var(--profit-text);
}

.metric-value.negative {
  color: var(--loss-text);
}

.metric-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.metric-change {
  font-size: var(--font-size-xs);
  display: flex;
  align-items: center;
  gap: 8px;
}

.change-label {
  color: var(--text-disabled);
}

.change-value {
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}
```

### 2. 表单组件样式
```css
/* 表单面板 */
.form-section {
  margin-bottom: 32px;
  padding: 24px;
  background: var(--card-background);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--primary-color);
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 40px;
  height: 2px;
  background: var(--primary-color);
}

/* 策略选项样式 */
.strategy-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.strategy-name {
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.strategy-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* 策略参数区域 */
.strategy-params {
  margin-top: 20px;
  padding: 20px;
  background: var(--background-color);
  border-radius: 6px;
  border: 1px dashed var(--border-color);
}

.strategy-params h5 {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  margin-top: 32px;
}
```

### 3. 图表容器样式
```css
/* 图表容器 */
.chart-container {
  background: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.chart-header h4 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-content {
  position: relative;
  height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}

/* 图表加载状态 */
.chart-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--text-secondary);
  font-size: var(--font-size-base);
}

.chart-loading .el-icon {
  margin-right: 8px;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### 4. 数据状态样式
```css
/* 数据状态网格 */
.data-status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.data-status-card {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.data-status-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.symbol-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.symbol {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.name {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.data-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item .label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.info-item .value {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}
```

## 交互设计规范

### 1. 加载状态设计
```html
<!-- 数据加载骨架屏 -->
<div class="loading-skeleton">
  <div class="skeleton-card">
    <div class="skeleton-header">
      <div class="skeleton-title"></div>
      <div class="skeleton-tag"></div>
    </div>
    <div class="skeleton-content">
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
      <div class="skeleton-line"></div>
    </div>
  </div>
</div>

<style>
.skeleton-card {
  background: var(--card-background);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.skeleton-title {
  width: 120px;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e6e6e6 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.skeleton-tag {
  width: 60px;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e6e6e6 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 12px;
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e6e6e6 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-line.short {
  width: 60%;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

### 2. 错误状态设计
```html
<!-- 错误状态组件 -->
<div class="error-state">
  <div class="error-icon">
    <el-icon><Warning /></el-icon>
  </div>
  <div class="error-content">
    <h4 class="error-title">{{ errorTitle }}</h4>
    <p class="error-message">{{ errorMessage }}</p>
    <div class="error-actions">
      <el-button @click="retry">重试</el-button>
      <el-button type="text" @click="reportError">报告问题</el-button>
    </div>
  </div>
</div>

<style>
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.error-icon {
  font-size: 64px;
  color: var(--error-color);
  margin-bottom: 20px;
}

.error-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.error-message {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  max-width: 400px;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 12px;
}
</style>
```

### 3. 空状态设计
```html
<!-- 空状态组件 -->
<div class="empty-state">
  <div class="empty-icon">
    <el-icon><DocumentRemove /></el-icon>
  </div>
  <div class="empty-content">
    <h4 class="empty-title">{{ emptyTitle }}</h4>
    <p class="empty-message">{{ emptyMessage }}</p>
    <div class="empty-actions">
      <el-button type="primary" @click="primaryAction">
        {{ primaryActionText }}
      </el-button>
    </div>
  </div>
</div>

<style>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 80px;
  color: var(--text-disabled);
  margin-bottom: 24px;
}

.empty-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.empty-message {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  margin: 0 0 32px 0;
  max-width: 400px;
  line-height: 1.6;
}
</style>
```

## 响应式设计

### 1. 断点定义
```css
/* 响应式断点 */
:root {
  --breakpoint-xs: 480px;
  --breakpoint-sm: 768px;
  --breakpoint-md: 992px;
  --breakpoint-lg: 1200px;
  --breakpoint-xl: 1600px;
}

/* 媒体查询混合器 */
@media (max-width: 479px) {
  /* 超小屏幕 */
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .metric-card {
    padding: 16px;
  }
  
  .metric-value {
    font-size: 24px;
  }
}

@media (min-width: 480px) and (max-width: 767px) {
  /* 小屏幕 */
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

@media (min-width: 768px) and (max-width: 991px) {
  /* 中等屏幕 */
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

@media (min-width: 992px) {
  /* 大屏幕 */
  .metrics-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
  }
}
```

### 2. 移动端优化
```css
/* 移动端表格优化 */
@media (max-width: 767px) {
  .el-table {
    font-size: var(--font-size-sm);
  }
  
  .el-table .cell {
    padding: 8px 4px;
  }
  
  /* 隐藏次要列 */
  .el-table-column--hidden-sm {
    display: none;
  }
  
  /* 表格横向滚动 */
  .table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}

/* 移动端表单优化 */
@media (max-width: 767px) {
  .el-form-item {
    margin-bottom: 16px;
  }
  
  .el-form-item__label {
    line-height: 1.4;
    padding-bottom: 4px;
  }
  
  .el-col {
    margin-bottom: 0;
  }
  
  /* 表单按钮全宽 */
  .form-actions .el-button {
    flex: 1;
  }
}
```

## 动画效果

### 1. 页面过渡动画
```css
/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滑动过渡 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}
```

### 2. 数据更新动画
```css
/* 数值变化动画 */
.metric-value {
  transition: all 0.3s ease;
}

.metric-value.updating {
  transform: scale(1.05);
  color: var(--primary-color);
}

/* 进度条动画 */
.progress-bar {
  position: relative;
  overflow: hidden;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}
```

## 可访问性设计

### 1. 键盘导航支持
```css
/* 焦点样式 */
.focusable:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* 跳过链接 */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary-color);
  color: white;
  padding: 8px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 1000;
}

.skip-link:focus {
  top: 6px;
}
```

### 2. 屏幕阅读器支持
```html
<!-- ARIA 标签示例 -->
<div 
  class="metric-card" 
  role="region" 
  aria-labelledby="total-return-title"
  aria-describedby="total-return-desc"
>
  <h4 id="total-return-title">总收益率</h4>
  <div class="metric-value" aria-live="polite">
    {{ formatPercent(result.totalReturn) }}
  </div>
  <div id="total-return-desc" class="sr-only">
    当前策略的总收益率为 {{ formatPercent(result.totalReturn) }}
  </div>
</div>

<style>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
```

## 设计交付要求

### 交付物清单
1. **设计稿**: Figma源文件，包含所有页面和组件
2. **组件库**: 可复用的UI组件设计规范
3. **交互原型**: 高保真交互原型
4. **设计规范**: 颜色、字体、间距、图标使用规范
5. **响应式设计**: 不同屏幕尺寸的适配方案
6. **切图资源**: 所需的图标和图片资源

### 设计验收标准
1. **视觉一致性**: 与现有DAOTrader风格保持一致
2. **交互流畅性**: 操作流程简洁高效
3. **响应式适配**: 在不同设备上显示正常
4. **可访问性**: 符合WCAG 2.1 AA标准
5. **性能优化**: 图片和动画不影响页面性能

### 开发对接
1. **组件命名**: 使用统一的命名规范
2. **样式变量**: 提供完整的CSS变量定义
3. **交互说明**: 详细的交互行为说明
4. **状态设计**: 各种状态下的界面表现
5. **边界情况**: 异常情况下的界面处理

**严格按照本提示词执行UI设计，确保界面专业美观、交互流畅、响应式适配完善。零自由度执行，所有设计必须符合量化交易平台的专业标准。**