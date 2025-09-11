import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from data_service.akshare_client import AKShareClient
from data_service.data_converter import DataConverter

async def debug_datetime():
    """调试datetime类型问题"""
    client = AKShareClient()
    converter = DataConverter()
    
    try:
        print("Debugging datetime types...")
        
        # 获取akshare数据
        df = await client.get_stock_data(
            symbol="000001",
            period="daily", 
            start_date="2024-01-01",
            end_date="2024-01-02"
        )
        
        if len(df) > 0:
            print(f"\nAKShare datetime type: {type(df.iloc[0]['datetime'])}")
            print(f"AKShare datetime value: {df.iloc[0]['datetime']}")
            
            # 转换为VNPY格式
            bars = converter.akshare_to_vnpy_bars(
                df=df,
                symbol="000001",
                exchange="sz",
                interval="daily"
            )
            
            if len(bars) > 0:
                bar = bars[0]
                print(f"\nVNPY bar datetime type: {type(bar.datetime)}")
                print(f"VNPY bar datetime value: {bar.datetime}")
                print(f"VNPY bar datetime tzinfo: {bar.datetime.tzinfo}")
                
                # 测试datetime转换
                if hasattr(bar.datetime, 'to_pydatetime'):
                    py_dt = bar.datetime.to_pydatetime()
                    print(f"\nConverted datetime type: {type(py_dt)}")
                    print(f"Converted datetime value: {py_dt}")
                    print(f"Converted datetime tzinfo: {py_dt.tzinfo}")
                    
                    # 移除时区信息
                    if py_dt.tzinfo:
                        py_dt_naive = py_dt.replace(tzinfo=None)
                        print(f"\nNaive datetime type: {type(py_dt_naive)}")
                        print(f"Naive datetime value: {py_dt_naive}")
                        print(f"Naive datetime tzinfo: {py_dt_naive.tzinfo}")
                else:
                    print("\nNo to_pydatetime method available")
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_datetime())