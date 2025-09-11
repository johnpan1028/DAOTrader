#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库监控脚本 - 实时监控数据下载情况
"""

import sqlite3
import os
import time
from pathlib import Path

def get_db_info(db_path):
    """获取数据库信息"""
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表列表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        info = {
            'file_size': os.path.getsize(db_path),
            'tables': tables,
            'records': {}
        }
        
        # 获取每个表的记录数
        for table in tables:
            if table != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                info['records'][table] = count
                
                # 如果是dbbardata表，获取最新的几条记录
                if table == 'dbbardata':
                    cursor.execute(f"SELECT symbol, exchange, datetime FROM {table} ORDER BY datetime DESC LIMIT 5")
                    latest_records = cursor.fetchall()
                    info['latest_records'] = latest_records
        
        conn.close()
        return info
        
    except Exception as e:
        return {'error': str(e)}

def monitor_databases():
    """监控多个可能的数据库位置"""
    # 可能的数据库位置
    possible_locations = [
        "./data/vnpy_data.db",
        "G:/SynologyDrive/项目/DAOTrader/data/vnpy_data.db",
        os.path.expanduser("~/AppData/Local/Temp/daotrader/vnpy_data.db"),
        "C:/Users/Administrator/AppData/Local/Temp/daotrader/vnpy_data.db",
        "./vnpy_data.db",
        "./backend/vnpy_data.db"
    ]
    
    print("=" * 60)
    print("DAOTrader 数据库监控器")
    print("=" * 60)
    print("监控数据库位置:")
    for i, loc in enumerate(possible_locations, 1):
        print(f"{i}. {loc}")
    print("\n按 Ctrl+C 停止监控\n")
    
    previous_states = {}
    
    try:
        while True:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检查数据库状态...")
            
            found_any = False
            
            for location in possible_locations:
                abs_path = os.path.abspath(location)
                info = get_db_info(abs_path)
                
                if info is not None:
                    found_any = True
                    
                    # 检查是否有变化
                    current_state = str(info)
                    if abs_path not in previous_states or previous_states[abs_path] != current_state:
                        print(f"\n📍 发现数据库: {abs_path}")
                        
                        if 'error' in info:
                            print(f"   ❌ 错误: {info['error']}")
                        else:
                            print(f"   📊 文件大小: {info['file_size']:,} 字节")
                            print(f"   📋 数据表: {', '.join(info['tables'])}")
                            
                            for table, count in info['records'].items():
                                print(f"   📈 {table}: {count} 条记录")
                            
                            # 显示最新记录
                            if 'latest_records' in info and info['latest_records']:
                                print("   🔄 最新数据:")
                                for record in info['latest_records']:
                                    print(f"      {record[0]} ({record[1]}) - {record[2]}")
                        
                        previous_states[abs_path] = current_state
                        print("   " + "="*50)
            
            if not found_any:
                print("   ❌ 未找到任何数据库文件")
            
            time.sleep(5)  # 每5秒检查一次
            
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")

if __name__ == "__main__":
    monitor_databases()