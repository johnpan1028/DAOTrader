import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from data_service.akshare_client import AKShareClient
from data_service.data_converter import DataConverter

async def test_data_conversion():
    client = AKShareClient()
    converter = DataConverter()
    
    try:
        print("Testing AKShare to VNPY conversion...")
        
        # 获取akshare数据
        df = await client.get_stock_data(
            symbol="000001",
            period="daily", 
            start_date="2024-01-01",
            end_date="2024-01-05"
        )
        print(f"Got {len(df)} rows from AKShare")
        
        if len(df) > 0:
            print(f"AKShare columns: {list(df.columns)}")
            print(f"First AKShare row: {df.iloc[0].to_dict()}")
            
            # 转换为VNPY格式
            bars = converter.akshare_to_vnpy_bars(
                df=df,
                symbol="000001",
                exchange="sz",
                interval="daily"
            )
            
            print(f"\nConverted to {len(bars)} VNPY BarData objects")
            if len(bars) > 0:
                first_bar = bars[0]
                print(f"First VNPY bar:")
                print(f"  Symbol: {first_bar.symbol}")
                print(f"  Exchange: {first_bar.exchange}")
                print(f"  DateTime: {first_bar.datetime}")
                print(f"  Interval: {first_bar.interval}")
                print(f"  Open: {first_bar.open_price}")
                print(f"  High: {first_bar.high_price}")
                print(f"  Low: {first_bar.low_price}")
                print(f"  Close: {first_bar.close_price}")
                print(f"  Volume: {first_bar.volume}")
                print(f"  Turnover: {first_bar.turnover}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_data_conversion())