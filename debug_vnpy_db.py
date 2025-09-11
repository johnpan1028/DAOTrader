#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from vnpy.trader.database import get_database
from vnpy.trader.setting import SETTINGS

# 设置数据库配置
SETTINGS["database.driver"] = "sqlite"
SETTINGS["database.database"] = "./data/vnpy_data.db"

print("=== 设置后的VNPY数据库配置 ===")
print(f"数据库驱动: {SETTINGS.get('database.driver')}")
print(f"数据库路径: {SETTINGS.get('database.database')}")

# 获取数据库实例
db = get_database()
print(f"\n数据库实例类型: {type(db)}")
print(f"数据库实例属性: {dir(db)}")

# 检查数据库实例的实际路径
if hasattr(db, 'db_path'):
    print(f"数据库实际路径: {db.db_path}")
elif hasattr(db, 'database_path'):
    print(f"数据库实际路径: {db.database_path}")
elif hasattr(db, 'path'):
    print(f"数据库实际路径: {db.path}")
else:
    print("无法获取数据库路径属性")

# 尝试保存测试数据
from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from datetime import datetime

test_bar = BarData(
    symbol="TEST",
    exchange=Exchange.SHFE,
    datetime=datetime.now(),
    interval=Interval.DAILY,
    volume=1000,
    turnover=100000,
    open_price=100.0,
    high_price=101.0,
    low_price=99.0,
    close_price=100.5,
    gateway_name="test"
)

print("\n=== 测试保存数据 ===")
try:
    db.save_bar_data([test_bar])
    print("测试数据保存成功")
except Exception as e:
    print(f"测试数据保存失败: {e}")
    import traceback
    traceback.print_exc()

# 检查数据是否真的保存了
try:
    bars = db.load_bar_data("TEST", Exchange.SHFE, Interval.DAILY, datetime(2020, 1, 1), datetime(2030, 1, 1))
    print(f"加载到的测试数据: {len(bars)} 条")
except Exception as e:
    print(f"加载测试数据失败: {e}")