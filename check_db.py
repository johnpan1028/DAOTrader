import sqlite3
import os

print('检查项目data目录数据库:')
db_path = './data/vnpy_data.db'
print(f'文件存在: {os.path.exists(db_path)}')

if os.path.exists(db_path):
    print(f'文件大小: {os.path.getsize(db_path)} 字节')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM dbbardata')
        count = cursor.fetchone()[0]
        print(f'记录数: {count}')
        
        if count > 0:
            cursor.execute('SELECT * FROM dbbardata LIMIT 3')
            records = cursor.fetchall()
            print('最新记录:')
            for record in records:
                print(record)
        
        conn.close()
    except Exception as e:
        print(f'数据库查询错误: {e}')
else:
    print('数据库文件不存在')