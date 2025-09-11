import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from data_service.akshare_client import AKShareClient
from data_service.data_converter import DataConverter
from data_service.vnpy_database import VnpyDatabaseManager

async def test_full_pipeline():
    """测试完整的数据流水线：AKShare -> 转换 -> VNPY数据库"""
    client = AKShareClient()
    converter = DataConverter()
    db_manager = VnpyDatabaseManager()
    
    try:
        print("Testing full data pipeline: AKShare -> Converter -> VNPY Database...")
        
        # 1. 获取akshare数据
        print("\n1. Fetching data from AKShare...")
        df = await client.get_stock_data(
            symbol="000001",
            period="daily", 
            start_date="2024-01-01",
            end_date="2024-01-03"
        )
        print(f"Got {len(df)} rows from AKShare")
        
        if len(df) == 0:
            print("No data received from AKShare")
            return
            
        # 2. 转换为VNPY格式
        print("\n2. Converting to VNPY format...")
        bars = converter.akshare_to_vnpy_bars(
            df=df,
            symbol="000001",
            exchange="sz",
            interval="daily"
        )
        print(f"Converted to {len(bars)} VNPY BarData objects")
        
        if len(bars) == 0:
            print("No bars converted")
            return
            
        # 3. 保存到VNPY数据库
        print("\n3. Saving to VNPY database...")
        success = db_manager.save_bar_data(bars)
        print(f"Save operation {'successful' if success else 'failed'}")
        
        if not success:
            print("❌ Failed to save data to database")
            return
        
        # 4. 验证数据是否保存成功
        print("\n4. Verifying saved data...")
        if hasattr(db_manager, 'database') and db_manager.database:
            # 使用VNPY数据库查询
            from datetime import datetime
            from vnpy.trader.constant import Exchange, Interval
            
            saved_bars = db_manager.database.load_bar_data(
                symbol="000001",
                exchange=Exchange.SZSE,
                interval=Interval.DAILY,
                start=datetime(2024, 1, 1),
                end=datetime(2024, 1, 3)
            )
            print(f"Retrieved {len(saved_bars)} bars from database")
            
            if len(saved_bars) > 0:
                first_saved = saved_bars[0]
                print(f"First saved bar:")
                print(f"  Symbol: {first_saved.symbol}")
                print(f"  Exchange: {first_saved.exchange}")
                print(f"  DateTime: {first_saved.datetime}")
                print(f"  Open: {first_saved.open_price}")
                print(f"  Close: {first_saved.close_price}")
                print(f"  Volume: {first_saved.volume}")
        else:
            print("Database not available for verification")
            
        print("\n✅ Full pipeline test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())