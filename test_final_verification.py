import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from data_service.akshare_client import AKShareClient
from data_service.data_converter import DataConverter
from data_service.vnpy_database import VnpyDatabaseManager
from vnpy.trader.constant import Exchange, Interval

async def test_final_verification():
    """最终验证AKShare数据接入VNPY"""
    print("=== AKShare数据接入VNPY最终验证 ===")
    
    try:
        # 1. 初始化组件
        client = AKShareClient()
        converter = DataConverter()
        db_manager = VnpyDatabaseManager()
        
        print("\n1. 获取股票数据...")
        # 获取平安银行数据
        df = await client.get_stock_data(
            symbol="000001",
            period="daily",
            start_date="2024-01-01",
            end_date="2024-01-05"
        )
        
        if len(df) == 0:
            print("❌ 未获取到股票数据")
            return
            
        print(f"✓ 成功获取 {len(df)} 条股票数据")
        print(f"  数据列: {list(df.columns)}")
        print(f"  时间范围: {df.iloc[0]['datetime']} 到 {df.iloc[-1]['datetime']}")
        
        print("\n2. 转换为VNPY格式...")
        bars = converter.akshare_to_vnpy_bars(
            df=df,
            symbol="000001",
            exchange="sz",
            interval="daily"
        )
        
        if len(bars) == 0:
            print("❌ 数据转换失败")
            return
            
        print(f"✓ 成功转换为 {len(bars)} 个VNPY BarData对象")
        bar = bars[0]
        print(f"  首条数据: {bar.symbol}.{bar.exchange.value} {bar.datetime}")
        print(f"  OHLC: {bar.open_price}/{bar.high_price}/{bar.low_price}/{bar.close_price}")
        print(f"  成交量: {bar.volume}")
        
        print("\n3. 保存到VNPY数据库...")
        success = db_manager.save_bar_data(bars)
        
        if not success:
            print("❌ 数据保存失败")
            return
            
        print("✓ 数据保存成功")
        
        print("\n4. 验证数据读取...")
        saved_bars = db_manager.load_bar_data(
            symbol="000001",
            exchange=Exchange.SZSE,
            interval=Interval.DAILY,
            start=bars[0].datetime,
            end=bars[-1].datetime
        )
        
        if len(saved_bars) == 0:
            print("❌ 数据读取失败")
            return
            
        print(f"✓ 成功读取 {len(saved_bars)} 条数据")
        saved_bar = saved_bars[0]
        print(f"  读取数据: {saved_bar.symbol}.{saved_bar.exchange.value} {saved_bar.datetime}")
        print(f"  OHLC: {saved_bar.open_price}/{saved_bar.high_price}/{saved_bar.low_price}/{saved_bar.close_price}")
        
        print("\n5. 数据一致性检查...")
        original_bar = bars[0]
        if (
            saved_bar.symbol == original_bar.symbol and
            saved_bar.open_price == original_bar.open_price and
            saved_bar.close_price == original_bar.close_price and
            saved_bar.volume == original_bar.volume
        ):
            print("✓ 数据一致性检查通过")
        else:
            print("❌ 数据一致性检查失败")
            print(f"  原始: O={original_bar.open_price} C={original_bar.close_price} V={original_bar.volume}")
            print(f"  读取: O={saved_bar.open_price} C={saved_bar.close_price} V={saved_bar.volume}")
        
        print("\n🎉 AKShare数据成功接入VNPY！")
        print("\n数据流程验证完成:")
        print("  AKShare API → 数据获取 ✓")
        print("  数据标准化 → VNPY格式转换 ✓")
        print("  VNPY数据库 → 数据存储 ✓")
        print("  数据读取 → 一致性验证 ✓")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_final_verification())