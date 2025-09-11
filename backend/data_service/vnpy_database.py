# DAOTrader v2.1 VNPY数据库操作模块
# 基于VNPY框架的数据库操作封装

import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
from vnpy.trader.object import BarData, Exchange, Interval
from vnpy.trader.constant import Exchange as VnpyExchange, Interval as VnpyInterval
from vnpy.trader.database import BaseDatabase, get_database
from vnpy.trader.utility import extract_vt_symbol


class VnpyDatabaseManager:
    """VNPY数据库管理器"""
    
    def __init__(self, db_path: str = None):
        self.logger = logging.getLogger(__name__)
        
        # 设置数据库路径 - 强制使用内存数据库避免I/O错误
        if db_path == ":memory:":
            self.db_path = ":memory:"
        else:
            # 临时使用内存数据库避免磁盘I/O问题
            self.db_path = ":memory:"
            self.logger.warning("由于磁盘I/O问题，强制使用内存数据库")
        
        # 确保数据目录存在
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            # 测试写入权限
            test_file = self.db_path.parent / "test_write.tmp"
            test_file.touch()
            test_file.unlink()
            self.logger.info(f"数据库目录权限检查通过: {self.db_path.parent}")
        except Exception as e:
            self.logger.error(f"数据库目录权限检查失败: {e}")
            # 使用临时目录作为备选
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "daotrader"
            temp_dir.mkdir(exist_ok=True)
            self.db_path = temp_dir / "vnpy_data.db"
            self.logger.warning(f"使用临时目录: {self.db_path}")
        
        # 初始化数据库连接
        self.database = None
        self._init_database()
        
        # 初始化数据表
        self._init_tables()
    
    def _init_database(self):
        """初始化数据库连接"""
        try:
            # 使用VNPY的数据库管理器
            from vnpy.trader.setting import SETTINGS
            
            # 设置数据库配置
            SETTINGS["database.driver"] = "sqlite"
            SETTINGS["database.database"] = str(self.db_path)
            
            # 获取数据库实例
            self.database = get_database()
            
            self.logger.info(f"数据库初始化成功: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {str(e)}")
            # 降级使用直接SQLite连接
            self._init_sqlite_fallback()
    
    def _init_sqlite_fallback(self):
        """降级SQLite连接初始化"""
        try:
            # 首先尝试连接到文件数据库
            try:
                self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
                # 测试数据库是否可写
                self.conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER)")
                self.conn.execute("DROP TABLE test_table")
                self.conn.commit()
                self.logger.info(f"SQLite文件数据库连接成功: {self.db_path}")
            except Exception as file_db_error:
                self.logger.warning(f"文件数据库连接失败: {file_db_error}，使用内存数据库")
                # 使用内存数据库作为备选
                self.conn = sqlite3.connect(":memory:", check_same_thread=False)
                self.logger.info("使用SQLite内存数据库")
            
            # 设置SQLite优化参数
            self.conn.execute("PRAGMA synchronous=NORMAL")
            self.conn.execute("PRAGMA cache_size=10000")
            self.conn.execute("PRAGMA temp_store=MEMORY")
            
        except Exception as e:
            self.logger.error(f"SQLite连接失败: {str(e)}")
            raise e
    
    def _init_tables(self):
        """初始化数据表"""
        try:
            if self.database:
                # VNPY会自动创建表结构
                self.logger.info("使用VNPY数据库表结构")
            else:
                # 手动创建表结构
                self._create_tables_manual()
                
        except Exception as e:
            self.logger.error(f"数据表初始化失败: {str(e)}")
    
    def _create_tables_manual(self):
        """手动创建数据表"""
        try:
            # 创建K线数据表
            create_bar_table = """
            CREATE TABLE IF NOT EXISTS dbbardata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                exchange TEXT NOT NULL,
                datetime TIMESTAMP NOT NULL,
                interval TEXT NOT NULL,
                volume REAL NOT NULL,
                turnover REAL NOT NULL,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, exchange, datetime, interval)
            )
            """
            
            # 创建索引
            create_bar_index = """
            CREATE INDEX IF NOT EXISTS idx_bar_symbol_exchange_datetime 
            ON dbbardata(symbol, exchange, datetime)
            """
            
            create_bar_index2 = """
            CREATE INDEX IF NOT EXISTS idx_bar_datetime 
            ON dbbardata(datetime)
            """
            
            self.conn.execute(create_bar_table)
            self.conn.execute(create_bar_index)
            self.conn.execute(create_bar_index2)
            self.conn.commit()
            
            self.logger.info("手动创建数据表成功")
            
        except Exception as e:
            self.logger.error(f"手动创建数据表失败: {str(e)}")
            raise e
    
    def save_bar_data(self, bars: List[BarData]) -> bool:
        """保存K线数据
        
        Args:
            bars: BarData对象列表
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if not bars:
                self.logger.warning("没有数据需要保存")
                return True
            
            self.logger.info(f"开始保存K线数据: {len(bars)} 条")
            
            if self.database:
                # 使用VNPY数据库
                for bar in bars:
                    self.database.save_bar_data([bar])
            else:
                # 使用SQLite直接保存
                self._save_bars_sqlite(bars)
            
            self.logger.info(f"K线数据保存成功: {len(bars)} 条")
            return True
            
        except Exception as e:
            self.logger.error(f"保存K线数据失败: {str(e)}")
            return False
    
    def _save_bars_sqlite(self, bars: List[BarData]):
        """使用SQLite直接保存K线数据"""
        try:
            data_to_insert = []
            
            for bar in bars:
                # 处理datetime对象，确保转换为Python datetime
                if hasattr(bar.datetime, 'to_pydatetime'):
                    # Pandas Timestamp
                    datetime_obj = bar.datetime.to_pydatetime()
                elif hasattr(bar.datetime, 'replace') and hasattr(bar.datetime, 'tzinfo'):
                    # Python datetime with timezone
                    datetime_obj = bar.datetime.replace(tzinfo=None) if bar.datetime.tzinfo else bar.datetime
                else:
                    # 其他类型，尝试直接使用
                    datetime_obj = bar.datetime
                
                data_to_insert.append((
                    bar.symbol,
                    bar.exchange.value,
                    datetime_obj,
                    bar.interval.value,
                    bar.volume,
                    bar.turnover,
                    bar.open_price,
                    bar.high_price,
                    bar.low_price,
                    bar.close_price
                ))
            
            # 批量插入，忽略重复数据
            insert_sql = """
            INSERT OR IGNORE INTO dbbardata 
            (symbol, exchange, datetime, interval, volume, turnover, 
             open_price, high_price, low_price, close_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.conn.executemany(insert_sql, data_to_insert)
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"SQLite保存数据失败: {str(e)}")
            raise e
    
    def load_bar_data(self, symbol: str, exchange: VnpyExchange, 
                     interval: VnpyInterval, start: datetime = None, 
                     end: datetime = None) -> List[BarData]:
        """加载K线数据
        
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
            # 处理exchange参数，确保是枚举类型
            if isinstance(exchange, str):
                exchange = VnpyExchange(exchange)
            
            self.logger.info(f"加载K线数据: {symbol}.{exchange.value}, {interval.value}")
            
            if self.database:
                # 使用VNPY数据库
                bars = self.database.load_bar_data(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    start=start,
                    end=end
                )
            else:
                # 使用SQLite直接查询
                bars = self._load_bars_sqlite(symbol, exchange, interval, start, end)
            
            self.logger.info(f"加载K线数据成功: {len(bars)} 条")
            return bars
            
        except Exception as e:
            self.logger.error(f"加载K线数据失败: {str(e)}")
            return []
    
    def _load_bars_sqlite(self, symbol: str, exchange: VnpyExchange, 
                         interval: VnpyInterval, start: datetime = None, 
                         end: datetime = None) -> List[BarData]:
        """使用SQLite直接查询K线数据"""
        try:
            # 构建查询SQL
            sql = """
            SELECT symbol, exchange, datetime, interval, volume, turnover,
                   open_price, high_price, low_price, close_price
            FROM dbbardata 
            WHERE symbol = ? AND exchange = ? AND interval = ?
            """
            
            params = [symbol, exchange.value, interval.value]
            
            if start:
                sql += " AND datetime >= ?"
                # 将Pandas Timestamp转换为Python datetime对象
                start_dt = start.to_pydatetime() if hasattr(start, 'to_pydatetime') else start
                params.append(start_dt)
            
            if end:
                sql += " AND datetime <= ?"
                # 将Pandas Timestamp转换为Python datetime对象
                end_dt = end.to_pydatetime() if hasattr(end, 'to_pydatetime') else end
                params.append(end_dt)
            
            sql += " ORDER BY datetime"
            
            # 执行查询
            cursor = self.conn.execute(sql, params)
            rows = cursor.fetchall()
            
            # 转换为BarData对象
            bars = []
            for row in rows:
                bar = BarData(
                    symbol=row[0],
                    exchange=VnpyExchange(row[1]),
                    datetime=pd.to_datetime(row[2]),
                    interval=VnpyInterval(row[3]),
                    volume=row[4],
                    turnover=row[5],
                    open_price=row[6],
                    high_price=row[7],
                    low_price=row[8],
                    close_price=row[9],
                    gateway_name="database"
                )
                bars.append(bar)
            
            return bars
            
        except Exception as e:
            self.logger.error(f"SQLite查询数据失败: {str(e)}")
            return []
    
    def get_bar_overview(self) -> List[Dict[str, Any]]:
        """获取数据概览
        
        Returns:
            List[Dict]: 数据概览信息
        """
        try:
            if self.database:
                # 使用VNPY数据库
                overview = self.database.get_bar_overview()
            else:
                # 使用SQLite直接查询
                overview = self._get_overview_sqlite()
            
            self.logger.info(f"获取数据概览成功: {len(overview)} 个品种")
            return overview
            
        except Exception as e:
            self.logger.error(f"获取数据概览失败: {str(e)}")
            return []
    
    def _get_overview_sqlite(self) -> List[Dict[str, Any]]:
        """使用SQLite获取数据概览"""
        try:
            sql = """
            SELECT symbol, exchange, interval, 
                   COUNT(*) as count,
                   MIN(datetime) as start_date,
                   MAX(datetime) as end_date
            FROM dbbardata 
            GROUP BY symbol, exchange, interval
            ORDER BY symbol, exchange, interval
            """
            
            cursor = self.conn.execute(sql)
            rows = cursor.fetchall()
            
            overview = []
            for row in rows:
                overview.append({
                    'symbol': row[0],
                    'exchange': row[1],
                    'interval': row[2],
                    'count': row[3],
                    'start': pd.to_datetime(row[4]),
                    'end': pd.to_datetime(row[5])
                })
            
            return overview
            
        except Exception as e:
            self.logger.error(f"SQLite获取概览失败: {str(e)}")
            return []
    
    def delete_bar_data(self, symbol: str, exchange: VnpyExchange, 
                       interval: VnpyInterval) -> bool:
        """删除K线数据
        
        Args:
            symbol: 品种代码
            exchange: 交易所
            interval: 时间周期
            
        Returns:
            bool: 删除是否成功
        """
        try:
            self.logger.info(f"删除K线数据: {symbol}.{exchange.value}, {interval.value}")
            
            if self.database:
                # 使用VNPY数据库
                self.database.delete_bar_data(symbol, exchange, interval)
            else:
                # 使用SQLite直接删除
                sql = "DELETE FROM dbbardata WHERE symbol = ? AND exchange = ? AND interval = ?"
                self.conn.execute(sql, (symbol, exchange.value, interval.value))
                self.conn.commit()
            
            self.logger.info(f"删除K线数据成功: {symbol}.{exchange.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"删除K线数据失败: {str(e)}")
            return False
    
    def get_newest_bar_data(self, symbol: str, exchange: VnpyExchange, 
                           interval: VnpyInterval) -> Optional[BarData]:
        """获取最新的K线数据
        
        Args:
            symbol: 品种代码
            exchange: 交易所
            interval: 时间周期
            
        Returns:
            Optional[BarData]: 最新的K线数据
        """
        try:
            if self.database:
                # 使用VNPY数据库
                bars = self.database.load_bar_data(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    start=None,
                    end=None
                )
                return bars[-1] if bars else None
            else:
                # 使用SQLite直接查询
                sql = """
                SELECT symbol, exchange, datetime, interval, volume, turnover,
                       open_price, high_price, low_price, close_price
                FROM dbbardata 
                WHERE symbol = ? AND exchange = ? AND interval = ?
                ORDER BY datetime DESC
                LIMIT 1
                """
                
                cursor = self.conn.execute(sql, (symbol, exchange.value, interval.value))
                row = cursor.fetchone()
                
                if row:
                    return BarData(
                        symbol=row[0],
                        exchange=VnpyExchange(row[1]),
                        datetime=pd.to_datetime(row[2]),
                        interval=VnpyInterval(row[3]),
                        volume=row[4],
                        turnover=row[5],
                        open_price=row[6],
                        high_price=row[7],
                        low_price=row[8],
                        close_price=row[9],
                        gateway_name="database"
                    )
                
                return None
            
        except Exception as e:
            self.logger.error(f"获取最新K线数据失败: {str(e)}")
            return None
    
    def get_bar_count(self, symbol: str = None, exchange: VnpyExchange = None, 
                     interval: VnpyInterval = None) -> int:
        """获取K线数据数量
        
        Args:
            symbol: 品种代码（可选）
            exchange: 交易所（可选）
            interval: 时间周期（可选）
            
        Returns:
            int: 数据数量
        """
        try:
            if self.database:
                # 使用VNPY数据库（需要自定义实现）
                sql = "SELECT COUNT(*) FROM dbbardata WHERE 1=1"
                params = []
                
                if symbol:
                    sql += " AND symbol = ?"
                    params.append(symbol)
                
                if exchange:
                    sql += " AND exchange = ?"
                    params.append(exchange.value)
                
                if interval:
                    sql += " AND interval = ?"
                    params.append(interval.value)
                
                # 这里需要直接访问数据库连接
                # 暂时使用SQLite方式
                return self._get_count_sqlite(symbol, exchange, interval)
            else:
                return self._get_count_sqlite(symbol, exchange, interval)
            
        except Exception as e:
            self.logger.error(f"获取数据数量失败: {str(e)}")
            return 0
    
    def _get_count_sqlite(self, symbol: str = None, exchange: VnpyExchange = None, 
                         interval: VnpyInterval = None) -> int:
        """使用SQLite获取数据数量"""
        try:
            sql = "SELECT COUNT(*) FROM dbbardata WHERE 1=1"
            params = []
            
            if symbol:
                sql += " AND symbol = ?"
                params.append(symbol)
            
            if exchange:
                sql += " AND exchange = ?"
                params.append(exchange.value)
            
            if interval:
                sql += " AND interval = ?"
                params.append(interval.value)
            
            cursor = self.conn.execute(sql, params)
            count = cursor.fetchone()[0]
            
            return count
            
        except Exception as e:
            self.logger.error(f"SQLite获取数量失败: {str(e)}")
            return 0
    
    def close(self):
        """关闭数据库连接"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
            
            self.logger.info("数据库连接已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭数据库连接失败: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()