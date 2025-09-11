#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from pathlib import Path

# 检查VNPY数据库的实际位置
try:
    from vnpy.trader.database import get_database
    from vnpy.trader.setting import SETTINGS
    
    print("=== VNPY数据库配置检查 ===")
    print(f"数据库驱动: {SETTINGS.get('database.driver', 'Not Set')}")
    print(f"数据库路径: {SETTINGS.get('database.database', 'Not Set')}")
    print(f"数据库主机: {SETTINGS.get('database.host', 'Not Set')}")
    print(f"数据库端口: {SETTINGS.get('database.port', 'Not Set')}")
    
    # 获取数据库实例
    db = get_database()
    print(f"\n数据库实例类型: {type(db)}")
    
    # 如果是SQLite，尝试找到实际文件位置
    if hasattr(db, 'db_path'):
        print(f"数据库文件路径: {db.db_path}")
        if os.path.exists(db.db_path):
            print(f"文件存在，大小: {os.path.getsize(db.db_path)} 字节")
        else:
            print("文件不存在")
    
    # 检查可能的数据库位置
    possible_paths = [
        "./data/vnpy_data.db",
        "./vnpy_data.db", 
        os.path.expanduser("~/.vnpy/vnpy_data.db"),
        os.path.expanduser("~/vnpy_data.db"),
        "./temp/vnpy_data.db"
    ]
    
    print("\n=== 检查可能的数据库文件位置 ===")
    for path in possible_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"找到: {path} (大小: {size} 字节)")
            
            # 检查表内容
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"  表: {[t[0] for t in tables]}")
                
                if ('dbbardata',) in tables:
                    cursor.execute("SELECT COUNT(*) FROM dbbardata")
                    count = cursor.fetchone()[0]
                    print(f"  dbbardata记录数: {count}")
                    
                    if count > 0:
                        cursor.execute("SELECT symbol, exchange, datetime FROM dbbardata LIMIT 3")
                        records = cursor.fetchall()
                        print(f"  前3条记录: {records}")
                
                conn.close()
            except Exception as e:
                print(f"  检查表内容失败: {e}")
        else:
            print(f"不存在: {path}")
            
except Exception as e:
    print(f"检查VNPY数据库失败: {e}")
    import traceback
    traceback.print_exc()