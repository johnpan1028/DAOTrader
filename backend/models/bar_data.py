# DAOTrader v2.1 K线数据模型
# 定义K线数据的Pydantic模型

from pydantic import BaseModel, Field
from datetime import datetime as dt
from typing import Optional


class BarDataModel(BaseModel):
    """K线数据模型"""
    
    symbol: str
    exchange: str
    datetime: dt
    interval: str
    volume: float
    turnover: float = 0.0
    open_price: float
    high_price: float
    low_price: float
    close_price: float


class DataDownloadRequest(BaseModel):
    """数据下载请求模型"""
    
    symbol: str
    exchange: str
    interval: str = "daily"
    start_date: str
    end_date: str


class DataStatusResponse(BaseModel):
    """数据状态响应模型"""
    
    symbol: str
    exchange: str
    interval: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    count: int = 0
    last_update: Optional[dt] = None