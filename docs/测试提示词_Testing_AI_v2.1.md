# DAOTrader v2.1 测试提示词 (Testing AI)

## 执行指令概述

你是DAOTrader v2.1的专业测试AI，负责对AKShare数据接入与VNPY回测功能进行全面测试。严格按照本提示词执行，零自由度，确保测试覆盖率和质量标准。

## 测试环境准备

### 测试数据准备
```python
# 测试用股票代码
TEST_STOCKS = [
    {"symbol": "000001", "exchange": "SZSE", "name": "平安银行"},
    {"symbol": "000002", "exchange": "SZSE", "name": "万科A"},
    {"symbol": "600000", "exchange": "SSE", "name": "浦发银行"},
    {"symbol": "600036", "exchange": "SSE", "name": "招商银行"}
]

# 测试时间范围
TEST_DATE_RANGES = [
    {"start": "2023-01-01", "end": "2023-03-31", "desc": "短期测试"},
    {"start": "2023-01-01", "end": "2023-12-31", "desc": "年度测试"},
    {"start": "2020-01-01", "end": "2023-12-31", "desc": "长期测试"}
]

# 测试时间周期
TEST_INTERVALS = ["daily", "60min", "30min", "15min", "5min"]
```

### 测试环境配置
```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov requests-mock
npm install --save-dev @vue/test-utils vitest jsdom

# 创建测试数据库
cp data/vnpy_data.db data/test_vnpy_data.db

# 设置测试环境变量
export TESTING=true
export DATABASE_URL=sqlite:///./data/test_vnpy_data.db
```

## 功能测试

### 1. 数据获取模块测试

#### 1.1 AKShare客户端测试
```python
# tests/test_akshare_client.py
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from backend.data_service.akshare_client import AKShareClient

class TestAKShareClient:
    @pytest.fixture
    def client(self):
        return AKShareClient()
    
    @pytest.mark.asyncio
    async def test_get_stock_data_success(self, client):
        """测试股票数据获取成功"""
        # 模拟AKShare返回数据
        mock_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'open': [10.0, 10.5],
            'high': [10.2, 10.8],
            'low': [9.8, 10.3],
            'close': [10.1, 10.6],
            'volume': [1000000, 1200000]
        })
        
        with patch('akshare.stock_zh_a_hist', return_value=mock_data):
            result = await client.get_stock_data("000001", "daily", "2023-01-01", "2023-01-02")
            
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'date' in result.columns
        assert 'close' in result.columns
    
    @pytest.mark.asyncio
    async def test_get_stock_data_network_error(self, client):
        """测试网络错误重试机制"""
        with patch('akshare.stock_zh_a_hist', side_effect=Exception("Network Error")):
            with pytest.raises(Exception):
                await client.get_stock_data("000001", "daily", "2023-01-01", "2023-01-02")
    
    @pytest.mark.asyncio
    async def test_get_stock_data_invalid_symbol(self, client):
        """测试无效股票代码"""
        with patch('akshare.stock_zh_a_hist', return_value=pd.DataFrame()):
            result = await client.get_stock_data("INVALID", "daily", "2023-01-01", "2023-01-02")
            assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_index_data(self, client):
        """测试指数数据获取"""
        mock_data = pd.DataFrame({
            'date': ['2023-01-01'],
            'open': [3000.0],
            'high': [3100.0],
            'low': [2950.0],
            'close': [3050.0],
            'volume': [50000000]
        })
        
        with patch('akshare.index_zh_a_hist', return_value=mock_data):
            result = await client.get_index_data("000001", "2023-01-01", "2023-01-01")
            
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
```

#### 1.2 数据转换模块测试
```python
# tests/test_data_converter.py
import pytest
import pandas as pd
from datetime import datetime
from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from backend.data_service.data_converter import DataConverter

class TestDataConverter:
    @pytest.fixture
    def converter(self):
        return DataConverter()
    
    @pytest.fixture
    def sample_akshare_data(self):
        return pd.DataFrame({
            '日期': ['2023-01-01', '2023-01-02'],
            '开盘': [10.0, 10.5],
            '最高': [10.2, 10.8],
            '最低': [9.8, 10.3],
            '收盘': [10.1, 10.6],
            '成交量': [1000000, 1200000],
            '成交额': [10100000, 12720000]
        })
    
    def test_akshare_to_bardata_conversion(self, converter, sample_akshare_data):
        """测试AKShare数据转换为BarData"""
        bars = converter.akshare_to_bardata(
            sample_akshare_data, "000001", "SZSE", "daily"
        )
        
        assert len(bars) == 2
        assert all(isinstance(bar, BarData) for bar in bars)
        
        first_bar = bars[0]
        assert first_bar.symbol == "000001"
        assert first_bar.exchange == Exchange.SZSE
        assert first_bar.interval == Interval.DAILY
        assert first_bar.open_price == 10.0
        assert first_bar.high_price == 10.2
        assert first_bar.low_price == 9.8
        assert first_bar.close_price == 10.1
        assert first_bar.volume == 1000000
    
    def test_validate_data_normal(self, converter, sample_akshare_data):
        """测试正常数据验证"""
        validated_data = converter.validate_data(sample_akshare_data)
        assert len(validated_data) == 2
    
    def test_validate_data_with_nulls(self, converter):
        """测试包含空值的数据验证"""
        data_with_nulls = pd.DataFrame({
            '日期': ['2023-01-01', '2023-01-02', '2023-01-03'],
            '开盘': [10.0, None, 10.5],
            '最高': [10.2, 10.8, None],
            '最低': [9.8, 10.3, 10.2],
            '收盘': [10.1, 10.6, 10.4],
            '成交量': [1000000, 1200000, 1100000]
        })
        
        validated_data = converter.validate_data(data_with_nulls)
        # 应该过滤掉包含空值的行
        assert len(validated_data) == 1
    
    def test_normalize_datetime(self, converter):
        """测试时间格式标准化"""
        test_cases = [
            "2023-01-01",
            "2023-01-01 09:30:00",
            "20230101"
        ]
        
        for dt_str in test_cases:
            result = converter.normalize_datetime(dt_str)
            assert isinstance(result, datetime)
```

#### 1.3 数据库操作测试
```python
# tests/test_vnpy_database.py
import pytest
from datetime import datetime
from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from backend.data_service.vnpy_database import VNPYDatabase

class TestVNPYDatabase:
    @pytest.fixture
    def database(self):
        return VNPYDatabase()
    
    @pytest.fixture
    def sample_bars(self):
        bars = []
        for i in range(5):
            bar = BarData(
                symbol="000001",
                exchange=Exchange.SZSE,
                datetime=datetime(2023, 1, i+1, 9, 30),
                interval=Interval.DAILY,
                volume=1000000 + i * 100000,
                turnover=10000000 + i * 1000000,
                open_price=10.0 + i * 0.1,
                high_price=10.2 + i * 0.1,
                low_price=9.8 + i * 0.1,
                close_price=10.1 + i * 0.1,
                gateway_name="test"
            )
            bars.append(bar)
        return bars
    
    def test_save_bar_data(self, database, sample_bars):
        """测试保存K线数据"""
        result = database.save_bar_data(sample_bars)
        assert result is True
    
    def test_load_bar_data(self, database, sample_bars):
        """测试加载K线数据"""
        # 先保存数据
        database.save_bar_data(sample_bars)
        
        # 加载数据
        loaded_bars = database.load_bar_data(
            "000001", Exchange.SZSE, Interval.DAILY,
            datetime(2023, 1, 1), datetime(2023, 1, 5)
        )
        
        assert len(loaded_bars) == 5
        assert all(isinstance(bar, BarData) for bar in loaded_bars)
    
    def test_get_data_range(self, database, sample_bars):
        """测试获取数据时间范围"""
        database.save_bar_data(sample_bars)
        
        start, end = database.get_data_range(
            "000001", Exchange.SZSE, Interval.DAILY
        )
        
        assert start == datetime(2023, 1, 1, 9, 30)
        assert end == datetime(2023, 1, 5, 9, 30)
    
    def test_check_data_exists(self, database, sample_bars):
        """测试检查数据是否存在"""
        database.save_bar_data(sample_bars)
        
        exists = database.check_data_exists(
            "000001", Exchange.SZSE, Interval.DAILY,
            datetime(2023, 1, 1), datetime(2023, 1, 3)
        )
        
        assert exists is True
        
        not_exists = database.check_data_exists(
            "000002", Exchange.SZSE, Interval.DAILY,
            datetime(2023, 1, 1), datetime(2023, 1, 3)
        )
        
        assert not_exists is False
```

### 2. 回测引擎测试

#### 2.1 回测管理器测试
```python
# tests/test_backtest_engine.py
import pytest
from datetime import datetime
from backend.backtest_service.backtest_engine import BacktestManager
from backend.backtest_service.strategy_manager import MovingAverageStrategy

class TestBacktestManager:
    @pytest.fixture
    def backtest_manager(self):
        return BacktestManager()
    
    def test_run_backtest_success(self, backtest_manager):
        """测试回测执行成功"""
        result = backtest_manager.run_backtest(
            strategy_class=MovingAverageStrategy,
            symbol="000001",
            exchange="SZSE",
            interval="daily",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 12, 31),
            rate=0.0003,
            slippage=0.01,
            size=100,
            pricetick=0.01,
            capital=100000,
            setting={"fast_window": 10, "slow_window": 20}
        )
        
        assert isinstance(result, dict)
        assert "total_return" in result
        assert "sharpe_ratio" in result
        assert "max_drawdown" in result
    
    def test_run_backtest_no_data(self, backtest_manager):
        """测试无数据情况下的回测"""
        with pytest.raises(Exception):
            backtest_manager.run_backtest(
                strategy_class=MovingAverageStrategy,
                symbol="INVALID",
                exchange="SZSE",
                interval="daily",
                start=datetime(2023, 1, 1),
                end=datetime(2023, 12, 31),
                rate=0.0003,
                slippage=0.01,
                size=100,
                pricetick=0.01,
                capital=100000,
                setting={"fast_window": 10, "slow_window": 20}
            )
    
    def test_generate_report(self, backtest_manager):
        """测试生成回测报告"""
        # 先运行一个回测
        backtest_manager.run_backtest(
            strategy_class=MovingAverageStrategy,
            symbol="000001",
            exchange="SZSE",
            interval="daily",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 3, 31),
            rate=0.0003,
            slippage=0.01,
            size=100,
            pricetick=0.01,
            capital=100000,
            setting={"fast_window": 5, "slow_window": 10}
        )
        
        report = backtest_manager.generate_report()
        
        assert isinstance(report, dict)
        assert "statistics" in report
        assert "trades" in report
        assert "daily_returns" in report
```

#### 2.2 策略管理器测试
```python
# tests/test_strategy_manager.py
import pytest
from backend.backtest_service.strategy_manager import StrategyManager, MovingAverageStrategy

class TestStrategyManager:
    @pytest.fixture
    def strategy_manager(self):
        return StrategyManager()
    
    def test_get_strategy_class(self, strategy_manager):
        """测试获取策略类"""
        strategy_class = strategy_manager.get_strategy_class("MovingAverage")
        assert strategy_class == MovingAverageStrategy
    
    def test_get_invalid_strategy_class(self, strategy_manager):
        """测试获取无效策略类"""
        with pytest.raises(KeyError):
            strategy_manager.get_strategy_class("InvalidStrategy")
    
    def test_validate_strategy_setting_valid(self, strategy_manager):
        """测试有效策略参数验证"""
        setting = {"fast_window": 10, "slow_window": 20}
        result = strategy_manager.validate_strategy_setting("MovingAverage", setting)
        assert result is True
    
    def test_validate_strategy_setting_invalid(self, strategy_manager):
        """测试无效策略参数验证"""
        setting = {"fast_window": 20, "slow_window": 10}  # fast > slow
        result = strategy_manager.validate_strategy_setting("MovingAverage", setting)
        assert result is False
```

### 3. API接口测试

#### 3.1 数据接口测试
```python
# tests/test_api_data.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestDataAPI:
    def test_download_data_success(self):
        """测试数据下载成功"""
        response = client.post("/api/data/download", json={
            "symbol": "000001",
            "exchange": "SZSE",
            "interval": "daily",
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "success"
    
    def test_download_data_invalid_symbol(self):
        """测试无效股票代码"""
        response = client.post("/api/data/download", json={
            "symbol": "",
            "exchange": "SZSE",
            "interval": "daily",
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        })
        
        assert response.status_code == 422
    
    def test_get_data_status(self):
        """测试获取数据状态"""
        response = client.get("/api/data/status/000001?exchange=SZSE&interval=daily")
        
        assert response.status_code == 200
        data = response.json()
        assert "symbol" in data
        assert "count" in data
    
    def test_get_data_status_not_found(self):
        """测试获取不存在数据的状态"""
        response = client.get("/api/data/status/NOTFOUND?exchange=SZSE&interval=daily")
        
        assert response.status_code == 404
```

#### 3.2 回测接口测试
```python
# tests/test_api_backtest.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestBacktestAPI:
    def test_run_backtest_success(self):
        """测试回测执行成功"""
        response = client.post("/api/backtest/run", json={
            "strategy_name": "MovingAverage",
            "symbol": "000001",
            "exchange": "SZSE",
            "interval": "daily",
            "start_date": "2023-01-01",
            "end_date": "2023-03-31",
            "capital": 100000,
            "setting": {
                "fast_window": 10,
                "slow_window": 20
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "running"
    
    def test_run_backtest_invalid_strategy(self):
        """测试无效策略名称"""
        response = client.post("/api/backtest/run", json={
            "strategy_name": "InvalidStrategy",
            "symbol": "000001",
            "exchange": "SZSE",
            "interval": "daily",
            "start_date": "2023-01-01",
            "end_date": "2023-03-31",
            "capital": 100000,
            "setting": {}
        })
        
        assert response.status_code == 400
    
    def test_get_backtest_result(self):
        """测试获取回测结果"""
        # 先运行回测
        run_response = client.post("/api/backtest/run", json={
            "strategy_name": "MovingAverage",
            "symbol": "000001",
            "exchange": "SZSE",
            "interval": "daily",
            "start_date": "2023-01-01",
            "end_date": "2023-03-31",
            "capital": 100000,
            "setting": {"fast_window": 10, "slow_window": 20}
        })
        
        task_id = run_response.json()["task_id"]
        
        # 获取结果
        result_response = client.get(f"/api/backtest/result/{task_id}")
        
        assert result_response.status_code == 200
        data = result_response.json()
        assert "task_id" in data
        assert "result" in data
    
    def test_get_strategies(self):
        """测试获取策略列表"""
        response = client.get("/api/strategies")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "MovingAverage" in [s["name"] for s in data]
```

## 边界条件测试

### 1. 数据边界测试
```python
# tests/test_boundary_conditions.py
import pytest
import pandas as pd
from datetime import datetime, timedelta
from backend.data_service.akshare_client import AKShareClient
from backend.data_service.data_converter import DataConverter

class TestBoundaryConditions:
    @pytest.fixture
    def client(self):
        return AKShareClient()
    
    @pytest.fixture
    def converter(self):
        return DataConverter()
    
    @pytest.mark.asyncio
    async def test_large_date_range(self, client):
        """测试大时间范围数据获取"""
        # 测试5年数据
        start_date = "2019-01-01"
        end_date = "2023-12-31"
        
        result = await client.get_stock_data("000001", "daily", start_date, end_date)
        
        # 验证数据量合理（约1200个交易日）
        assert len(result) > 1000
        assert len(result) < 1500
    
    def test_empty_dataframe_conversion(self, converter):
        """测试空DataFrame转换"""
        empty_df = pd.DataFrame()
        
        bars = converter.akshare_to_bardata(empty_df, "000001", "SZSE", "daily")
        
        assert len(bars) == 0
    
    def test_single_row_dataframe(self, converter):
        """测试单行数据转换"""
        single_row_df = pd.DataFrame({
            '日期': ['2023-01-01'],
            '开盘': [10.0],
            '最高': [10.2],
            '最低': [9.8],
            '收盘': [10.1],
            '成交量': [1000000],
            '成交额': [10100000]
        })
        
        bars = converter.akshare_to_bardata(single_row_df, "000001", "SZSE", "daily")
        
        assert len(bars) == 1
        assert bars[0].close_price == 10.1
    
    def test_extreme_price_values(self, converter):
        """测试极端价格值"""
        extreme_df = pd.DataFrame({
            '日期': ['2023-01-01', '2023-01-02'],
            '开盘': [0.01, 9999.99],  # 极小和极大值
            '最高': [0.02, 10000.0],
            '最低': [0.01, 9999.0],
            '收盘': [0.015, 9999.5],
            '成交量': [1, 999999999],  # 极小和极大成交量
            '成交额': [0.015, 99999999999]
        })
        
        bars = converter.akshare_to_bardata(extreme_df, "000001", "SZSE", "daily")
        
        assert len(bars) == 2
        assert bars[0].close_price == 0.015
        assert bars[1].close_price == 9999.5
    
    @pytest.mark.asyncio
    async def test_weekend_date_range(self, client):
        """测试包含周末的日期范围"""
        # 选择一个包含周末的日期范围
        start_date = "2023-01-07"  # 周六
        end_date = "2023-01-08"    # 周日
        
        result = await client.get_stock_data("000001", "daily", start_date, end_date)
        
        # 周末应该没有交易数据
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_holiday_date_range(self, client):
        """测试节假日期间数据获取"""
        # 春节期间
        start_date = "2023-01-21"  # 春节前
        end_date = "2023-01-28"    # 春节后
        
        result = await client.get_stock_data("000001", "daily", start_date, end_date)
        
        # 节假日期间交易日较少
        assert len(result) <= 3
```

### 2. 性能边界测试
```python
# tests/test_performance.py
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from backend.data_service.akshare_client import AKShareClient
from backend.backtest_service.backtest_engine import BacktestManager

class TestPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_data_requests(self):
        """测试并发数据请求"""
        client = AKShareClient()
        symbols = ["000001", "000002", "600000", "600036"]
        
        start_time = time.time()
        
        tasks = []
        for symbol in symbols:
            task = client.get_stock_data(symbol, "daily", "2023-01-01", "2023-01-31")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 并发请求应该比串行快
        assert duration < 30  # 30秒内完成
        assert all(len(result) > 0 for result in results)
    
    def test_large_dataset_backtest(self):
        """测试大数据集回测性能"""
        backtest_manager = BacktestManager()
        
        start_time = time.time()
        
        result = backtest_manager.run_backtest(
            strategy_class=MovingAverageStrategy,
            symbol="000001",
            exchange="SZSE",
            interval="daily",
            start=datetime(2020, 1, 1),  # 4年数据
            end=datetime(2023, 12, 31),
            rate=0.0003,
            slippage=0.01,
            size=100,
            pricetick=0.01,
            capital=100000,
            setting={"fast_window": 10, "slow_window": 20}
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 4年数据回测应在合理时间内完成
        assert duration < 60  # 60秒内完成
        assert isinstance(result, dict)
    
    def test_memory_usage_large_dataset(self):
        """测试大数据集内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 加载大量数据
        database = VNPYDatabase()
        bars = database.load_bar_data(
            "000001", Exchange.SZSE, Interval.DAILY,
            datetime(2020, 1, 1), datetime(2023, 12, 31)
        )
        
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        
        # 内存增长应在合理范围内（小于500MB）
        assert memory_increase < 500 * 1024 * 1024
        assert len(bars) > 0
```

## 回归测试

### 1. 核心功能回归测试
```python
# tests/test_regression.py
import pytest
from datetime import datetime
from backend.data_service.akshare_client import AKShareClient
from backend.data_service.data_converter import DataConverter
from backend.data_service.vnpy_database import VNPYDatabase
from backend.backtest_service.backtest_engine import BacktestManager
from backend.backtest_service.strategy_manager import MovingAverageStrategy

class TestRegression:
    """回归测试确保核心功能稳定"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_data_flow(self):
        """测试端到端数据流程"""
        # 1. 获取数据
        client = AKShareClient()
        df = await client.get_stock_data("000001", "daily", "2023-01-01", "2023-01-31")
        assert len(df) > 0
        
        # 2. 转换数据
        converter = DataConverter()
        bars = converter.akshare_to_bardata(df, "000001", "SZSE", "daily")
        assert len(bars) > 0
        
        # 3. 存储数据
        database = VNPYDatabase()
        result = database.save_bar_data(bars)
        assert result is True
        
        # 4. 加载数据
        loaded_bars = database.load_bar_data(
            "000001", Exchange.SZSE, Interval.DAILY,
            datetime(2023, 1, 1), datetime(2023, 1, 31)
        )
        assert len(loaded_bars) == len(bars)
        
        # 5. 执行回测
        backtest_manager = BacktestManager()
        backtest_result = backtest_manager.run_backtest(
            strategy_class=MovingAverageStrategy,
            symbol="000001",
            exchange="SZSE",
            interval="daily",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 1, 31),
            rate=0.0003,
            slippage=0.01,
            size=100,
            pricetick=0.01,
            capital=100000,
            setting={"fast_window": 5, "slow_window": 10}
        )
        assert isinstance(backtest_result, dict)
        assert "total_return" in backtest_result
    
    def test_strategy_consistency(self):
        """测试策略结果一致性"""
        backtest_manager = BacktestManager()
        
        # 运行相同参数的回测两次
        result1 = backtest_manager.run_backtest(
            strategy_class=MovingAverageStrategy,
            symbol="000001",
            exchange="SZSE",
            interval="daily",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 3, 31),
            rate=0.0003,
            slippage=0.01,
            size=100,
            pricetick=0.01,
            capital=100000,
            setting={"fast_window": 10, "slow_window": 20}
        )
        
        result2 = backtest_manager.run_backtest(
            strategy_class=MovingAverageStrategy,
            symbol="000001",
            exchange="SZSE",
            interval="daily",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 3, 31),
            rate=0.0003,
            slippage=0.01,
            size=100,
            pricetick=0.01,
            capital=100000,
            setting={"fast_window": 10, "slow_window": 20}
        )
        
        # 结果应该完全一致
        assert result1["total_return"] == result2["total_return"]
        assert result1["sharpe_ratio"] == result2["sharpe_ratio"]
        assert result1["max_drawdown"] == result2["max_drawdown"]
```

## 前端测试

### 1. 组件单元测试
```javascript
// tests/frontend/DataManager.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import DataManager from '@/components/DataManager.vue'
import { ElButton, ElForm, ElInput } from 'element-plus'

describe('DataManager', () => {
  it('renders properly', () => {
    const wrapper = mount(DataManager, {
      global: {
        components: {
          ElButton,
          ElForm,
          ElInput
        }
      }
    })
    
    expect(wrapper.find('.data-manager').exists()).toBe(true)
    expect(wrapper.find('el-form').exists()).toBe(true)
  })
  
  it('validates form input', async () => {
    const wrapper = mount(DataManager)
    
    // 测试空输入验证
    const symbolInput = wrapper.find('input[placeholder="如：000001"]')
    await symbolInput.setValue('')
    
    const downloadButton = wrapper.find('el-button')
    await downloadButton.trigger('click')
    
    // 应该显示验证错误
    expect(wrapper.find('.el-form-item__error').exists()).toBe(true)
  })
  
  it('calls download API on form submit', async () => {
    const mockDownload = vi.fn()
    vi.mock('@/services/api', () => ({
      downloadHistoryData: mockDownload
    }))
    
    const wrapper = mount(DataManager)
    
    // 填写表单
    await wrapper.find('input[placeholder="如：000001"]').setValue('000001')
    
    // 提交表单
    await wrapper.find('el-button').trigger('click')
    
    expect(mockDownload).toHaveBeenCalledWith({
      symbol: '000001',
      exchange: 'SSE',
      interval: 'daily',
      start_date: '',
      end_date: ''
    })
  })
})
```

```javascript
// tests/frontend/BacktestConfig.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import BacktestConfig from '@/components/BacktestConfig.vue'

describe('BacktestConfig', () => {
  it('loads strategies on mount', async () => {
    const mockStrategies = [
      { name: 'MovingAverage', label: '双均线策略' },
      { name: 'RSI', label: 'RSI策略' }
    ]
    
    vi.mock('@/services/api', () => ({
      getStrategies: () => Promise.resolve(mockStrategies)
    }))
    
    const wrapper = mount(BacktestConfig)
    
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.strategies).toEqual(mockStrategies)
  })
  
  it('updates strategy parameters when strategy changes', async () => {
    const wrapper = mount(BacktestConfig)
    
    // 选择策略
    await wrapper.find('el-select').setValue('MovingAverage')
    
    // 应该显示策略参数
    expect(wrapper.find('h4').text()).toBe('策略参数')
    expect(wrapper.findAll('el-input-number').length).toBeGreaterThan(0)
  })
  
  it('submits backtest with correct parameters', async () => {
    const mockRunBacktest = vi.fn()
    vi.mock('@/services/api', () => ({
      runBacktest: mockRunBacktest
    }))
    
    const wrapper = mount(BacktestConfig)
    
    // 填写表单
    await wrapper.find('el-select').setValue('MovingAverage')
    await wrapper.find('input[placeholder="品种代码"]').setValue('000001')
    
    // 提交回测
    await wrapper.find('el-button[type="primary"]').trigger('click')
    
    expect(mockRunBacktest).toHaveBeenCalled()
  })
})
```

### 2. 集成测试
```javascript
// tests/frontend/integration.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'
import App from '@/App.vue'
import Backtest from '@/views/Backtest.vue'

describe('Integration Tests', () => {
  it('navigates to backtest page', async () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/backtest', component: Backtest }
      ]
    })
    
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })
    
    await router.push('/backtest')
    await wrapper.vm.$nextTick()
    
    expect(wrapper.findComponent(Backtest).exists()).toBe(true)
  })
  
  it('completes full backtest workflow', async () => {
    // 模拟API响应
    const mockAPI = {
      downloadHistoryData: vi.fn().mockResolvedValue({ task_id: 'test-123' }),
      getStrategies: vi.fn().mockResolvedValue([{ name: 'MovingAverage', label: '双均线策略' }]),
      runBacktest: vi.fn().mockResolvedValue({ task_id: 'backtest-456' }),
      getBacktestResult: vi.fn().mockResolvedValue({
        status: 'completed',
        result: { total_return: 0.15, sharpe_ratio: 1.2 }
      })
    }
    
    vi.mock('@/services/api', () => mockAPI)
    
    const wrapper = mount(Backtest)
    
    // 1. 下载数据
    await wrapper.find('[data-test="download-data"]').trigger('click')
    expect(mockAPI.downloadHistoryData).toHaveBeenCalled()
    
    // 2. 配置回测
    await wrapper.find('[data-test="run-backtest"]').trigger('click')
    expect(mockAPI.runBacktest).toHaveBeenCalled()
    
    // 3. 查看结果
    await wrapper.vm.$nextTick()
    expect(mockAPI.getBacktestResult).toHaveBeenCalled()
  })
})
```

## 测试执行和报告

### 1. 测试执行脚本
```bash
#!/bin/bash
# run_tests.sh

echo "开始执行DAOTrader v2.1测试套件..."

# 后端测试
echo "执行后端测试..."
cd backend
python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

if [ $? -ne 0 ]; then
    echo "后端测试失败！"
    exit 1
fi

# 前端测试
echo "执行前端测试..."
cd ../frontend
npm run test:coverage

if [ $? -ne 0 ]; then
    echo "前端测试失败！"
    exit 1
fi

# 集成测试
echo "执行集成测试..."
cd ..
python -m pytest tests/integration/ -v

if [ $? -ne 0 ]; then
    echo "集成测试失败！"
    exit 1
fi

echo "所有测试通过！"
```

### 2. 测试报告生成
```python
# generate_test_report.py
import json
import datetime
from pathlib import Path

def generate_test_report():
    """生成测试报告"""
    report = {
        "project": "DAOTrader v2.1",
        "test_date": datetime.datetime.now().isoformat(),
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "coverage": 0
        },
        "modules": {
            "data_service": {"tests": 0, "passed": 0, "coverage": 0},
            "backtest_service": {"tests": 0, "passed": 0, "coverage": 0},
            "api": {"tests": 0, "passed": 0, "coverage": 0},
            "frontend": {"tests": 0, "passed": 0, "coverage": 0}
        },
        "performance": {
            "data_download_avg_time": 0,
            "backtest_avg_time": 0,
            "memory_usage_peak": 0
        },
        "issues": []
    }
    
    # 读取测试结果文件
    # 解析覆盖率报告
    # 生成HTML报告
    
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("测试报告已生成：test_report.json")

if __name__ == "__main__":
    generate_test_report()
```

## 测试交付要求

### 测试完成标准
1. **代码覆盖率**: 后端 ≥ 90%，前端 ≥ 85%
2. **测试通过率**: 100%
3. **性能测试**: 所有性能指标达标
4. **文档完整**: 测试报告、缺陷列表、测试用例文档

### 测试交付物
1. **测试报告**: 包含测试结果、覆盖率、性能数据
2. **缺陷列表**: 发现的问题及修复状态
3. **测试用例**: 完整的测试用例文档
4. **性能报告**: 性能测试结果和优化建议
5. **回归测试**: 确保原有功能正常

### 测试环境清理
```bash
# cleanup_test_env.sh
echo "清理测试环境..."

# 删除测试数据库
rm -f data/test_vnpy_data.db

# 清理测试缓存
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf htmlcov

# 重置测试配置
unset TESTING
unset DATABASE_URL

echo "测试环境清理完成"
```

**严格按照本提示词执行测试，确保所有功能模块都经过充分验证，测试覆盖率达标，性能指标合格。零自由度执行，不允许跳过任何测试用例。**