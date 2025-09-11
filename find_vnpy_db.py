#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from pathlib import Path
from vnpy.trader.database import get_database
from vnpy.trader.setting import SETTINGS

# 设置数据库配置
SETTINGS["database.driver"] = "sqlite"
SETTINGS["database.database"] = "./data/vnpy_data.db"

# 获取数据库实例
db = get_database()

# 检查当前目录下所有.db文件
print("=== 搜索所有.db文件 ===")
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".db"):
            db_path = os.path.join(root, file)
            size = os.path.getsize(db_path)
            print(f"找到数据库: {db_path} (大小: {size} 字节)")
            
            # 检查是否包含我们的测试数据
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 检查是否有dbbardata表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dbbardata'")
                if cursor.fetchone():
                    cursor.execute("SELECT COUNT(*) FROM dbbardata")
                    count = cursor.fetchone()[0]
                    print(f"  dbbardata记录数: {count}")
                    
                    if count > 0:
                        cursor.execute("SELECT symbol, exchange, datetime FROM dbbardata ORDER BY datetime DESC LIMIT 5")
                        records = cursor.fetchall()
                        print(f"  最新5条记录: {records}")
                
                conn.close()
            except Exception as e:
                print(f"  检查失败: {e}")

# 检查VNPY默认位置
print("\n=== 检查VNPY默认数据库位置 ===")
vnpy_home = os.path.expanduser("~/.vnpy")
if os.path.exists(vnpy_home):
    print(f"VNPY主目录存在: {vnpy_home}")
    for file in os.listdir(vnpy_home):
        if file.endswith(".db"):
            db_path = os.path.join(vnpy_home, file)
            size = os.path.getsize(db_path)
            print(f"  找到: {db_path} (大小: {size} 字节)")
else:
    print(f"VNPY主目录不存在: {vnpy_home}")

# 检查当前工作目录的database.db
default_db = "database.db"
if os.path.exists(default_db):
    size = os.path.getsize(default_db)
    print(f"\n找到默认数据库: {default_db} (大小: {size} 字节)")
    
    try:
        conn = sqlite3.connect(default_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"  表: {[t[0] for t in tables]}")
        
        if ('dbbardata',) in tables:
            cursor.execute("SELECT COUNT(*) FROM dbbardata")
            count = cursor.fetchone()[0]
            print(f"  dbbardata记录数: {count}")
            
            if count > 0:
                cursor.execute("SELECT symbol, exchange, datetime FROM dbbardata ORDER BY datetime DESC LIMIT 5")
                records = cursor.fetchall()
                print(f"  最新5条记录: {records}")
        
        conn.close()
    except Exception as e:
        print(f"  检查默认数据库失败: {e}")
else:
    print(f"\n默认数据库不存在: {default_db}")