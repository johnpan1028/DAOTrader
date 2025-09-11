# DAOTrader v2.1 AKShare数据获取客户端
# 封装AKShare API调用，支持股票、指数、期货数据获取

import akshare as ak
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging
import time
from functools import wraps


class AKShareClient:
    """AKShare数据获取客户端"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.retry_times = 3
        self.retry_delay = 1
        self.request_interval = 0.1  # 请求间隔，避免频率限制
        
        # 交易所映射
        self.exchange_mapping = {
            'SSE': 'sh',  # 上交所
            'SZSE': 'sz',  # 深交所
            'SHFE': 'shfe',  # 上期所
            'DCE': 'dce',  # 大商所
            'CZCE': 'czce',  # 郑商所
            'CFFEX': 'cffex'  # 中金所
        }
        
        # 时间周期映射
        self.period_mapping = {
            'daily': 'daily',
            '60min': '60',
            '30min': '30', 
            '15min': '15',
            '5min': '5',
            '1min': '1'
        }
    
    def _retry_request(self, func, *args, **kwargs):
        """重试机制装饰器"""
        for attempt in range(self.retry_times):
            try:
                time.sleep(self.request_interval)  # 请求间隔
                result = func(*args, **kwargs)
                if result is not None and len(result) > 0:
                    return result
                else:
                    self.logger.warning(f"第{attempt + 1}次请求返回空数据: {func.__name__}")
            except Exception as e:
                self.logger.warning(f"第{attempt + 1}次请求失败: {func.__name__}, 错误: {str(e)}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # 递增延迟
                else:
                    self.logger.error(f"请求最终失败: {func.__name__}, 错误: {str(e)}")
                    raise e
        return pd.DataFrame()
    
    async def get_stock_data(self, symbol: str, period: str = "daily", 
                           start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取股票历史数据
        
        Args:
            symbol: 股票代码，如 '000001'
            period: 时间周期，支持 daily, 60min, 30min, 15min, 5min, 1min
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'
            
        Returns:
            DataFrame: 包含OHLCV数据的DataFrame
        """
        try:
            self.logger.info(f"获取股票数据: {symbol}, 周期: {period}, 时间范围: {start_date} - {end_date}")
            print(f"DEBUG akshare_client: period={period}, type={type(period)}")
            
            # 参数验证
            if period not in self.period_mapping:
                raise ValueError(f"不支持的时间周期: {period}")
            
            # 设置默认时间范围
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            else:
                start_date = start_date.replace('-', '')
                
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            else:
                end_date = end_date.replace('-', '')
            
            print(f"DEBUG akshare_client: 处理后的日期 start_date={start_date}, end_date={end_date}")
            
            # 异步执行数据获取
            loop = asyncio.get_event_loop()
            
            print(f"DEBUG akshare_client: 检查period == 'daily': {period == 'daily'}")
            if period == 'daily':
                # 获取日线数据
                self.logger.info(f"调用akshare函数，参数: symbol={symbol}, period=daily, start_date={start_date}, end_date={end_date}, adjust=qfq")
                def get_stock_hist():
                    return ak.stock_zh_a_hist(
                        symbol=symbol,
                        period='daily',
                        start_date=start_date,
                        end_date=end_date,
                        adjust='qfq'
                    )
                df = await loop.run_in_executor(None, get_stock_hist)
                self.logger.info(f"akshare函数调用完成，返回数据量: {len(df) if df is not None else 0}")
            else:
                # 获取分钟数据
                df = await loop.run_in_executor(
                    None,
                    self._retry_request, 
                    ak.stock_zh_a_hist_min_em,
                    symbol,
                    start_date,
                    end_date,
                    self.period_mapping[period]
                )
            
            if len(df) == 0:
                self.logger.warning(f"未获取到股票数据: {symbol}")
                return df
            
            # 标准化列名
            df = self._standardize_columns(df, 'stock')
            
            self.logger.info(f"成功获取股票数据: {symbol}, 数据量: {len(df)}")
            return df
            
        except Exception as e:
            self.logger.error(f"获取股票数据失败: {symbol}, 错误: {str(e)}")
            raise e
    
    async def get_index_data(self, symbol: str, start_date: str = None, 
                           end_date: str = None) -> pd.DataFrame:
        """获取指数历史数据
        
        Args:
            symbol: 指数代码，如 'sh000001' (上证指数)
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'
            
        Returns:
            DataFrame: 包含OHLCV数据的DataFrame
        """
        try:
            self.logger.info(f"获取指数数据: {symbol}, 时间范围: {start_date} - {end_date}")
            
            # 设置默认时间范围
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            else:
                start_date = start_date.replace('-', '')
                
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            else:
                end_date = end_date.replace('-', '')
            
            # 异步执行数据获取
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                self._retry_request,
                ak.stock_zh_index_daily,
                symbol
            )
            
            if len(df) == 0:
                self.logger.warning(f"未获取到指数数据: {symbol}")
                return df
            
            # 过滤时间范围
            df['date'] = pd.to_datetime(df['date'])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
            
            # 标准化列名
            df = self._standardize_columns(df, 'index')
            
            self.logger.info(f"成功获取指数数据: {symbol}, 数据量: {len(df)}")
            return df
            
        except Exception as e:
            self.logger.error(f"获取指数数据失败: {symbol}, 错误: {str(e)}")
            raise e
    
    async def get_futures_data(self, symbol: str, start_date: str = None, 
                             end_date: str = None) -> pd.DataFrame:
        """获取期货历史数据
        
        Args:
            symbol: 期货代码，如 'CU0' (铜主力)
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'
            
        Returns:
            DataFrame: 包含OHLCV数据的DataFrame
        """
        try:
            self.logger.info(f"获取期货数据: {symbol}, 时间范围: {start_date} - {end_date}")
            
            # 异步执行数据获取
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                self._retry_request,
                ak.futures_main_sina,
                symbol
            )
            
            if len(df) == 0:
                self.logger.warning(f"未获取到期货数据: {symbol}")
                return df
            
            # 标准化列名
            df = self._standardize_columns(df, 'futures')
            
            # 时间范围过滤（在标准化后进行）
            if start_date or end_date:
                if start_date:
                    start_dt = pd.to_datetime(start_date)
                    df = df[df['datetime'] >= start_dt]
                if end_date:
                    end_dt = pd.to_datetime(end_date)
                    df = df[df['datetime'] <= end_dt]
            
            self.logger.info(f"成功获取期货数据: {symbol}, 数据量: {len(df)}")
            return df
            
        except Exception as e:
            import traceback
            self.logger.error(f"获取期货数据失败: {symbol}, 错误: {str(e)}")
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
            raise e
    
    def _standardize_columns(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """标准化DataFrame列名
        
        Args:
            df: 原始DataFrame
            data_type: 数据类型 'stock', 'index', 'futures'
            
        Returns:
            DataFrame: 标准化后的DataFrame
        """
        try:
            df = df.copy()
            
            # 根据数据类型进行列名映射
            if data_type == 'stock':
                column_mapping = {
                    '日期': 'datetime',
                    '开盘': 'open',
                    '收盘': 'close', 
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'turnover',
                    '振幅': 'amplitude',
                    '涨跌幅': 'pct_change',
                    '涨跌额': 'change',
                    '换手率': 'turnover_rate'
                }
            elif data_type == 'index':
                column_mapping = {
                    'date': 'datetime',
                    'open': 'open',
                    'close': 'close',
                    'high': 'high', 
                    'low': 'low',
                    'volume': 'volume',
                    'turnover': 'turnover'
                }
            elif data_type == 'futures':
                column_mapping = {
                    '日期': 'datetime',
                    '开盘价': 'open',
                    '收盘价': 'close',
                    '最高价': 'high',
                    '最低价': 'low', 
                    '成交量': 'volume',
                    '持仓量': 'open_interest',
                    '成交额': 'turnover',
                    '动态结算价': 'settlement_price',
                    'datetime': 'datetime',  # 如果已经有datetime列
                    'open': 'open',
                    'close': 'close',
                    'high': 'high',
                    'low': 'low',
                    'volume': 'volume'
                }
            else:
                return df
            
            # 重命名列
            self.logger.debug(f"重命名前的列名: {df.columns.tolist()}")
            df = df.rename(columns=column_mapping)
            self.logger.debug(f"重命名后的列名: {df.columns.tolist()}")
            
            # 确保必要列存在
            required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'volume':
                        df[col] = 0.0
                    elif col == 'turnover':
                        df[col] = 0.0
                    else:
                        self.logger.warning(f"缺少必要列: {col}")
            
            # 数据类型转换
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
            else:
                self.logger.error(f"datetime列不存在，当前列名: {df.columns.tolist()}")
                raise KeyError('datetime')
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 添加turnover列（如果不存在）
            if 'turnover' not in df.columns:
                df['turnover'] = 0.0
            else:
                df['turnover'] = pd.to_numeric(df['turnover'], errors='coerce').fillna(0.0)
            
            # 排序并重置索引
            df = df.sort_values('datetime').reset_index(drop=True)
            
            # 删除包含NaN的行
            df = df.dropna(subset=['open', 'high', 'low', 'close'])
            
            return df
            
        except Exception as e:
            self.logger.error(f"标准化列名失败: {str(e)}")
            return df
    
    async def get_supported_symbols(self, market_type: str = 'stock') -> List[Dict[str, str]]:
        """获取支持的品种列表
        
        Args:
            market_type: 市场类型 'stock', 'index', 'futures'
            
        Returns:
            List[Dict]: 品种信息列表
        """
        try:
            if market_type == 'stock':
                # 异步获取股票列表
                loop = asyncio.get_event_loop()
                df = await loop.run_in_executor(
                    None,
                    self._retry_request,
                    ak.stock_info_a_code_name
                )
                return [{
                    'symbol': row['code'],
                    'name': row['name'],
                    'market': 'stock'
                } for _, row in df.iterrows()]
            
            elif market_type == 'index':
                # 返回主要指数
                return [
                    {'symbol': 'sh000001', 'name': '上证指数', 'market': 'index'},
                    {'symbol': 'sz399001', 'name': '深证成指', 'market': 'index'},
                    {'symbol': 'sz399006', 'name': '创业板指', 'market': 'index'},
                    {'symbol': 'sh000688', 'name': '科创50', 'market': 'index'}
                ]
            
            elif market_type == 'futures':
                # 返回主要期货品种
                return [
                    {'symbol': 'CU0', 'name': '沪铜主力', 'market': 'futures'},
                    {'symbol': 'AL0', 'name': '沪铝主力', 'market': 'futures'},
                    {'symbol': 'RB0', 'name': '螺纹钢主力', 'market': 'futures'},
                    {'symbol': 'IF0', 'name': '沪深300股指期货主力', 'market': 'futures'}
                ]
            
            return []
            
        except Exception as e:
            self.logger.error(f"获取品种列表失败: {market_type}, 错误: {str(e)}")
            return []
    
    async def test_connection(self) -> bool:
        """测试AKShare连接
        
        Returns:
            bool: 连接是否正常
        """
        try:
            self.logger.info("测试AKShare连接...")
            
            # 尝试获取上证指数最近一天的数据
            df = await self.get_index_data('sh000001')
            
            if len(df) > 0:
                self.logger.info("AKShare连接测试成功")
                return True
            else:
                self.logger.warning("AKShare连接测试失败：未获取到数据")
                return False
                
        except Exception as e:
            self.logger.error(f"AKShare连接测试失败: {str(e)}")
            return False