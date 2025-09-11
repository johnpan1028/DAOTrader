#!/usr/bin/env python3
# 调试VNPY数据库实际路径

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vnpy.trader.database import get_database
from vnpy.trader.setting import SETTINGS
from vnpy.trader.object import BarData, Exchange, Interval
from datetime import datetime
import sqlite3
import glob

def debug_vnpy_path():
    print("=== 调试VNPY数据库实际路径 ===")
    
    # 检查VNPY设置
    print("\n=== VNPY设置 ===")
    print(f"database.driver: {SETTINGS.get('database.driver', 'NOT SET')}")
    print(f"database.database: {SETTINGS.get('database.database', 'NOT SET')}")
    print(f"database.host: {SETTINGS.get('database.host', 'NOT SET')}")
    print(f"database.port: {SETTINGS.get('database.port', 'NOT SET')}")
    print(f"database.user: {SETTINGS.get('database.user', 'NOT SET')}")
    print(f"database.password: {SETTINGS.get('database.password', 'NOT SET')}")
    
    # 获取VNPY数据库实例
    print("\n=== VNPY数据库实例 ===")
    db = get_database()
    print(f"数据库类型: {type(db)}")
    print(f"数据库模块: {db.__class__.__module__}")
    
    # 检查数据库属性
    print("\n=== 数据库属性 ===")
    for attr in dir(db):
        if not attr.startswith('_') and not callable(getattr(db, attr)):
            try:
                value = getattr(db, attr)
                print(f"{attr}: {value}")
            except:
                print(f"{attr}: <无法访问>")
    
    # 检查私有属性中的路径信息
    print("\n=== 私有属性检查 ===")
    for attr in ['_engine', '_db_path', '_database_path', 'db_path', 'database_path']:
        if hasattr(db, attr):
            try:
                value = getattr(db, attr)
                print(f"{attr}: {value}")
                if hasattr(value, 'url'):
                    print(f"  -> url: {value.url}")
            except:
                print(f"{attr}: <无法访问>")
    
    # 创建测试数据并保存
    print("\n=== 测试数据保存 ===")
    test_bar = BarData(
        symbol="DEBUG2509",
        exchange=Exchange.SHFE,
        datetime=datetime(2024, 9, 19, 10, 30, 0),
        interval=Interval.DAILY,
        volume=1000.0,
        turnover=3237000.0,
        open_price=3237.0,
        high_price=3250.0,
        low_price=3230.0,
        close_price=3245.0,
        gateway_name="debug"
    )
    
    try:
        db.save_bar_data([test_bar])
        print("数据保存完成")
    except Exception as e:
        print(f"数据保存失败: {e}")
    
    # 搜索所有可能的数据库文件
    print("\n=== 搜索所有数据库文件 ===")
    search_patterns = [
        "**/*.db",
        "**/*.sqlite",
        "**/*.sqlite3"
    ]
    
    found_files = set()
    for pattern in search_patterns:
        try:
            files = glob.glob(pattern, recursive=True)
            found_files.update(files)
        except:
            pass
    
    print(f"找到的数据库文件: {len(found_files)} 个")
    for file_path in sorted(found_files):
        try:
            size = os.path.getsize(file_path)
            print(f"  {file_path} ({size} bytes)")
            
            # 检查是否包含dbbardata表
            try:
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dbbardata'")
                if cursor.fetchone():
                    cursor.execute("SELECT COUNT(*) FROM dbbardata")
                    count = cursor.fetchone()[0]
                    print(f"    -> 包含dbbardata表，记录数: {count}")
                    
                    if count > 0:
                        cursor.execute("SELECT DISTINCT symbol FROM dbbardata LIMIT 10")
                        symbols = [row[0] for row in cursor.fetchall()]
                        print(f"    -> symbols: {symbols}")
                conn.close()
            except:
                pass
                
        except Exception as e:
            print(f"  {file_path} (无法访问: {e})")
    
    # 检查VNPY默认路径
    print("\n=== 检查VNPY默认路径 ===")
    try:
        from vnpy.trader.utility import get_folder_path
        vnpy_folder = get_folder_path("")
        print(f"VNPY文件夹: {vnpy_folder}")
        
        # 检查该文件夹下的数据库文件
        if os.path.exists(vnpy_folder):
            for file in os.listdir(vnpy_folder):
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    file_path = os.path.join(vnpy_folder, file)
                    size = os.path.getsize(file_path)
                    print(f"  {file_path} ({size} bytes)")
    except Exception as e:
        print(f"获取VNPY文件夹失败: {e}")

if __name__ == "__main__":
    debug_vnpy_path()