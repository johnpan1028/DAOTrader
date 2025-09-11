#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测引擎模块功能测试脚本
测试策略管理、技术指标计算和回测执行等核心功能
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 使用绝对导入
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from backtest_service.strategy_manager import StrategyManager, DualMAStrategy
    from backtest_service.indicators import TechnicalIndicators
    from backtest_service.backtest_engine import BacktestManager
    
    # 尝试不同的VNPY导入路径
    try:
        from vnpy.trader.object import BarData, Interval, Exchange
        from vnpy.trader.constant import Direction, Offset
    except ImportError:
        try:
            from vnpy_core.trader.object import BarData, Interval, Exchange
            from vnpy_core.trader.constant import Direction, Offset
        except ImportError:
            # 如果都失败，创建简化的测试类
            print("警告: 无法导入VNPY对象，使用简化测试模式")
            class BarData:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            
            class Interval:
                MINUTE = "1m"
            
            class Exchange:
                SSE = "SSE"
            
            class Direction:
                LONG = "LONG"
                SHORT = "SHORT"
            
            class Offset:
                OPEN = "OPEN"
                CLOSE = "CLOSE"
                
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装VNPY相关依赖包")
    sys.exit(1)

def create_sample_bars() -> List[BarData]:
    """
    创建示例K线数据用于测试
    """
    bars = []
    base_time = datetime(2024, 1, 1, 9, 30)
    base_price = 100.0
    
    for i in range(100):
        # 模拟价格波动
        price_change = (i % 10 - 5) * 0.5
        open_price = base_price + price_change
        high_price = open_price + abs(price_change) * 0.5
        low_price = open_price - abs(price_change) * 0.3
        close_price = open_price + price_change * 0.8
        
        bar = BarData(
            symbol="000001",
            exchange=Exchange.SSE,
            datetime=base_time + timedelta(minutes=i),
            interval=Interval.MINUTE,
            gateway_name="DB",
            volume=1000 + i * 10,
            turnover=(open_price + close_price) * (1000 + i * 10) / 2,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price
        )
        bars.append(bar)
        base_price = close_price
    
    return bars

def test_strategy_manager():
    """
    测试策略管理器功能
    """
    print("\n=== 测试策略管理器 ===")
    
    manager = StrategyManager()
    
    # 测试获取策略列表
    strategies = manager.get_strategy_list()
    print(f"可用策略数量: {len(strategies)}")
    for strategy_name in strategies:
        print(f"- {strategy_name}")
    
    # 测试获取策略信息
    if "DualMA" in strategies:
        info = manager.get_strategy_info("DualMA")
        print(f"\n双均线策略信息:")
        print(f"描述: {info['description']}")
        print(f"参数: {info['parameters']}")
    
    # 测试参数验证
    valid_params = {"fast_window": 5, "slow_window": 20}
    invalid_params = {"fast_window": 25, "slow_window": 10}  # fast > slow
    
    print(f"\n参数验证测试:")
    try:
        result1 = manager.validate_strategy_setting('DualMA', valid_params)
        print(f"有效参数 {valid_params}: {result1['valid']}")
    except Exception as e:
        print(f"有效参数验证失败: {e}")
    
    try:
        result2 = manager.validate_strategy_setting('DualMA', invalid_params)
        print(f"无效参数 {invalid_params}: {result2['valid']}")
    except Exception as e:
        print(f"无效参数验证失败: {e}")

def test_technical_indicators():
    """
    测试技术指标计算功能
    """
    print("\n=== 测试技术指标计算 ===")
    
    # 创建测试数据
    prices = [100 + i * 0.5 + (i % 5 - 2) * 0.3 for i in range(50)]
    
    indicators = TechnicalIndicators()
    
    # 测试SMA
    sma_5 = indicators.sma(prices, 5)
    print(f"SMA(5) 最后5个值: {sma_5[-5:]}")
    
    # 测试EMA
    ema_5 = indicators.ema(prices, 5)
    print(f"EMA(5) 最后5个值: {ema_5[-5:]}")
    
    # 测试RSI
    rsi = indicators.rsi(prices, 14)
    print(f"RSI(14) 最后5个值: {rsi[-5:]}")
    
    # 测试MACD
    macd_line, signal_line, histogram = indicators.macd(prices)
    print(f"MACD 最后值: {macd_line[-1]:.4f}")
    print(f"Signal 最后值: {signal_line[-1]:.4f}")
    print(f"Histogram 最后值: {histogram[-1]:.4f}")
    
    # 测试布林带
    upper, middle, lower = indicators.bollinger_bands(prices, 20, 2.0)
    print(f"布林带最后值 - 上轨: {upper[-1]:.2f}, 中轨: {middle[-1]:.2f}, 下轨: {lower[-1]:.2f}")

def test_backtest_engine():
    """
    测试回测引擎功能
    """
    print("\n=== 测试回测引擎 ===")
    
    # 创建回测管理器
    backtest_manager = BacktestManager()
    
    # 创建示例数据
    bars = create_sample_bars()
    print(f"创建了 {len(bars)} 条K线数据")
    
    # 配置回测参数
    backtest_config = {
        "strategy_class": "DualMAStrategy",
        "strategy_params": {"fast_window": 5, "slow_window": 20},
        "start_date": "2024-01-01",
        "end_date": "2024-01-02",
        "initial_capital": 100000.0,
        "commission_rate": 0.0003,
        "slippage": 0.01,
        "size_multiplier": 1
    }
    
    try:
        # 运行回测
        print("\n开始运行回测...")
        result = backtest_manager.run_backtest(
            symbol="000001",
            exchange="SSE",
            interval="1m",
            bars=bars,
            **backtest_config
        )
        
        if result:
            print("回测完成！")
            print(f"总收益率: {result.get('total_return', 0):.2%}")
            print(f"年化收益率: {result.get('annual_return', 0):.2%}")
            print(f"最大回撤: {result.get('max_drawdown', 0):.2%}")
            print(f"夏普比率: {result.get('sharpe_ratio', 0):.2f}")
            print(f"交易次数: {result.get('total_trades', 0)}")
            print(f"胜率: {result.get('win_rate', 0):.2%}")
        else:
            print("回测失败")
            
    except Exception as e:
        print(f"回测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    主测试函数
    """
    print("开始回测引擎模块功能测试")
    print("=" * 50)
    
    try:
        # 测试策略管理器
        test_strategy_manager()
        
        # 测试技术指标
        test_technical_indicators()
        
        # 测试回测引擎
        test_backtest_engine()
        
        print("\n=" * 50)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)