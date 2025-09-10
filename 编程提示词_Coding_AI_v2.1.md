# DAOTrader v2.1 编程提示词 (Coding AI)

## 执行指令概述

你是DAOTrader v2.1的专业开发AI，负责实现AKShare数据接入与VNPY回测功能。严格按照本提示词执行，零自由度，确保代码质量和功能完整性。

## 项目结构要求

### 目录结构
```
DAOTrader/
├── backend/
│   ├── main.py                 # 现有FastAPI主程序
│   ├── requirements.txt        # 依赖包列表
│   ├── data_service/          # 新增：数据服务模块
│   │   ├── __init__.py
│   │   ├── akshare_client.py  # AKShare数据获取
│   │   ├── data_converter.py  # 数据格式转换
│   │   └── vnpy_database.py   # VNPY数据库操作
│   ├── backtest_service/      # 新增：回测服务模块
│   │   ├── __init__.py
│   │   ├── backtest_engine.py # 回测引擎封装
│   │   ├── strategy_manager.py # 策略管理
│   │   └── indicators.py      # 技术指标
│   └── models/                # 新增：数据模型
│       ├── __init__.py
│       ├── bar_data.py        # K线数据模型
│       └── backtest_result.py # 回测结果模型
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── KLineChart.vue     # 现有K线图组件
│   │   │   ├── DataManager.vue    # 新增：数据管理组件
│   │   │   ├── BacktestConfig.vue # 新增：回测配置组件
│   │   │   └── ResultDisplay.vue  # 新增：结果展示组件
│   │   ├── views/
│   │   │   ├── Dashboard.vue      # 现有仪表板
│   │   │   └── Backtest.vue       # 新增：回测页面
│   │   └── services/
│   │       └── api.ts             # API服务封装
└── data/                          # 新增：数据存储目录
    └── vnpy_data.db              # SQLite数据库文件
```

## 功能模块实现

### 1. 数据获取模块 (data_service/akshare_client.py)

**功能要求**:
- 封装AKShare API调用
- 支持股票、指数、期货数据获取
- 实现错误重试和异常处理
- 支持多时间频率数据

**核心代码结构**:
```python
import akshare as ak
import pandas as pd
from typing import Optional, List
from datetime import datetime, timedelta
import asyncio
import logging

class AKShareClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.retry_times = 3
        self.retry_delay = 1
    
    async def get_stock_data(self, symbol: str, period: str = "daily", 
                           start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取股票历史数据"""
        pass
    
    async def get_index_data(self, symbol: str, start_date: str = None, 
                           end_date: str = None) -> pd.DataFrame:
        """获取指数历史数据"""
        pass
    
    async def get_futures_data(self, symbol: str, start_date: str = None, 
                             end_date: str = None) -> pd.DataFrame:
        """获取期货历史数据"""
        pass
    
    def _retry_request(self, func, *args, **kwargs):
        """重试机制"""
        pass
```

### 2. 数据转换模块 (data_service/data_converter.py)

**功能要求**:
- 将AKShare DataFrame转换为VNPY BarData对象
- 处理时间格式标准化
- 数据清洗和验证
- 批量转换优化

**核心代码结构**:
```python
from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
import pandas as pd
from typing import List
from datetime import datetime

class DataConverter:
    def __init__(self):
        self.exchange_mapping = {
            'SH': Exchange.SSE,
            'SZ': Exchange.SZSE,
            'SHFE': Exchange.SHFE,
            'DCE': Exchange.DCE,
            'CZCE': Exchange.CZCE,
            'CFFEX': Exchange.CFFEX
        }
        
        self.interval_mapping = {
            'daily': Interval.DAILY,
            '60min': Interval.HOUR,
            '30min': Interval.MINUTE_30,
            '15min': Interval.MINUTE_15,
            '5min': Interval.MINUTE_5,
            '1min': Interval.MINUTE
        }
    
    def akshare_to_bardata(self, df: pd.DataFrame, symbol: str, 
                          exchange: str, interval: str) -> List[BarData]:
        """转换AKShare数据为VNPY BarData对象"""
        pass
    
    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据验证和清洗"""
        pass
    
    def normalize_datetime(self, dt_str: str) -> datetime:
        """标准化时间格式"""
        pass
```

### 3. 数据库操作模块 (data_service/vnpy_database.py)

**功能要求**:
- 使用VNPY数据库系统
- 实现数据存储和查询
- 支持增量更新
- 数据去重处理

**核心代码结构**:
```python
from vnpy.trader.database import get_database
from vnpy.trader.object import BarData
from typing import List, Optional
from datetime import datetime

class VNPYDatabase:
    def __init__(self):
        self.database = get_database()
    
    def save_bar_data(self, bars: List[BarData]) -> bool:
        """保存K线数据"""
        pass
    
    def load_bar_data(self, symbol: str, exchange: str, interval: str,
                     start: datetime, end: datetime) -> List[BarData]:
        """加载K线数据"""
        pass
    
    def get_data_range(self, symbol: str, exchange: str, interval: str) -> tuple:
        """获取数据时间范围"""
        pass
    
    def check_data_exists(self, symbol: str, exchange: str, interval: str,
                         start: datetime, end: datetime) -> bool:
        """检查数据是否存在"""
        pass
```

### 4. 回测引擎模块 (backtest_service/backtest_engine.py)

**功能要求**:
- 集成VNPY BacktestingEngine
- 封装回测流程
- 支持多策略回测
- 生成回测报告

**核心代码结构**:
```python
from vnpy.app.cta_backtester import BacktesterEngine
from vnpy.trader.object import BarData
from vnpy.app.cta_strategy import CtaTemplate
from typing import Dict, List, Any
from datetime import datetime

class BacktestManager:
    def __init__(self):
        self.engine = BacktesterEngine()
        self.results = {}
    
    def run_backtest(self, strategy_class: CtaTemplate, symbol: str, 
                    exchange: str, interval: str, start: datetime, 
                    end: datetime, rate: float, slippage: float, 
                    size: int, pricetick: float, capital: float,
                    setting: Dict[str, Any]) -> Dict[str, Any]:
        """执行回测"""
        pass
    
    def get_backtest_result(self) -> Dict[str, Any]:
        """获取回测结果"""
        pass
    
    def generate_report(self) -> Dict[str, Any]:
        """生成回测报告"""
        pass
```

### 5. 策略管理模块 (backtest_service/strategy_manager.py)

**功能要求**:
- 内置经典策略模板
- 支持自定义策略
- 策略参数管理
- 策略验证

**核心代码结构**:
```python
from vnpy.app.cta_strategy import CtaTemplate, StopOrder
from vnpy.trader.object import TickData, BarData
from typing import Dict, Any

class MovingAverageStrategy(CtaTemplate):
    """双均线策略示例"""
    
    author = "DAOTrader"
    
    # 策略参数
    fast_window = 10
    slow_window = 20
    
    # 策略变量
    fast_ma = 0.0
    slow_ma = 0.0
    
    parameters = ["fast_window", "slow_window"]
    variables = ["fast_ma", "slow_ma"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
    
    def on_init(self):
        """策略初始化"""
        pass
    
    def on_start(self):
        """策略启动"""
        pass
    
    def on_stop(self):
        """策略停止"""
        pass
    
    def on_bar(self, bar: BarData):
        """K线数据推送"""
        pass

class StrategyManager:
    def __init__(self):
        self.strategies = {
            "MovingAverage": MovingAverageStrategy,
            # 添加更多策略
        }
    
    def get_strategy_class(self, name: str) -> CtaTemplate:
        """获取策略类"""
        pass
    
    def validate_strategy_setting(self, strategy_name: str, setting: Dict[str, Any]) -> bool:
        """验证策略参数"""
        pass
```

### 6. FastAPI接口扩展 (backend/main.py)

**新增API接口**:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 数据模型
class DataDownloadRequest(BaseModel):
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: str

class BacktestRequest(BaseModel):
    strategy_name: str
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: str
    capital: float
    setting: dict

# API路由
@app.post("/api/data/download")
async def download_data(request: DataDownloadRequest):
    """下载历史数据"""
    pass

@app.get("/api/data/status/{symbol}")
async def get_data_status(symbol: str, exchange: str, interval: str):
    """获取数据状态"""
    pass

@app.post("/api/backtest/run")
async def run_backtest(request: BacktestRequest):
    """执行回测"""
    pass

@app.get("/api/backtest/result/{task_id}")
async def get_backtest_result(task_id: str):
    """获取回测结果"""
    pass

@app.get("/api/strategies")
async def get_strategies():
    """获取策略列表"""
    pass
```

### 7. 前端组件实现

#### 数据管理组件 (frontend/src/components/DataManager.vue)
```vue
<template>
  <div class="data-manager">
    <el-card>
      <template #header>
        <span>数据管理</span>
      </template>
      
      <!-- 数据下载表单 -->
      <el-form :model="downloadForm" label-width="100px">
        <el-form-item label="品种代码">
          <el-input v-model="downloadForm.symbol" placeholder="如：000001"></el-input>
        </el-form-item>
        <el-form-item label="交易所">
          <el-select v-model="downloadForm.exchange">
            <el-option label="上交所" value="SSE"></el-option>
            <el-option label="深交所" value="SZSE"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="时间周期">
          <el-select v-model="downloadForm.interval">
            <el-option label="日线" value="daily"></el-option>
            <el-option label="60分钟" value="60min"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="downloadData">下载数据</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 数据状态表格 -->
      <el-table :data="dataStatus" style="width: 100%">
        <el-table-column prop="symbol" label="品种"></el-table-column>
        <el-table-column prop="exchange" label="交易所"></el-table-column>
        <el-table-column prop="interval" label="周期"></el-table-column>
        <el-table-column prop="start_date" label="开始日期"></el-table-column>
        <el-table-column prop="end_date" label="结束日期"></el-table-column>
        <el-table-column prop="count" label="数据量"></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { downloadHistoryData, getDataStatus } from '../services/api'

// 组件逻辑实现
const downloadForm = ref({
  symbol: '',
  exchange: 'SSE',
  interval: 'daily',
  start_date: '',
  end_date: ''
})

const dataStatus = ref([])

const downloadData = async () => {
  // 实现数据下载逻辑
}

const loadDataStatus = async () => {
  // 实现数据状态加载
}

onMounted(() => {
  loadDataStatus()
})
</script>
```

#### 回测配置组件 (frontend/src/components/BacktestConfig.vue)
```vue
<template>
  <div class="backtest-config">
    <el-card>
      <template #header>
        <span>回测配置</span>
      </template>
      
      <el-form :model="backtestForm" label-width="120px">
        <el-form-item label="策略选择">
          <el-select v-model="backtestForm.strategy_name">
            <el-option 
              v-for="strategy in strategies" 
              :key="strategy.name"
              :label="strategy.label" 
              :value="strategy.name">
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="交易品种">
          <el-input v-model="backtestForm.symbol"></el-input>
        </el-form-item>
        
        <el-form-item label="回测时间">
          <el-date-picker
            v-model="backtestForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="初始资金">
          <el-input-number v-model="backtestForm.capital" :min="10000"></el-input-number>
        </el-form-item>
        
        <!-- 策略参数动态表单 -->
        <div v-if="strategyParams.length > 0">
          <h4>策略参数</h4>
          <el-form-item 
            v-for="param in strategyParams" 
            :key="param.name"
            :label="param.label">
            <el-input-number 
              v-model="backtestForm.setting[param.name]"
              :min="param.min"
              :max="param.max"
              :step="param.step">
            </el-input-number>
          </el-form-item>
        </div>
        
        <el-form-item>
          <el-button type="primary" @click="runBacktest" :loading="isRunning">
            {{ isRunning ? '回测中...' : '开始回测' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑实现
</script>
```

## 接口定义

### RESTful API接口

```typescript
// 数据管理接口
POST /api/data/download
{
  "symbol": "000001",
  "exchange": "SSE",
  "interval": "daily",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}

GET /api/data/status/{symbol}?exchange=SSE&interval=daily
{
  "symbol": "000001",
  "exchange": "SSE",
  "interval": "daily",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "count": 244,
  "last_update": "2024-01-01T00:00:00"
}

// 回测接口
POST /api/backtest/run
{
  "strategy_name": "MovingAverage",
  "symbol": "000001",
  "exchange": "SSE",
  "interval": "daily",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "capital": 100000,
  "setting": {
    "fast_window": 10,
    "slow_window": 20
  }
}

GET /api/backtest/result/{task_id}
{
  "task_id": "uuid",
  "status": "completed",
  "result": {
    "total_return": 0.15,
    "sharpe_ratio": 1.2,
    "max_drawdown": 0.08,
    "trades": [...],
    "daily_returns": [...]
  }
}
```

## 数据库设计

### 数据表结构
```sql
-- VNPY内置表结构（自动创建）
CREATE TABLE dbbardata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    datetime DATETIME NOT NULL,
    interval VARCHAR(20) NOT NULL,
    volume REAL,
    turnover REAL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    UNIQUE(symbol, exchange, datetime, interval)
);

-- 自定义回测结果表
CREATE TABLE backtest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(50) UNIQUE,
    strategy_name VARCHAR(100),
    symbol VARCHAR(50),
    exchange VARCHAR(20),
    interval VARCHAR(20),
    start_date DATE,
    end_date DATE,
    capital REAL,
    setting TEXT,  -- JSON格式策略参数
    total_return REAL,
    sharpe_ratio REAL,
    max_drawdown REAL,
    total_trades INTEGER,
    win_rate REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running'
);

-- 交易记录表
CREATE TABLE trade_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(50),
    datetime DATETIME,
    symbol VARCHAR(50),
    direction VARCHAR(10),  -- LONG/SHORT
    offset VARCHAR(10),     -- OPEN/CLOSE
    price REAL,
    volume INTEGER,
    commission REAL,
    slippage REAL,
    FOREIGN KEY (task_id) REFERENCES backtest_results(task_id)
);
```

## 交互要求

### 异常情况处理
1. **网络异常**: 实现重试机制，最多重试3次
2. **数据异常**: 记录异常日志，跳过异常数据
3. **API限制**: 实现请求频率控制
4. **内存不足**: 分批处理大数据集
5. **数据库异常**: 事务回滚，保证数据一致性

### 用户操作流程
1. **数据准备**: 用户选择品种和时间范围下载数据
2. **策略配置**: 选择策略并设置参数
3. **回测执行**: 提交回测任务，显示进度
4. **结果查看**: 展示回测结果和分析报告
5. **参数优化**: 支持批量参数测试

## 部署方案

### 开发环境部署
```bash
# 1. 安装Python依赖
cd backend
pip install -r requirements.txt

# 2. 安装前端依赖
cd ../frontend
npm install

# 3. 启动后端服务
cd ../backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 4. 启动前端服务
cd ../frontend
npm run dev
```

### 生产环境部署
```dockerfile
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///app/data/vnpy_data.db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
```

### 环境变量说明
```bash
# .env文件
DATABASE_URL=sqlite:///./data/vnpy_data.db
AKSHARE_TIMEOUT=30
BACKTEST_MAX_WORKERS=4
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379  # 可选
```

### 启动命令
```bash
# 开发环境
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
npm run dev

# 生产环境
docker-compose up -d
```

## 代码质量要求

### 编码规范
1. **Python**: 遵循PEP 8规范，使用Black格式化
2. **TypeScript**: 遵循ESLint规则，使用Prettier格式化
3. **注释**: 关键函数必须有docstring
4. **类型提示**: Python和TypeScript都要求类型注解

### 错误处理
1. **异常捕获**: 所有外部调用都要有异常处理
2. **日志记录**: 使用结构化日志，记录关键操作
3. **用户友好**: 向用户展示友好的错误信息
4. **数据验证**: 输入参数严格验证

### 性能优化
1. **异步处理**: 使用async/await处理IO操作
2. **批量操作**: 数据库操作尽量批量处理
3. **缓存机制**: 热点数据使用缓存
4. **分页加载**: 大数据集分页展示

---

## 执行检查清单

### 后端开发检查
- [ ] AKShare客户端实现完成
- [ ] 数据转换模块测试通过
- [ ] VNPY数据库集成正常
- [ ] 回测引擎封装完成
- [ ] 策略管理模块实现
- [ ] FastAPI接口全部实现
- [ ] 异常处理机制完善
- [ ] 日志系统配置完成

### 前端开发检查
- [ ] 数据管理组件完成
- [ ] 回测配置组件完成
- [ ] 结果展示组件完成
- [ ] API服务封装完成
- [ ] 路由配置正确
- [ ] 响应式设计适配
- [ ] 错误处理完善
- [ ] 用户体验优化

### 集成测试检查
- [ ] 数据下载流程测试
- [ ] 数据转换准确性验证
- [ ] 回测功能端到端测试
- [ ] 前后端接口联调
- [ ] 异常场景测试
- [ ] 性能压力测试
- [ ] 部署脚本验证
- [ ] 文档完整性检查

**严格按照本提示词执行，确保每个功能模块都完整实现，代码质量达到生产标准。零自由度执行，不允许简化或省略任何功能。**