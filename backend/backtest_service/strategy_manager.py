"""策略管理模块

内置经典策略模板，支持自定义策略，策略参数管理，策略验证。
"""

# 尝试不同的VNPY导入路径
try:
    from vnpy.app.cta_strategy import CtaTemplate, StopOrder
    from vnpy.trader.object import TickData, BarData
    from vnpy.trader.constant import Direction, Status
    from vnpy.trader.utility import ArrayManager
except ImportError:
    try:
        from vnpy_ctastrategy import CtaTemplate
        from vnpy.trader.object import TickData, BarData
        from vnpy.trader.constant import Direction, Status
        from vnpy.trader.utility import ArrayManager
        
        class StopOrder:
            pass
    except ImportError:
        # 创建简化的类用于测试
        print("警告: 无法导入VNPY策略基类，使用简化模式")
        
        class CtaTemplate:
            def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
                self.cta_engine = cta_engine
                self.strategy_name = strategy_name
                self.vt_symbol = vt_symbol
                self.setting = setting
                self.pos = 0
                self.inited = False
                self.trading = False
            
            def on_init(self):
                pass
            
            def on_start(self):
                pass
            
            def on_stop(self):
                pass
            
            def on_bar(self, bar):
                pass
            
            def buy(self, price, volume, stop=False, lock=False, net=False):
                pass
            
            def sell(self, price, volume, stop=False, lock=False, net=False):
                pass
            
            def short(self, price, volume, stop=False, lock=False, net=False):
                pass
            
            def cover(self, price, volume, stop=False, lock=False, net=False):
                pass
            
            def write_log(self, msg):
                print(f"[{self.strategy_name}] {msg}")
            
            def load_bar(self, days):
                pass
            
            def put_event(self):
                pass
        
        class StopOrder:
            pass
        
        class TickData:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        
        class BarData:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        
        class Direction:
            LONG = "LONG"
            SHORT = "SHORT"
        
        class Status:
            SUBMITTING = "SUBMITTING"
            NOTTRADED = "NOTTRADED"
            PARTTRADED = "PARTTRADED"
            ALLTRADED = "ALLTRADED"
            CANCELLED = "CANCELLED"
            REJECTED = "REJECTED"
        
        class ArrayManager:
            def __init__(self, size=100):
                self.size = size
                self.inited = False
                self.close = []
            
            def update_bar(self, bar):
                if hasattr(bar, 'close_price'):
                    self.close.append(bar.close_price)
                    if len(self.close) > self.size:
                        self.close.pop(0)
                    if len(self.close) >= 30:
                        self.inited = True
from typing import Dict, Any, List, Type
try:
    import talib
except Exception:
    talib = None

class DualMAStrategy(CtaTemplate):
    """双均线策略示例"""
    
    author = "DAOTrader"
    
    # 策略参数
    fast_window = 10
    slow_window = 20
    
    # 策略变量
    fast_ma = 0.0
    slow_ma = 0.0
    ma_trend = 0
    
    parameters = ["fast_window", "slow_window"]
    variables = ["fast_ma", "slow_ma", "ma_trend"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        self.am = ArrayManager()
        
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(10)
        
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
        
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
        
    def on_bar(self, bar: BarData):
        """K线数据推送"""
        self.am.update_bar(bar)
        if not self.am.inited:
            return
            
        # 计算技术指标
        fast_array = self.am.close[-self.fast_window:]
        slow_array = self.am.close[-self.slow_window:]
        
        if talib is not None:
            self.fast_ma = talib.SMA(fast_array, self.fast_window)[-1]
            self.slow_ma = talib.SMA(slow_array, self.slow_window)[-1]
        else:
            # 纯Python计算移动平均
            self.fast_ma = sum(fast_array) / len(fast_array) if fast_array else 0
            self.slow_ma = sum(slow_array) / len(slow_array) if slow_array else 0
        
        # 判断趋势
        if self.fast_ma > self.slow_ma:
            if self.ma_trend <= 0:
                self.ma_trend = 1
                # 金叉信号，买入
                if self.pos == 0:
                    self.buy(bar.close_price + 5, 1)
                elif self.pos < 0:
                    self.cover(bar.close_price + 5, abs(self.pos))
                    self.buy(bar.close_price + 5, 1)
                    
        elif self.fast_ma < self.slow_ma:
            if self.ma_trend >= 0:
                self.ma_trend = -1
                # 死叉信号，卖出
                if self.pos == 0:
                    self.short(bar.close_price - 5, 1)
                elif self.pos > 0:
                    self.sell(bar.close_price - 5, abs(self.pos))
                    self.short(bar.close_price - 5, 1)
        
        self.put_event()

class RSIStrategy(CtaTemplate):
    """RSI策略示例"""
    
    author = "DAOTrader"
    
    # 策略参数
    rsi_window = 14
    rsi_upper = 70
    rsi_lower = 30
    
    # 策略变量
    rsi_value = 0.0
    rsi_trend = 0
    
    parameters = ["rsi_window", "rsi_upper", "rsi_lower"]
    variables = ["rsi_value", "rsi_trend"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        self.am = ArrayManager()
        
    def on_init(self):
        """策略初始化"""
        self.write_log("RSI策略初始化")
        self.load_bar(10)
        
    def on_start(self):
        """策略启动"""
        self.write_log("RSI策略启动")
        
    def on_stop(self):
        """策略停止"""
        self.write_log("RSI策略停止")
        
    def on_bar(self, bar: BarData):
        """K线数据推送"""
        self.am.update_bar(bar)
        if not self.am.inited:
            return
            
        # 计算RSI指标
        if talib is not None:
            self.rsi_value = talib.RSI(self.am.close, self.rsi_window)[-1]
        else:
            # 纯Python计算RSI
            if len(self.am.close) < self.rsi_window + 1:
                self.rsi_value = 50.0
            else:
                deltas = [self.am.close[i] - self.am.close[i-1] for i in range(1, len(self.am.close))]
                gains = [d if d > 0 else 0.0 for d in deltas]
                losses = [-d if d < 0 else 0.0 for d in deltas]
                
                avg_gain = sum(gains[-self.rsi_window:]) / self.rsi_window
                avg_loss = sum(losses[-self.rsi_window:]) / self.rsi_window
                
                if avg_loss == 0:
                    self.rsi_value = 100.0
                else:
                    rs = avg_gain / avg_loss
                    self.rsi_value = 100 - (100 / (1 + rs))
        
        # RSI交易信号
        if self.rsi_value < self.rsi_lower:
            if self.rsi_trend != 1:
                self.rsi_trend = 1
                # RSI超卖，买入信号
                if self.pos <= 0:
                    if self.pos < 0:
                        self.cover(bar.close_price + 5, abs(self.pos))
                    self.buy(bar.close_price + 5, 1)
                    
        elif self.rsi_value > self.rsi_upper:
            if self.rsi_trend != -1:
                self.rsi_trend = -1
                # RSI超买，卖出信号
                if self.pos >= 0:
                    if self.pos > 0:
                        self.sell(bar.close_price - 5, abs(self.pos))
                    self.short(bar.close_price - 5, 1)
        
        self.put_event()

class BollingerStrategy(CtaTemplate):
    """布林带策略示例"""
    
    author = "DAOTrader"
    
    # 策略参数
    bb_window = 20
    bb_dev = 2.0
    
    # 策略变量
    bb_upper = 0.0
    bb_middle = 0.0
    bb_lower = 0.0
    bb_trend = 0
    
    parameters = ["bb_window", "bb_dev"]
    variables = ["bb_upper", "bb_middle", "bb_lower", "bb_trend"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        self.am = ArrayManager()
        
    def on_init(self):
        """策略初始化"""
        self.write_log("布林带策略初始化")
        self.load_bar(10)
        
    def on_start(self):
        """策略启动"""
        self.write_log("布林带策略启动")
        
    def on_stop(self):
        """策略停止"""
        self.write_log("布林带策略停止")
        
    def on_bar(self, bar: BarData):
        """K线数据推送"""
        self.am.update_bar(bar)
        if not self.am.inited:
            return
            
        # 计算布林带指标
        if talib is not None:
            self.bb_upper, self.bb_middle, self.bb_lower = talib.BBANDS(
                self.am.close, self.bb_window, self.bb_dev, self.bb_dev
            )
            
            self.bb_upper = self.bb_upper[-1]
            self.bb_middle = self.bb_middle[-1]
            self.bb_lower = self.bb_lower[-1]
        else:
            # 纯Python计算布林带
            if len(self.am.close) >= self.bb_window:
                recent_prices = self.am.close[-self.bb_window:]
                self.bb_middle = sum(recent_prices) / len(recent_prices)
                std_dev = (sum((x - self.bb_middle) ** 2 for x in recent_prices) / len(recent_prices)) ** 0.5
                self.bb_upper = self.bb_middle + self.bb_dev * std_dev
                self.bb_lower = self.bb_middle - self.bb_dev * std_dev
            else:
                self.bb_upper = bar.close_price
                self.bb_middle = bar.close_price
                self.bb_lower = bar.close_price
        
        # 布林带交易信号
        if bar.close_price <= self.bb_lower:
            if self.bb_trend != 1:
                self.bb_trend = 1
                # 价格触及下轨，买入信号
                if self.pos <= 0:
                    if self.pos < 0:
                        self.cover(bar.close_price + 5, abs(self.pos))
                    self.buy(bar.close_price + 5, 1)
                    
        elif bar.close_price >= self.bb_upper:
            if self.bb_trend != -1:
                self.bb_trend = -1
                # 价格触及上轨，卖出信号
                if self.pos >= 0:
                    if self.pos > 0:
                        self.sell(bar.close_price - 5, abs(self.pos))
                    self.short(bar.close_price - 5, 1)
        
        self.put_event()

class StrategyManager:
    """策略管理器"""
    
    def __init__(self):
        self.strategies = {
            "DualMA": DualMAStrategy,
            "RSI": RSIStrategy,
            "Bollinger": BollingerStrategy
        }
        
        # 策略默认参数
        self.default_settings = {
            "DualMA": {
                "fast_window": 10,
                "slow_window": 20
            },
            "RSI": {
                "rsi_window": 14,
                "rsi_upper": 70,
                "rsi_lower": 30
            },
            "Bollinger": {
                "bb_window": 20,
                "bb_dev": 2.0
            }
        }
    
    def get_strategy_class(self, name: str) -> Type[CtaTemplate]:
        """获取策略类
        
        Args:
            name: 策略名称
            
        Returns:
            策略类
        """
        if name not in self.strategies:
            raise ValueError(f"策略 {name} 不存在")
        
        return self.strategies[name]
    
    def get_strategy_list(self) -> List[str]:
        """获取策略列表
        
        Returns:
            策略名称列表
        """
        return list(self.strategies.keys())
    
    def get_strategy_info(self, name: str) -> Dict[str, Any]:
        """获取策略信息
        
        Args:
            name: 策略名称
            
        Returns:
            策略信息字典
        """
        if name not in self.strategies:
            raise ValueError(f"策略 {name} 不存在")
        
        strategy_class = self.strategies[name]
        
        return {
            "name": name,
            "author": getattr(strategy_class, 'author', 'Unknown'),
            "parameters": getattr(strategy_class, 'parameters', []),
            "variables": getattr(strategy_class, 'variables', []),
            "default_setting": self.default_settings.get(name, {}),
            "description": strategy_class.__doc__ or "无描述"
        }
    
    def validate_strategy_setting(self, strategy_name: str, setting: Dict[str, Any]) -> Dict[str, Any]:
        """验证策略参数
        
        Args:
            strategy_name: 策略名称
            setting: 策略参数设置
            
        Returns:
            验证结果字典
        """
        if strategy_name not in self.strategies:
            return {
                "valid": False,
                "error": f"策略 {strategy_name} 不存在"
            }
        
        strategy_class = self.strategies[strategy_name]
        parameters = getattr(strategy_class, 'parameters', [])
        
        # 检查必需参数
        missing_params = []
        for param in parameters:
            if param not in setting:
                missing_params.append(param)
        
        if missing_params:
            return {
                "valid": False,
                "error": f"缺少必需参数: {', '.join(missing_params)}"
            }
        
        # 参数类型和范围验证
        validation_rules = self._get_validation_rules(strategy_name)
        
        for param, value in setting.items():
            if param in validation_rules:
                rule = validation_rules[param]
                
                # 类型检查
                if 'type' in rule and not isinstance(value, rule['type']):
                    return {
                        "valid": False,
                        "error": f"参数 {param} 类型错误，期望 {rule['type'].__name__}，实际 {type(value).__name__}"
                    }
                
                # 范围检查
                if 'min' in rule and value < rule['min']:
                    return {
                        "valid": False,
                        "error": f"参数 {param} 值 {value} 小于最小值 {rule['min']}"
                    }
                
                if 'max' in rule and value > rule['max']:
                    return {
                        "valid": False,
                        "error": f"参数 {param} 值 {value} 大于最大值 {rule['max']}"
                    }
        
        return {
            "valid": True,
            "error": None
        }
    
    def _get_validation_rules(self, strategy_name: str) -> Dict[str, Dict[str, Any]]:
        """获取参数验证规则
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            验证规则字典
        """
        rules = {
            "DualMA": {
                "fast_window": {"type": int, "min": 1, "max": 100},
                "slow_window": {"type": int, "min": 1, "max": 200}
            },
            "RSI": {
                "rsi_window": {"type": int, "min": 2, "max": 100},
                "rsi_upper": {"type": (int, float), "min": 50, "max": 100},
                "rsi_lower": {"type": (int, float), "min": 0, "max": 50}
            },
            "Bollinger": {
                "bb_window": {"type": int, "min": 2, "max": 100},
                "bb_dev": {"type": (int, float), "min": 0.1, "max": 5.0}
            }
        }
        
        return rules.get(strategy_name, {})
    
    def get_default_setting(self, strategy_name: str) -> Dict[str, Any]:
        """获取策略默认参数
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            默认参数字典
        """
        return self.default_settings.get(strategy_name, {})
    
    def add_strategy(self, name: str, strategy_class: Type[CtaTemplate], 
                    default_setting: Dict[str, Any] = None):
        """添加自定义策略
        
        Args:
            name: 策略名称
            strategy_class: 策略类
            default_setting: 默认参数设置
        """
        self.strategies[name] = strategy_class
        if default_setting:
            self.default_settings[name] = default_setting
    
    def remove_strategy(self, name: str):
        """移除策略
        
        Args:
            name: 策略名称
        """
        if name in self.strategies:
            del self.strategies[name]
        if name in self.default_settings:
            del self.default_settings[name]

    # ---- v2.1 API helpers for backend/main.py ----
    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Return detailed info for all strategies.

        Provides name, parameters, defaults, and description for each strategy.
        """
        result: List[Dict[str, Any]] = []
        for name in self.get_strategy_list():
            info = self.get_strategy_info(name)
            result.append({
                "name": name,
                "parameters": info.get("parameters", []),
                "default_setting": info.get("default_setting", {}),
                "description": info.get("description", "")
            })
        return result

    def has_strategy(self, name: str) -> bool:
        """Check if a strategy exists by name."""
        return name in self.strategies

    def validate_strategy_params(self, strategy_name: str, setting: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper with naming expected by API; normalizes keys.

        Returns a dict with keys: {'valid': bool, 'message': str|None}
        """
        result = self.validate_strategy_setting(strategy_name, setting)
        if result.get("valid"):
            return {"valid": True, "message": None}
        return {"valid": False, "message": result.get("error")}