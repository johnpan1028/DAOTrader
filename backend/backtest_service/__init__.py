"""回测服务模块

提供回测引擎、策略管理、技术指标等功能。
"""

from .backtest_engine import BacktestManager
from .strategy_manager import StrategyManager, DualMAStrategy
from .indicators import TechnicalIndicators

__all__ = [
    'BacktestManager',
    'StrategyManager',
    'DualMAStrategy', 
    'TechnicalIndicators'
]