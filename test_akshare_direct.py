#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试AKShare功能
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def test_akshare_direct():
    """直接测试AKShare获取股票数据"""
    try:
        print("开始测试AKShare直接调用...")
        
        # 测试获取股票数据
        symbol = "000001"
        start_date = "20240101"
        end_date = "20240105"
        
        print(f"调用ak.stock_zh_a_hist，参数: symbol={symbol}, period=daily, start_date={start_date}, end_date={end_date}, adjust=qfq")
        
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period='daily',
            start_date=start_date,
            end_date=end_date,
            adjust='qfq'
        )
        
        print(f"返回数据类型: {type(df)}")
        print(f"返回数据量: {len(df) if df is not None else 0}")
        
        if df is not None and len(df) > 0:
            print("\n数据列名:")
            print(df.columns.tolist())
            print("\n前5行数据:")
            print(df.head())
            print("\n数据类型:")
            print(df.dtypes)
        else:
            print("未获取到数据")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_akshare_direct()