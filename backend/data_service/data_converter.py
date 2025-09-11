# DAOTrader v2.1 数据转换适配器
# 将AKShare数据转换为VNPY BarData格式

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
from vnpy.trader.object import BarData, Exchange, Interval
from vnpy.trader.constant import Exchange as VnpyExchange, Interval as VnpyInterval


class DataConverter:
    """数据转换适配器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 交易所映射
        self.exchange_mapping = {
            'SSE': VnpyExchange.SSE,  # 上交所
            'SZSE': VnpyExchange.SZSE,  # 深交所
            'SHFE': VnpyExchange.SHFE,  # 上期所
            'DCE': VnpyExchange.DCE,  # 大商所
            'CZCE': VnpyExchange.CZCE,  # 郑商所
            'CFFEX': VnpyExchange.CFFEX,  # 中金所
            'sh': VnpyExchange.SSE,
            'sz': VnpyExchange.SZSE
        }
        
        # 时间周期映射
        self.interval_mapping = {
            'daily': VnpyInterval.DAILY,
            'd': VnpyInterval.DAILY,
            '1d': VnpyInterval.DAILY,
            '60min': VnpyInterval.HOUR,
            '1h': VnpyInterval.HOUR,
            '30min': VnpyInterval.MINUTE,  # 使用通用MINUTE
            '15min': VnpyInterval.MINUTE,  # 使用通用MINUTE
            '5min': VnpyInterval.MINUTE,   # 使用通用MINUTE
            '1min': VnpyInterval.MINUTE,
            '1m': VnpyInterval.MINUTE
        }
    
    def akshare_to_vnpy_bars(self, df: pd.DataFrame, symbol: str, 
                            exchange: str, interval: str) -> List[BarData]:
        """将AKShare DataFrame转换为VNPY BarData列表
        
        Args:
            df: AKShare数据DataFrame
            symbol: 品种代码
            exchange: 交易所代码
            interval: 时间周期
            
        Returns:
            List[BarData]: VNPY BarData对象列表
        """
        try:
            self.logger.info(f"转换数据: {symbol}.{exchange}, 周期: {interval}, 数据量: {len(df)}")
            
            if len(df) == 0:
                self.logger.warning("输入数据为空")
                return []
            
            # 验证必要列
            required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"缺少必要列: {missing_columns}")
            
            # 获取VNPY交易所和周期
            vnpy_exchange = self._get_vnpy_exchange(exchange)
            vnpy_interval = self._get_vnpy_interval(interval)
            
            bars = []
            
            for _, row in df.iterrows():
                try:
                    # 处理时间，确保返回Python datetime对象
                    dt = self._parse_datetime(row['datetime'])
                    
                    # 如果仍然是pandas Timestamp，强制转换
                    if hasattr(dt, 'to_pydatetime'):
                        dt = dt.to_pydatetime()
                    
                    # 移除时区信息以避免SQLite绑定问题
                    if hasattr(dt, 'tzinfo') and dt.tzinfo:
                        dt = dt.replace(tzinfo=None)
                    
                    # 创建BarData对象
                    bar = BarData(
                        symbol=symbol,
                        exchange=vnpy_exchange,
                        datetime=dt,
                        interval=vnpy_interval,
                        volume=float(row['volume']) if pd.notna(row['volume']) else 0.0,
                        turnover=float(row.get('turnover', 0.0)) if pd.notna(row.get('turnover', 0.0)) else 0.0,
                        open_price=float(row['open']),
                        high_price=float(row['high']),
                        low_price=float(row['low']),
                        close_price=float(row['close']),
                        gateway_name="akshare"
                    )
                    
                    bars.append(bar)
                    
                except Exception as e:
                    self.logger.warning(f"转换单条数据失败: {row.to_dict()}, 错误: {str(e)}")
                    continue
            
            self.logger.info(f"成功转换数据: {len(bars)} 条")
            return bars
            
        except Exception as e:
            self.logger.error(f"数据转换失败: {str(e)}")
            raise e
    
    def vnpy_bars_to_dataframe(self, bars: List[BarData]) -> pd.DataFrame:
        """将VNPY BarData列表转换为DataFrame
        
        Args:
            bars: VNPY BarData对象列表
            
        Returns:
            pd.DataFrame: 标准化的DataFrame
        """
        try:
            if not bars:
                return pd.DataFrame()
            
            data = []
            for bar in bars:
                data.append({
                    'datetime': bar.datetime,
                    'symbol': bar.symbol,
                    'exchange': bar.exchange.value,
                    'interval': bar.interval.value,
                    'open': bar.open_price,
                    'high': bar.high_price,
                    'low': bar.low_price,
                    'close': bar.close_price,
                    'volume': bar.volume,
                    'turnover': bar.turnover
                })
            
            df = pd.DataFrame(data)
            df = df.sort_values('datetime').reset_index(drop=True)
            
            self.logger.info(f"成功转换VNPY数据为DataFrame: {len(df)} 条")
            return df
            
        except Exception as e:
            self.logger.error(f"VNPY数据转换为DataFrame失败: {str(e)}")
            raise e
    
    def dataframe_to_dict_list(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """将DataFrame转换为字典列表
        
        Args:
            df: 输入DataFrame
            
        Returns:
            List[Dict]: 字典列表
        """
        try:
            if len(df) == 0:
                return []
            
            # 处理datetime列
            df_copy = df.copy()
            if 'datetime' in df_copy.columns:
                df_copy['datetime'] = df_copy['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            result = df_copy.to_dict('records')
            
            self.logger.info(f"成功转换DataFrame为字典列表: {len(result)} 条")
            return result
            
        except Exception as e:
            self.logger.error(f"DataFrame转换为字典列表失败: {str(e)}")
            raise e
    
    def vnpy_to_dict_list(self, bars: List[BarData]) -> List[Dict[str, Any]]:
        """将VNPY BarData列表转换为字典列表
        
        Args:
            bars: VNPY BarData对象列表
            
        Returns:
            List[Dict]: 字典列表
        """
        try:
            if not bars:
                return []
            
            result = []
            for bar in bars:
                result.append({
                    'datetime': bar.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'symbol': bar.symbol,
                    'exchange': bar.exchange.value,
                    'interval': bar.interval.value,
                    'open': bar.open_price,
                    'high': bar.high_price,
                    'low': bar.low_price,
                    'close': bar.close_price,
                    'volume': bar.volume,
                    'turnover': bar.turnover
                })
            
            self.logger.info(f"成功转换VNPY数据为字典列表: {len(result)} 条")
            return result
            
        except Exception as e:
            self.logger.error(f"VNPY数据转换为字典列表失败: {str(e)}")
            raise e
    
    def dict_list_to_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """将字典列表转换为DataFrame
        
        Args:
            data: 字典列表
            
        Returns:
            pd.DataFrame: 标准化的DataFrame
        """
        try:
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            
            # 处理datetime列
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
            
            # 数据类型转换
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'turnover']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.sort_values('datetime').reset_index(drop=True)
            
            self.logger.info(f"成功转换字典列表为DataFrame: {len(df)} 条")
            return df
            
        except Exception as e:
            self.logger.error(f"字典列表转换为DataFrame失败: {str(e)}")
            raise e
    
    def _get_vnpy_exchange(self, exchange: str) -> VnpyExchange:
        """获取VNPY交易所枚举
        
        Args:
            exchange: 交易所代码
            
        Returns:
            VnpyExchange: VNPY交易所枚举
        """
        # 根据品种代码推断交易所
        if exchange in self.exchange_mapping:
            return self.exchange_mapping[exchange]
        
        # 默认返回上交所
        self.logger.warning(f"未知交易所: {exchange}, 使用默认值 SSE")
        return VnpyExchange.SSE
    
    def _get_vnpy_interval(self, interval: str) -> VnpyInterval:
        """获取VNPY时间周期枚举
        
        Args:
            interval: 时间周期
            
        Returns:
            VnpyInterval: VNPY时间周期枚举
        """
        if interval in self.interval_mapping:
            return self.interval_mapping[interval]
        
        # 默认返回日线
        self.logger.warning(f"未知时间周期: {interval}, 使用默认值 DAILY")
        return VnpyInterval.DAILY
    
    def _parse_datetime(self, dt) -> datetime:
        """解析时间格式
        
        Args:
            dt: 时间对象
            
        Returns:
            datetime: 标准化的datetime对象
        """
        try:
            if isinstance(dt, datetime):
                # 确保有时区信息
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            elif isinstance(dt, str):
                # 解析字符串时间
                dt_obj = pd.to_datetime(dt)
                # 转换为Python datetime对象
                if hasattr(dt_obj, 'to_pydatetime'):
                    dt_obj = dt_obj.to_pydatetime()
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                return dt_obj
            else:
                # 其他类型转换（如pandas Timestamp）
                dt_obj = pd.to_datetime(dt)
                # 转换为Python datetime对象
                if hasattr(dt_obj, 'to_pydatetime'):
                    dt_obj = dt_obj.to_pydatetime()
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                return dt_obj
                
        except Exception as e:
            self.logger.error(f"时间解析失败: {dt}, 错误: {str(e)}")
            # 返回当前时间作为默认值
            return datetime.now(timezone.utc)
    
    def infer_exchange_from_symbol(self, symbol: str) -> str:
        """根据品种代码推断交易所
        
        Args:
            symbol: 品种代码
            
        Returns:
            str: 交易所代码
        """
        try:
            # 股票代码规则
            if symbol.startswith('00') or symbol.startswith('30'):
                return 'SZSE'  # 深交所
            elif symbol.startswith('60') or symbol.startswith('68'):
                return 'SSE'   # 上交所
            
            # 指数代码规则
            elif symbol.startswith('sh'):
                return 'SSE'
            elif symbol.startswith('sz'):
                return 'SZSE'
            
            # 期货代码规则（简化）
            elif len(symbol) <= 4 and symbol[-1].isdigit():
                # 根据品种前缀判断
                commodity = symbol[:-1]
                if commodity.upper() in ['CU', 'AL', 'ZN', 'PB', 'NI', 'SN', 'AU', 'AG']:
                    return 'SHFE'  # 上期所
                elif commodity.upper() in ['C', 'CS', 'A', 'B', 'M', 'Y', 'P', 'FB', 'BB', 'JD', 'L', 'V', 'PP', 'J', 'JM', 'I', 'EG', 'EB', 'PG']:
                    return 'DCE'   # 大商所
                elif commodity.upper() in ['WH', 'PM', 'CF', 'SR', 'OI', 'RI', 'RS', 'RM', 'TC', 'ZC', 'FG', 'MA', 'TA', 'UR', 'SA', 'PF', 'CY', 'AP', 'CJ', 'PK']:
                    return 'CZCE'  # 郑商所
                elif commodity.upper() in ['IF', 'IC', 'IH', 'T', 'TF', 'TS']:
                    return 'CFFEX' # 中金所
            
            # 默认返回上交所
            self.logger.warning(f"无法推断交易所: {symbol}, 使用默认值 SSE")
            return 'SSE'
            
        except Exception as e:
            self.logger.error(f"推断交易所失败: {symbol}, 错误: {str(e)}")
            return 'SSE'
    
    def validate_bar_data(self, bars: List[BarData]) -> List[BarData]:
        """验证和清理BarData数据
        
        Args:
            bars: BarData列表
            
        Returns:
            List[BarData]: 验证后的BarData列表
        """
        try:
            valid_bars = []
            
            for bar in bars:
                # 基本数据验证
                if (bar.open_price <= 0 or bar.high_price <= 0 or 
                    bar.low_price <= 0 or bar.close_price <= 0):
                    self.logger.warning(f"价格数据异常: {bar.symbol} {bar.datetime}")
                    continue
                
                # 价格逻辑验证
                if (bar.high_price < max(bar.open_price, bar.close_price) or
                    bar.low_price > min(bar.open_price, bar.close_price)):
                    self.logger.warning(f"价格逻辑异常: {bar.symbol} {bar.datetime}")
                    continue
                
                # 成交量验证
                if bar.volume < 0:
                    bar.volume = 0
                
                valid_bars.append(bar)
            
            self.logger.info(f"数据验证完成: 输入 {len(bars)} 条, 有效 {len(valid_bars)} 条")
            return valid_bars
            
        except Exception as e:
            self.logger.error(f"数据验证失败: {str(e)}")
            return bars
    
    def merge_bar_data(self, bars1: List[BarData], bars2: List[BarData]) -> List[BarData]:
        """合并两个BarData列表
        
        Args:
            bars1: 第一个BarData列表
            bars2: 第二个BarData列表
            
        Returns:
            List[BarData]: 合并后的BarData列表
        """
        try:
            # 转换为DataFrame进行合并
            df1 = self.vnpy_bars_to_dataframe(bars1)
            df2 = self.vnpy_bars_to_dataframe(bars2)
            
            # 合并并去重
            df_merged = pd.concat([df1, df2], ignore_index=True)
            df_merged = df_merged.drop_duplicates(subset=['datetime', 'symbol', 'exchange'])
            df_merged = df_merged.sort_values('datetime').reset_index(drop=True)
            
            # 转换回BarData
            merged_bars = []
            for _, row in df_merged.iterrows():
                bar = BarData(
                    symbol=row['symbol'],
                    exchange=VnpyExchange(row['exchange']),
                    datetime=row['datetime'],
                    interval=VnpyInterval(row['interval']),
                    volume=row['volume'],
                    turnover=row['turnover'],
                    open_price=row['open'],
                    high_price=row['high'],
                    low_price=row['low'],
                    close_price=row['close'],
                    gateway_name="akshare"
                )
                merged_bars.append(bar)
            
            self.logger.info(f"数据合并完成: {len(bars1)} + {len(bars2)} = {len(merged_bars)}")
            return merged_bars
            
        except Exception as e:
            self.logger.error(f"数据合并失败: {str(e)}")
            return bars1 + bars2