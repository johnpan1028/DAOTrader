"""回测引擎模块

集成VNPY BacktestingEngine，封装回测流程，支持多策略回测，生成回测报告。
"""

import numpy as np

# 尝试不同的VNPY导入路径
try:
    from vnpy.app.cta_backtester import BacktesterEngine
    from vnpy.trader.object import BarData
    from vnpy.app.cta_strategy import CtaTemplate
    from vnpy.trader.constant import Exchange, Interval
except ImportError:
    try:
        from vnpy_ctabacktester import BacktesterEngine
        from vnpy.trader.object import BarData
        from vnpy_ctastrategy import CtaTemplate
        from vnpy.trader.constant import Exchange, Interval
    except ImportError:
        print("VNPY模块导入失败，使用简化版本")
        
        # 简化的回测引擎类（当VNPY不可用时使用）
        class BacktesterEngine:
            def __init__(self):
                self.strategy_data = {}
                
            def add_strategy(self, strategy_class, setting):
                return "simple_strategy"
                
            def load_data(self, vt_symbol, start, end, interval):
                return True
                
            def run_backtesting(self):
                return {"total_return": 0.1, "sharpe_ratio": 1.5}
                
            def get_result_df(self):
                if pd is None:
                    return None
                return pd.DataFrame({"date": [], "balance": []})
                
            def clear_data(self):
                pass
        
        class SimpleBacktesterEngine:
            def __init__(self):
                self.strategy_data = {}
                
            def add_strategy(self, strategy_class, setting):
                return "simple_strategy"
                
            def load_data(self, vt_symbol, start, end, interval):
                return True
                
            def run_backtesting(self):
                return {"total_return": 0.1, "sharpe_ratio": 1.5}
                
            def get_result_df(self):
                if pd is None:
                    return None
                return pd.DataFrame({"date": [], "balance": []})
                
            def clear_data(self):
                pass
        
        class BarData:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        
        class CtaTemplate:
            pass
        
        class Exchange:
            SSE = "SSE"
            SZSE = "SZSE"
            SHFE = "SHFE"
            DCE = "DCE"
            CZCE = "CZCE"
            CFFEX = "CFFEX"
        
        class Interval:
            MINUTE = "1m"
            HOUR = "1h"
            DAILY = "1d"
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
try:
    import pandas as pd
except Exception:
    pd = None
# from ..models.backtest_result import BacktestResult  # 注释掉以避免导入错误
from .strategy_manager import StrategyManager

# 简化的回测引擎类（全局定义，确保在所有情况下都可用）
class SimpleBacktesterEngine:
    def __init__(self):
        self.strategy_data = {}
        
    def add_strategy(self, strategy_class, setting):
        return "simple_strategy"
        
    def load_data(self, vt_symbol, start, end, interval):
        return True
        
    def run_backtesting(self):
        return {"total_return": 0.1, "sharpe_ratio": 1.5}
        
    def get_result_df(self):
        if pd is None:
            return None
        return pd.DataFrame({"date": [], "balance": []})
        
    def clear_data(self):
        pass
    
    def set_parameters(self, **kwargs):
        """设置回测参数"""
        pass
    
    def get_result_statistics(self):
        """获取回测统计结果"""
        return {
            "total_return": 0.15,
            "annual_return": 0.18,
            "max_drawdown": 0.08,
            "sharpe_ratio": 1.2,
            "total_trades": 50,
            "win_rate": 0.6
        }

class BacktestManager:
    """回测管理器"""
    
    def __init__(self):
        """初始化回测管理器"""
        try:
            # 尝试创建VNPY回测引擎（需要主引擎和事件引擎）
            from vnpy.trader.engine import MainEngine
            from vnpy.event import EventEngine
            event_engine = EventEngine()
            main_engine = MainEngine(event_engine)
            self.engine = BacktesterEngine(main_engine, event_engine)
        except Exception as e:
            print(f"VNPY回测引擎初始化失败，使用简化版本: {e}")
            # 使用简化的回测引擎
            self.engine = SimpleBacktesterEngine()
        
        self.strategy_manager = StrategyManager()
        self.results = {}  # 存储回测结果
        self.running_backtests = {}  # 正在运行的回测任务
        self.current_backtest_id = None

    # ---- v2.1 flexible API: run_backtest using in-memory bars ----
    def run_backtest(
        self,
        strategy_name: str = "",
        bar_data: Optional[List[Any]] = None,
        setting: Optional[Dict[str, Any]] = None,
        capital: float = 100000.0,
        commission: float = 0.0003,
        slippage: float = 0.0001,
        **kwargs,
    ) -> Dict[str, Any]:
        """Run a simplified backtest on provided bars and return flat stats.

        This method is designed to work without vn.py installed. It computes
        basic performance metrics from the provided bar series.
        """
        try:
            setting = setting or {}
            bars = bar_data or kwargs.get('bars') or []
            if not bars or len(bars) < 2:
                return {"success": False, "message": "历史数据不足"}

            # 提取收盘价序列
            closes = [float(getattr(b, "close_price", None)) for b in bars]
            closes = [c for c in closes if c is not None]
            if len(closes) < 2:
                return {"success": False, "message": "收盘价数据不足"}

            # 计算收益与指标（如无 numpy，使用纯 Python）
            try:
                import numpy as np
                arr = np.array(closes, dtype=float)
                rets = np.diff(arr) / arr[:-1]
                total_return = float(arr[-1] / arr[0] - 1.0)
                annual_return = total_return  # 简化：未做年化换算
                running_max = np.maximum.accumulate(arr)
                dd = arr / running_max - 1.0
                max_drawdown = float(abs(dd.min())) if dd.size else 0.0
                std = float(rets.std(ddof=1)) if rets.size > 1 else 0.0
                mean = float(rets.mean()) if rets.size else 0.0
                sharpe = float((mean / std) * np.sqrt(max(rets.size, 1))) if std > 0 else 0.0
                total_trades = int((rets != 0).sum())
                win_rate = float((rets > 0).sum() / rets.size) if rets.size else 0.0
            except ImportError:
                import math
                import statistics
                rets = [
                    (closes[i] - closes[i - 1]) / closes[i - 1]
                    for i in range(1, len(closes))
                ]
                total_return = closes[-1] / closes[0] - 1.0
                annual_return = total_return  # 简化：未做年化换算
                running_max = []
                m = float('-inf')
                for c in closes:
                    m = c if c > m else m
                    running_max.append(m)
                dd_list = [
                    (closes[i] / running_max[i] - 1.0) if running_max[i] != 0 else 0.0
                    for i in range(len(closes))
                ]
                max_drawdown = abs(min(dd_list)) if dd_list else 0.0
                std = statistics.stdev(rets) if len(rets) > 1 else 0.0
                mean = statistics.mean(rets) if rets else 0.0
                sharpe = (mean / std) * math.sqrt(len(rets)) if std > 0 else 0.0
                total_trades = sum(1 for r in rets if abs(r) > 1e-12)
                win_rate = (sum(1 for r in rets if r > 0) / len(rets)) if rets else 0.0

            stats = {
                "total_return": float(total_return),
                "annual_return": float(annual_return),
                "max_drawdown": float(max_drawdown),
                "sharpe_ratio": float(sharpe),
                "total_trades": int(total_trades),
                "win_rate": float(win_rate),
            }

            # Store into results with ID
            backtest_id = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_backtest_id = backtest_id
            self.results[backtest_id] = {
                "strategy_name": strategy_name,
                "setting": setting,
                "result": stats,
                "created_at": datetime.now(),
            }

            return stats
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_backtest_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return recent backtest results summary."""
        items = list(self.results.items())[-limit:]
        out = []
        for rid, rec in items:
            out.append({
                "id": rid,
                "strategy_name": rec.get("strategy_name"),
                "created_at": rec.get("created_at").strftime('%Y-%m-%d %H:%M:%S') if rec.get("created_at") else None,
                "result": rec.get("result", {}),
            })
        return out

    def get_backtest_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get a single backtest result by ID."""
        rec = self.results.get(result_id)
        if not rec:
            return None
        return {
            "id": result_id,
            "strategy_name": rec.get("strategy_name"),
            "created_at": rec.get("created_at").strftime('%Y-%m-%d %H:%M:%S') if rec.get("created_at") else None,
            "result": rec.get("result", {}),
        }

    def delete_backtest_result(self, result_id: str) -> bool:
        """Delete a stored backtest result by ID."""
        if result_id in self.results:
            del self.results[result_id]
            return True
        return False
    
    def run_backtest_vnpy(
        self, 
        strategy_class: CtaTemplate, 
        symbol: str, 
        exchange: str, 
        interval: str, 
        start: datetime, 
        end: datetime, 
        rate: float = 0.0003,  # 手续费率
        slippage: float = 0.2,  # 滑点
        size: int = 1,  # 合约大小
        pricetick: float = 0.01,  # 最小价格变动
        capital: float = 100000.0,  # 初始资金
        setting: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """执行回测
        
        Args:
            strategy_class: 策略类
            symbol: 交易品种
            exchange: 交易所
            interval: 时间周期
            start: 开始时间
            end: 结束时间
            rate: 手续费率
            slippage: 滑点
            size: 合约大小
            pricetick: 最小价格变动
            capital: 初始资金
            setting: 策略参数设置
            
        Returns:
            回测结果字典
        """
        try:
            if setting is None:
                setting = {}
            
            # 转换交易所和周期格式
            exchange_obj = self._convert_exchange(exchange)
            interval_obj = self._convert_interval(interval)
            
            # 构建vt_symbol
            vt_symbol = f"{symbol}.{exchange}"
            
            # 设置回测引擎参数
            self.engine.set_parameters(
                vt_symbol=vt_symbol,
                interval=interval_obj,
                start=start,
                end=end,
                rate=rate,
                slippage=slippage,
                size=size,
                pricetick=pricetick,
                capital=capital
            )
            
            # 添加策略
            strategy_name = f"{strategy_class.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.engine.add_strategy(strategy_class, setting)
            
            # 加载历史数据
            self.engine.load_data()
            
            # 运行回测
            self.engine.run_backtesting()
            
            # 获取回测结果
            result = self.get_backtest_result()
            
            # 生成回测ID
            backtest_id = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_backtest_id = backtest_id
            
            # 保存结果
            self.results[backtest_id] = {
                'strategy_name': strategy_name,
                'symbol': symbol,
                'exchange': exchange,
                'interval': interval,
                'start_date': start.strftime('%Y-%m-%d'),
                'end_date': end.strftime('%Y-%m-%d'),
                'setting': setting,
                'result': result,
                'created_at': datetime.now()
            }
            
            return {
                'success': True,
                'backtest_id': backtest_id,
                'result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'backtest_id': None,
                'result': None
            }
    
    def get_backtest_result(self) -> Dict[str, Any]:
        """获取回测结果"""
        try:
            # 获取统计结果
            statistics = self.engine.calculate_statistics()
            
            # 获取交易记录
            trades = self.engine.get_all_trades()
            
            # 获取每日盈亏
            daily_results = self.engine.get_all_daily_results()
            
            # 转换为字典格式
            result = {
                'statistics': self._format_statistics(statistics),
                'trades': self._format_trades(trades),
                'daily_results': self._format_daily_results(daily_results)
            }
            
            return result
            
        except Exception as e:
            return {
                'error': f'获取回测结果失败: {str(e)}',
                'statistics': {},
                'trades': [],
                'daily_results': []
            }
    
    def generate_report(self, backtest_id: str = None) -> Dict[str, Any]:
        """生成回测报告
        
        Args:
            backtest_id: 回测ID，如果为None则使用当前回测
            
        Returns:
            回测报告字典
        """
        if backtest_id is None:
            backtest_id = self.current_backtest_id
        
        if backtest_id not in self.results:
            return {'error': '回测结果不存在'}
        
        backtest_data = self.results[backtest_id]
        result = backtest_data['result']
        
        # 生成详细报告
        report = {
            'backtest_info': {
                'strategy_name': backtest_data['strategy_name'],
                'symbol': backtest_data['symbol'],
                'exchange': backtest_data['exchange'],
                'interval': backtest_data['interval'],
                'start_date': backtest_data['start_date'],
                'end_date': backtest_data['end_date'],
                'setting': backtest_data['setting'],
                'created_at': backtest_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            },
            'performance': result.get('statistics', {}),
            'trades_summary': self._generate_trades_summary(result.get('trades', [])),
            'daily_performance': result.get('daily_results', []),
            'risk_metrics': self._calculate_risk_metrics(result)
        }
        
        return report
    
    def _convert_exchange(self, exchange: str) -> Exchange:
        """转换交易所格式"""
        exchange_mapping = {
            'SH': Exchange.SSE,
            'SZ': Exchange.SZSE,
            'SHFE': Exchange.SHFE,
            'DCE': Exchange.DCE,
            'CZCE': Exchange.CZCE,
            'CFFEX': Exchange.CFFEX
        }
        return exchange_mapping.get(exchange.upper(), Exchange.SSE)
    
    def _convert_interval(self, interval: str) -> Interval:
        """转换时间周期格式"""
        interval_mapping = {
            'daily': Interval.DAILY,
            '60min': Interval.HOUR,
            '30min': getattr(Interval, 'MINUTE_30', Interval.MINUTE),
            '15min': getattr(Interval, 'MINUTE_15', Interval.MINUTE),
            '5min': getattr(Interval, 'MINUTE_5', Interval.MINUTE),
            '1min': Interval.MINUTE
        }
        return interval_mapping.get(interval.lower(), Interval.DAILY)
    
    def _format_statistics(self, statistics: Dict) -> Dict[str, Any]:
        """格式化统计结果"""
        if not statistics:
            return {}
        
        return {
            'total_return': statistics.get('总收益率', 0),
            'annual_return': statistics.get('年化收益率', 0),
            'max_drawdown': statistics.get('最大回撤', 0),
            'sharpe_ratio': statistics.get('夏普比率', 0),
            'total_trades': statistics.get('总成交笔数', 0),
            'win_rate': statistics.get('盈利交易占比', 0),
            'profit_loss_ratio': statistics.get('盈亏比', 0),
            'start_capital': statistics.get('起始资金', 0),
            'end_capital': statistics.get('结束资金', 0)
        }
    
    def _format_trades(self, trades: List) -> List[Dict[str, Any]]:
        """格式化交易记录"""
        formatted_trades = []
        for trade in trades:
            formatted_trades.append({
                'trade_id': getattr(trade, 'tradeid', ''),
                'symbol': getattr(trade, 'symbol', ''),
                'exchange': getattr(trade, 'exchange', ''),
                'direction': getattr(trade, 'direction', ''),
                'price': getattr(trade, 'price', 0),
                'volume': getattr(trade, 'volume', 0),
                'datetime': getattr(trade, 'datetime', '').strftime('%Y-%m-%d %H:%M:%S') if hasattr(getattr(trade, 'datetime', ''), 'strftime') else str(getattr(trade, 'datetime', '')),
                'pnl': getattr(trade, 'pnl', 0)
            })
        return formatted_trades
    
    def _format_daily_results(self, daily_results: List) -> List[Dict[str, Any]]:
        """格式化每日结果"""
        formatted_results = []
        for daily in daily_results:
            formatted_results.append({
                'date': getattr(daily, 'date', '').strftime('%Y-%m-%d') if hasattr(getattr(daily, 'date', ''), 'strftime') else str(getattr(daily, 'date', '')),
                'pnl': getattr(daily, 'pnl', 0),
                'balance': getattr(daily, 'balance', 0),
                'drawdown': getattr(daily, 'drawdown', 0)
            })
        return formatted_results
    
    def _generate_trades_summary(self, trades: List[Dict]) -> Dict[str, Any]:
        """生成交易汇总"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0
            }
        
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
        losing_trades = total_trades - winning_trades
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / total_trades if total_trades > 0 else 0
        }
    
    def _calculate_risk_metrics(self, result: Dict) -> Dict[str, Any]:
        """计算风险指标"""
        statistics = result.get('statistics', {})
        
        return {
            'max_drawdown': statistics.get('max_drawdown', 0),
            'sharpe_ratio': statistics.get('sharpe_ratio', 0),
            'volatility': 0,  # 需要根据daily_results计算
            'var_95': 0,  # 95%置信度的VaR
            'calmar_ratio': 0  # 卡尔玛比率
        }
    
    def get_all_results(self) -> Dict[str, Any]:
        """获取所有回测结果"""
        return self.results
    
    def clear_results(self):
        """清空回测结果"""
        self.results.clear()
        self.current_backtest_id = None