#!/usr/bin/env python3
# 检查VNPY默认数据库中的数据

import sqlite3
import os

def check_vnpy_default_db():
    print("=== 检查VNPY默认数据库 ===")
    
    vnpy_db_path = r"C:\Users\Administrator\.vntrader\database.db"
    
    if not os.path.exists(vnpy_db_path):
        print(f"VNPY数据库文件不存在: {vnpy_db_path}")
        return
    
    try:
        conn = sqlite3.connect(vnpy_db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        print("\n=== 表结构 ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"表: {[t[0] for t in tables]}")
        
        # 检查dbbardata表
        if any('dbbardata' in str(t) for t in tables):
            print("\n=== dbbardata表信息 ===")
            
            # 总记录数
            cursor.execute("SELECT COUNT(*) FROM dbbardata")
            total_count = cursor.fetchone()[0]
            print(f"总记录数: {total_count}")
            
            # 检查最近的记录
            cursor.execute("SELECT * FROM dbbardata ORDER BY datetime DESC LIMIT 5")
            recent_records = cursor.fetchall()
            print(f"\n最近5条记录:")
            for i, record in enumerate(recent_records, 1):
                print(f"  {i}. {record}")
            
            # 检查所有symbol
            cursor.execute("SELECT DISTINCT symbol FROM dbbardata")
            symbols = cursor.fetchall()
            print(f"\n所有symbol: {[s[0] for s in symbols]}")
            
            # 检查DEBUG2509和RB2509
            for symbol in ['DEBUG2509', 'RB2509', 'COMMIT2509']:
                cursor.execute("SELECT COUNT(*) FROM dbbardata WHERE symbol = ?", (symbol,))
                count = cursor.fetchone()[0]
                print(f"{symbol}记录数: {count}")
                
                if count > 0:
                    cursor.execute("SELECT * FROM dbbardata WHERE symbol = ? LIMIT 3", (symbol,))
                    records = cursor.fetchall()
                    for j, record in enumerate(records, 1):
                        print(f"  {j}. {record}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_vnpy_default_db()