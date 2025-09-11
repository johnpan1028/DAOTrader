# DAOTrader v2.1 回测结果模型
# 定义回测结果的Pydantic模型

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Any, Optional


class BacktestRequest(BaseModel):
    """回测请求模型"""
    
    strategy_name: str = Field(..., description="策略名称")
    symbol: str = Field(..., description="品种代码")
    exchange: str = Field(..., description="交易所代码")
    interval: str = Field(default="daily", description="时间周期")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    capital: float = Field(default=100000.0, description="初始资金")
    rate: float = Field(default=0.0003, description="手续费率")
    slippage: float = Field(default=0.2, description="滑点")
    size: int = Field(default=1, description="合约乘数")
    pricetick: float = Field(default=0.01, description="最小价格变动")
    setting: Dict[str, Any] = Field(default_factory=dict, description="策略参数")
    
    class Config:
        schema_extra = {
            "example": {
                "strategy_name": "MovingAverage",
                "symbol": "000001",
                "exchange": "SSE",
                "interval": "daily",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "capital": 100000.0,
                "rate": 0.0003,
                "slippage": 0.2,
                "size": 1,
                "pricetick": 0.01,
                "setting": {
                    "fast_window": 10,
                    "slow_window": 20
                }
            }
        }


class TradeRecord(BaseModel):
    """交易记录模型"""
    
    datetime: datetime = Field(..., description="交易时间")
    symbol: str = Field(..., description="品种代码")
    direction: str = Field(..., description="交易方向 LONG/SHORT")
    offset: str = Field(..., description="开平仓 OPEN/CLOSE")
    price: float = Field(..., description="成交价格")
    volume: int = Field(..., description="成交数量")
    commission: float = Field(default=0.0, description="手续费")
    slippage: float = Field(default=0.0, description="滑点")
    pnl: float = Field(default=0.0, description="盈亏")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BacktestResultModel(BaseModel):
    """回测结果模型"""
    
    task_id: str = Field(..., description="任务ID")
    status: str = Field(default="running", description="任务状态")
    strategy_name: str = Field(..., description="策略名称")
    symbol: str = Field(..., description="品种代码")
    exchange: str = Field(..., description="交易所代码")
    interval: str = Field(..., description="时间周期")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    capital: float = Field(..., description="初始资金")
    setting: Dict[str, Any] = Field(default_factory=dict, description="策略参数")
    
    # 回测结果指标
    total_return: Optional[float] = Field(None, description="总收益率")
    annual_return: Optional[float] = Field(None, description="年化收益率")
    max_drawdown: Optional[float] = Field(None, description="最大回撤")
    sharpe_ratio: Optional[float] = Field(None, description="夏普比率")
    sortino_ratio: Optional[float] = Field(None, description="索提诺比率")
    calmar_ratio: Optional[float] = Field(None, description="卡玛比率")
    
    # 交易统计
    total_trades: Optional[int] = Field(None, description="总交易次数")
    win_trades: Optional[int] = Field(None, description="盈利交易次数")
    lose_trades: Optional[int] = Field(None, description="亏损交易次数")
    win_rate: Optional[float] = Field(None, description="胜率")
    avg_win: Optional[float] = Field(None, description="平均盈利")
    avg_lose: Optional[float] = Field(None, description="平均亏损")
    profit_factor: Optional[float] = Field(None, description="盈亏比")
    
    # 详细数据
    trades: List[TradeRecord] = Field(default_factory=list, description="交易记录")
    daily_returns: List[float] = Field(default_factory=list, description="日收益率")
    equity_curve: List[float] = Field(default_factory=list, description="资金曲线")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "task_id": "bt_20240101_123456",
                "status": "completed",
                "strategy_name": "MovingAverage",
                "symbol": "000001",
                "exchange": "SSE",
                "interval": "daily",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "capital": 100000.0,
                "setting": {"fast_window": 10, "slow_window": 20},
                "total_return": 0.15,
                "annual_return": 0.15,
                "max_drawdown": 0.08,
                "sharpe_ratio": 1.2,
                "total_trades": 25,
                "win_rate": 0.6
            }
        }