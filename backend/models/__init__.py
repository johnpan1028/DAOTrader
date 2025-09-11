# DAOTrader v2.1 数据模型定义
# 定义系统中使用的数据结构

from .bar_data import BarDataModel
from .backtest_result import BacktestResultModel

__all__ = [
    "BarDataModel",
    "BacktestResultModel"
]