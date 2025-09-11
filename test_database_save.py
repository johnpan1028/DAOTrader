import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from data_service.akshare_client import AKShareClient
from data_service.data_converter import DataConverter
from data_service.vnpy_database import VnpyDatabaseManager

async def test_full_data_pipeline():
    """测试完整的数据流程：获取 -> 转换 -> 保存"""
    
    # 初始化组件
    akshare_client = AKShareClient()
    data_converter = DataConverter()
    # 使用内存数据库进行测试
    db_manager = VnpyDatabaseManager(db_path=":memory:")
    
    try:
        print("1. 测试数据获取...")
        df = await akshare_client.get_stock_data(
            symbol="000001",
            period="daily", 
            start_date="2024-01-01",
            end_date="2024-01-05"  # 只获取几天的数据用于测试
        )
        print(f"   获取到 {len(df)} 行数据")
        if len(df) > 0:
            print(f"   第一行数据类型: {type(df.iloc[0]['datetime'])}")
            print(f"   第一行数据: {df.iloc[0]['datetime']}")
        
        print("\n2. 测试数据转换...")
        bar_data_list = data_converter.akshare_to_vnpy_bars(
            df, 
            symbol="000001.SZ", 
            exchange="SZSE", 
            interval="daily"
        )
        print(f"   转换得到 {len(bar_data_list)} 个BarData对象")
        if bar_data_list:
            first_bar = bar_data_list[0]
            print(f"   第一个BarData的datetime类型: {type(first_bar.datetime)}")
            print(f"   第一个BarData的datetime值: {first_bar.datetime}")
        
        print("\n3. 测试数据库保存...")
        success_count = db_manager.save_bar_data(bar_data_list)
        print(f"   成功保存 {success_count} 条数据")
        
        print("\n4. 测试数据库查询...")
        from vnpy.trader.constant import Exchange, Interval
        loaded_data = db_manager.load_bar_data(
            symbol="000001.SZ",
            exchange=Exchange.SZSE,
            interval=Interval.DAILY,
            start=bar_data_list[0].datetime,
            end=bar_data_list[-1].datetime
        )
        print(f"   查询到 {len(loaded_data)} 条数据")
        if loaded_data:
            print(f"   查询结果第一条datetime类型: {type(loaded_data[0].datetime)}")
            print(f"   查询结果第一条datetime值: {loaded_data[0].datetime}")
        
        print("\n✅ 完整数据流程测试成功！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_data_pipeline())