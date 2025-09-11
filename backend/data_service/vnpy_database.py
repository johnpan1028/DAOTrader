# DAOTrader v2.1 VNPY数据库操作模块
# 完全基于VNPY框架，只负责配置数据路径

from typing import List
from datetime import datetime
import logging
import os
from pathlib import Path
from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange as VnpyExchange, Interval as VnpyInterval
from vnpy.trader.database import get_database


class VnpyDatabaseManager:
    """VNPY数据库管理器 - 完全依赖VNPY核心功能"""
    
    def __init__(self, db_path: str = None):
        self.logger = logging.getLogger(__name__)
        
        # 设置数据库路径
        if db_path:
            self.db_path = Path(db_path)
        else:
            # 默认使用项目data目录
            self.db_path = Path("./data/vnpy_data.db").resolve()
        
        # 确保数据目录存在
        os.makedirs(self.db_path.parent, exist_ok=True)
        self.logger.info(f"数据库路径: {self.db_path}")
        
        # 配置VNPY使用项目本地数据库
        self._configure_vnpy_database()
        
        # 获取VNPY数据库实例
        self.database = get_database()
        self.logger.info("VNPY数据库初始化成功")
    
    def _configure_vnpy_database(self):
        """配置VNPY使用项目本地数据库"""
        from vnpy.trader.setting import SETTINGS
        
        # 只修改数据库路径，其他交给VNPY处理
        SETTINGS["database.driver"] = "sqlite"
        SETTINGS["database.database"] = str(self.db_path)
        self.logger.info(f"配置VNPY数据库路径: {self.db_path}")
    
    def save_bar_data(self, bars: List[BarData]) -> bool:
        """保存K线数据 - 完全依赖VNPY
        
        Args:
            bars: K线数据列表
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if not bars:
                self.logger.warning("没有数据需要保存")
                return True
            
            self.logger.info(f"开始保存K线数据: {len(bars)} 条")
            
            # 完全依赖VNPY的保存功能，包括去重逻辑
            self.database.save_bar_data(bars)
            
            self.logger.info(f"K线数据保存成功: {len(bars)} 条")
            return True
            
        except Exception as e:
            self.logger.error(f"保存K线数据失败: {str(e)}")
            return False
    
    def load_bar_data(self, symbol: str, exchange: VnpyExchange, 
                     interval: VnpyInterval, start: datetime = None, 
                     end: datetime = None) -> List[BarData]:
        """加载K线数据 - 完全依赖VNPY
        
        Args:
            symbol: 品种代码
            exchange: 交易所
            interval: 时间周期
            start: 开始时间
            end: 结束时间
            
        Returns:
            List[BarData]: K线数据列表
        """
        try:
            self.logger.info(f"加载K线数据: {symbol}.{exchange.value}, {interval.value}")
            
            # 完全依赖VNPY的加载功能
            bars = self.database.load_bar_data(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start=start,
                end=end
            )
            
            self.logger.info(f"加载K线数据成功: {len(bars)} 条")
            return bars
            
        except Exception as e:
            self.logger.error(f"加载K线数据失败: {str(e)}")
            return []
    
    def get_bar_overview(self) -> dict:
        """获取数据概览 - 完全依赖VNPY
        
        Returns:
            dict: 数据概览信息
        """
        try:
            # 使用VNPY的数据库功能获取概览
            overview = self.database.get_bar_overview()
            return overview
            
        except Exception as e:
            self.logger.error(f"获取数据概览失败: {str(e)}")
            return {}
    
    def delete_bar_data(self, symbol: str, exchange: VnpyExchange, 
                       interval: VnpyInterval) -> bool:
        """删除K线数据 - 完全依赖VNPY
        
        Args:
            symbol: 品种代码
            exchange: 交易所
            interval: 时间周期
            
        Returns:
            bool: 删除是否成功
        """
        try:
            self.logger.info(f"删除K线数据: {symbol}.{exchange.value}, {interval.value}")
            
            # 完全依赖VNPY的删除功能
            self.database.delete_bar_data(symbol, exchange, interval)
            
            self.logger.info("K线数据删除成功")
            return True
            
        except Exception as e:
            self.logger.error(f"删除K线数据失败: {str(e)}")
            return False