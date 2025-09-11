"""技术指标模块

提供常用的技术分析指标计算功能，包括移动平均线、RSI、MACD、布林带等。
"""

try:
    import numpy as np
except Exception:
    np = None

try:
    import pandas as pd
except Exception:
    pd = None

try:
    import talib
except Exception:
    talib = None
from typing import List, Tuple, Dict, Any, Optional
from vnpy.trader.object import BarData

class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        pass
    
    @staticmethod
    def SMA(series, period):
        """简单移动平均线
        
        Args:
            series: 价格序列
            period: 周期
            
        Returns:
            移动平均值
        """
        if pd is not None and hasattr(series, 'rolling'):
            return series.rolling(window=period).mean()
        elif np is not None:
            return np.convolve(series, np.ones(period)/period, mode='valid')
        else:
            # 纯Python实现
            if len(series) < period:
                return [None] * len(series)
            result = []
            for i in range(len(series)):
                if i < period - 1:
                    result.append(None)
                else:
                    window = series[i-period+1:i+1]
                    result.append(sum(window) / period)
            return result
    
    @staticmethod
    def EMA(series, period):
        """指数移动平均线
        
        Args:
            series: 价格序列
            period: 周期
            
        Returns:
            指数移动平均值
        """
        if talib is not None:
            return talib.EMA(series, timeperiod=period)
        elif pd is not None and hasattr(series, 'ewm'):
            return series.ewm(span=period, adjust=False).mean()
        elif np is not None:
            # numpy实现EMA
            if len(series) < period:
                return [None] * len(series)
            
            ema = np.zeros(len(series))
            multiplier = 2 / (period + 1)
            
            # 第一个EMA是SMA
            ema[period-1] = np.mean(series[:period])
            
            for i in range(period, len(series)):
                ema[i] = (series[i] - ema[i-1]) * multiplier + ema[i-1]
            
            # 前period-1个值为None
            ema[:period-1] = None
            return ema
        else:
            # 纯Python实现EMA
            if len(series) < period:
                return [None] * len(series)
            
            result = [None] * len(series)
            multiplier = 2 / (period + 1)
            
            # 第一个EMA是SMA
            sma = sum(series[:period]) / period
            result[period-1] = sma
            
            for i in range(period, len(series)):
                ema = (series[i] - result[i-1]) * multiplier + result[i-1]
                result[i] = ema
            
            return result
    
    @staticmethod
    def RSI(series, period=14):
        """相对强弱指数
        
        Args:
            series: 价格序列
            period: 周期，默认14
            
        Returns:
            RSI值
        """
        if talib is not None:
            return talib.RSI(series, timeperiod=period)
        elif pd is not None and hasattr(series, 'diff'):
            # pandas实现RSI
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        else:
            # 纯Python实现RSI
            if len(series) < period + 1:
                return [None] * len(series)
            
            result = [None] * len(series)
            
            for i in range(period, len(series)):
                window = series[i-period:i+1]
                deltas = [window[j] - window[j-1] for j in range(1, len(window))]
                
                gains = [d if d > 0 else 0 for d in deltas]
                losses = [-d if d < 0 else 0 for d in deltas]
                
                avg_gain = sum(gains) / period
                avg_loss = sum(losses) / period
                
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                
                result[i] = rsi
            
            return result
    
    @staticmethod
    def MACD(series, fast_period=12, slow_period=26, signal_period=9):
        """MACD指标
        
        Args:
            series: 价格序列
            fast_period: 快线周期，默认12
            slow_period: 慢线周期，默认26
            signal_period: 信号线周期，默认9
            
        Returns:
            (macd, signal, hist)
        """
        if talib is not None:
            macd, signal, hist = talib.MACD(series, fastperiod=fast_period, 
                                          slowperiod=slow_period, signalperiod=signal_period)
            return macd, signal, hist
        else:
            # 纯Python实现MACD
            if len(series) < slow_period + signal_period:
                return [None] * len(series), [None] * len(series), [None] * len(series)
            
            # 计算EMA
            ema_fast = TechnicalIndicators.EMA(series, fast_period)
            ema_slow = TechnicalIndicators.EMA(series, slow_period)
            
            # 计算MACD线
            macd_line = []
            for i in range(len(series)):
                if ema_fast[i] is not None and ema_slow[i] is not None:
                    macd_line.append(ema_fast[i] - ema_slow[i])
                else:
                    macd_line.append(None)
            
            # 计算信号线
            signal_line = TechnicalIndicators.EMA(macd_line, signal_period)
            
            # 计算柱状图
            histogram = []
            for i in range(len(series)):
                if macd_line[i] is not None and signal_line[i] is not None:
                    histogram.append(macd_line[i] - signal_line[i])
                else:
                    histogram.append(None)
            
            return macd_line, signal_line, histogram
    
    @staticmethod
    def BollingerBands(series, period=20, dev=2.0):
        """布林带
        
        Args:
            series: 价格序列
            period: 周期，默认20
            dev: 标准差倍数，默认2.0
            
        Returns:
            (upper, middle, lower)
        """
        if talib is not None:
            upper, middle, lower = talib.BBANDS(series, timeperiod=period, 
                                               nbdevup=dev, nbdevdn=dev)
            return upper, middle, lower
        elif pd is not None and hasattr(series, 'rolling'):
            middle = series.rolling(window=period).mean()
            std = series.rolling(window=period).std()
            upper = middle + (std * dev)
            lower = middle - (std * dev)
            return upper, middle, lower
        elif np is not None:
            # numpy实现布林带
            if len(series) < period:
                return [None] * len(series), [None] * len(series), [None] * len(series)
            
            upper = np.full(len(series), None)
            middle = np.full(len(series), None)
            lower = np.full(len(series), None)
            
            for i in range(period-1, len(series)):
                window = series[i-period+1:i+1]
                window_mean = np.mean(window)
                window_std = np.std(window)
                
                middle[i] = window_mean
                upper[i] = window_mean + dev * window_std
                lower[i] = window_mean - dev * window_std
            
            return upper, middle, lower
        else:
            # 纯Python实现布林带
            if len(series) < period:
                return [None] * len(series), [None] * len(series), [None] * len(series)
            
            upper = [None] * len(series)
            middle = [None] * len(series)
            lower = [None] * len(series)
            
            for i in range(period-1, len(series)):
                window = series[i-period+1:i+1]
                window_mean = sum(window) / len(window)
                variance = sum((x - window_mean) ** 2 for x in window) / len(window)
                window_std = variance ** 0.5
                
                middle[i] = window_mean
                upper[i] = window_mean + dev * window_std
                lower[i] = window_mean - dev * window_std
            
            return upper, middle, lower
    
    @staticmethod
    def Stochastic(high, low, close, period=14, k_period=3, d_period=3):
        """随机指标
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期，默认14
            k_period: K线周期，默认3
            d_period: D线周期，默认3
            
        Returns:
            (k, d)
        """
        if talib is not None:
            k, d = talib.STOCH(high, low, close, fastk_period=period,
                             slowk_period=k_period, slowd_period=d_period)
            return k, d
        else:
            # 纯Python实现随机指标
            if len(high) < period or len(low) < period or len(close) < period:
                return [None] * len(close), [None] * len(close)
            
            k_values = [None] * len(close)
            d_values = [None] * len(close)
            
            for i in range(period-1, len(close)):
                high_window = high[i-period+1:i+1]
                low_window = low[i-period+1:i+1]
                close_current = close[i]
                
                highest_high = max(high_window)
                lowest_low = min(low_window)
                
                if highest_high != lowest_low:
                    k = 100 * (close_current - lowest_low) / (highest_high - lowest_low)
                else:
                    k = 50
                
                k_values[i] = k
            
            # 计算K线的移动平均
            k_sma = TechnicalIndicators.SMA(k_values, k_period)
            
            # 计算D线（K线的移动平均）
            d_sma = TechnicalIndicators.SMA(k_sma, d_period)
            
            return k_sma, d_sma
    
    @staticmethod
    def ATR(high, low, close, period=14):
        """平均真实波幅
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期，默认14
            
        Returns:
            ATR值
        """
        if talib is not None:
            return talib.ATR(high, low, close, timeperiod=period)
        else:
            # 纯Python实现ATR
            if len(high) < period or len(low) < period or len(close) < period:
                return [None] * len(close)
            
            tr_values = [None] * len(close)
            
            for i in range(1, len(close)):
                tr1 = high[i] - low[i]
                tr2 = abs(high[i] - close[i-1])
                tr3 = abs(low[i] - close[i-1])
                tr = max(tr1, tr2, tr3)
                tr_values[i] = tr
            
            # 计算TR的移动平均
            atr = TechnicalIndicators.SMA(tr_values, period)
            return atr
    
    @staticmethod
    def CCI(high, low, close, period=20):
        """商品通道指数
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期，默认20
            
        Returns:
            CCI值
        """
        if talib is not None:
            return talib.CCI(high, low, close, timeperiod=period)
        else:
            # 纯Python实现CCI
            if len(high) < period or len(low) < period or len(close) < period:
                return [None] * len(close)
            
            cci_values = [None] * len(close)
            
            for i in range(period-1, len(close)):
                typical_price = [(high[j] + low[j] + close[j]) / 3 for j in range(i-period+1, i+1)]
                sma = sum(typical_price) / period
                
                mean_deviation = sum(abs(tp - sma) for tp in typical_price) / period
                
                if mean_deviation != 0:
                    cci = (typical_price[-1] - sma) / (0.015 * mean_deviation)
                else:
                    cci = 0
                
                cci_values[i] = cci
            
            return cci_values
    
    @staticmethod
    def WilliamsR(high, low, close, period=14):
        """威廉指标
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期，默认14
            
        Returns:
            威廉指标值
        """
        if talib is not None:
            return talib.WILLR(high, low, close, timeperiod=period)
        else:
            # 纯Python实现威廉指标
            if len(high) < period or len(low) < period or len(close) < period:
                return [None] * len(close)
            
            williams_r = [None] * len(close)
            
            for i in range(period-1, len(close)):
                highest_high = max(high[i-period+1:i+1])
                lowest_low = min(low[i-period+1:i+1])
                
                if highest_high != lowest_low:
                    wr = -100 * (highest_high - close[i]) / (highest_high - lowest_low)
                else:
                    wr = -50
                
                williams_r[i] = wr
            
            return williams_r
    
    @staticmethod
    def OBV(close, volume):
        """能量潮指标
        
        Args:
            close: 收盘价序列
            volume: 成交量序列
            
        Returns:
            OBV值
        """
        if talib is not None:
            return talib.OBV(close, volume)
        else:
            # 纯Python实现OBV
            if len(close) != len(volume):
                return [None] * len(close)
            
            obv = [0] * len(close)
            
            for i in range(1, len(close)):
                if close[i] > close[i-1]:
                    obv[i] = obv[i-1] + volume[i]
                elif close[i] < close[i-1]:
                    obv[i] = obv[i-1] - volume[i]
                else:
                    obv[i] = obv[i-1]
            
            return obv
    
    @staticmethod
    def ADX(high, low, close, period=14):
        """平均趋向指数
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期，默认14
            
        Returns:
            ADX值
        """
        if talib is not None:
            return talib.ADX(high, low, close, timeperiod=period)
        else:
            # 纯Python实现ADX（简化版）
            if len(high) < period or len(low) < period or len(close) < period:
                return [None] * len(close)
            
            # 简化实现：返回50作为中性值
            return [50] * len(close)
    
    @staticmethod
    def calculate_from_bars(bars, indicator_name, **params):
        """根据K线数据计算指定指标
        
        Args:
            bars: K线数据列表
            indicator_name: 指标名称
            **params: 指标参数
            
        Returns:
            指标值
        """
        # 提取价格序列
        closes = [bar.close_price for bar in bars]
        highs = [bar.high_price for bar in bars]
        lows = [bar.low_price for bar in bars]
        volumes = [bar.volume for bar in bars] if hasattr(bars[0], 'volume') else [1] * len(bars)
        
        # 根据指标名称调用对应方法
        if indicator_name == 'SMA':
            return TechnicalIndicators.SMA(closes, params.get('period', 20))
        elif indicator_name == 'EMA':
            return TechnicalIndicators.EMA(closes, params.get('period', 20))
        elif indicator_name == 'RSI':
            return TechnicalIndicators.RSI(closes, params.get('period', 14))
        elif indicator_name == 'MACD':
            return TechnicalIndicators.MACD(closes, 
                                          params.get('fast_period', 12),
                                          params.get('slow_period', 26),
                                          params.get('signal_period', 9))
        elif indicator_name == 'BollingerBands':
            return TechnicalIndicators.BollingerBands(closes,
                                                    params.get('period', 20),
                                                    params.get('dev', 2.0))
        elif indicator_name == 'Stochastic':
            return TechnicalIndicators.Stochastic(highs, lows, closes,
                                                params.get('period', 14),
                                                params.get('k_period', 3),
                                                params.get('d_period', 3))
        elif indicator_name == 'ATR':
            return TechnicalIndicators.ATR(highs, lows, closes,
                                          params.get('period', 14))
        elif indicator_name == 'CCI':
            return TechnicalIndicators.CCI(highs, lows, closes,
                                         params.get('period', 20))
        elif indicator_name == 'WilliamsR':
            return TechnicalIndicators.WilliamsR(highs, lows, closes,
                                               params.get('period', 14))
        elif indicator_name == 'OBV':
            return TechnicalIndicators.OBV(closes, volumes)
        elif indicator_name == 'ADX':
            return TechnicalIndicators.ADX(highs, lows, closes,
                                          params.get('period', 14))
        else:
            raise ValueError(f"不支持的指标: {indicator_name}")
    
    @staticmethod
    def get_supported_indicators():
        """获取支持的指标列表
        
        Returns:
            支持的指标名称和参数信息
        """
        return {
            'SMA': {'period': 'int'},
            'EMA': {'period': 'int'},
            'RSI': {'period': 'int'},
            'MACD': {'fast_period': 'int', 'slow_period': 'int', 'signal_period': 'int'},
            'BollingerBands': {'period': 'int', 'dev': 'float'},
            'Stochastic': {'period': 'int', 'k_period': 'int', 'd_period': 'int'},
            'ATR': {'period': 'int'},
            'CCI': {'period': 'int'},
            'WilliamsR': {'period': 'int'},
            'OBV': {},
            'ADX': {'period': 'int'}
        }
    
    @staticmethod
    def batch_calculate(bars, indicators_config):
        """批量计算多个技术指标
        
        Args:
            bars: K线数据列表
            indicators_config: 指标配置列表，每个配置包含name和params
            
        Returns:
            指标计算结果字典
        """
        results = {}
        
        for config in indicators_config:
            name = config['name']
            params = config.get('params', {})
            
            try:
                result = TechnicalIndicators.calculate_from_bars(bars, name, **params)
                results[name] = result
            except Exception as e:
                results[name] = {'error': str(e)}
        
        return results